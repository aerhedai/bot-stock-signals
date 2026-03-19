"""
AI service using Gemini via Vertex AI.

Provides two main interfaces:
- generate(): one-shot text generation (news analysis, summaries, etc.)
- run_agent(): multi-turn agentic loop with function calling tools

Uses the google-genai SDK (google.genai), the unified replacement for the
deprecated vertexai.generative_models API.

Authentication is handled via the GOOGLE_APPLICATION_CREDENTIALS env var,
which should point to a service account JSON key file.
"""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional

from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)

# Shared prompt templates used across features
PROMPT_TEMPLATES = {
    "market_analysis_stocks": (
        "You are a financial analyst. Based on the following recent stock market news headlines, "
        "write a detailed paragraph (5-7 sentences) summarising the current state of the stock market. "
        "Cover the key themes, affected sectors, overall sentiment, and any notable risks or opportunities. "
        "Do not make specific price predictions.\n\nHeadlines:\n{headlines}"
    ),
    "market_analysis_crypto": (
        "You are a crypto analyst. Based on the following recent crypto news headlines, "
        "write a detailed paragraph (5-7 sentences) summarising the current state of the crypto market. "
        "Cover dominant narratives, sentiment, major assets mentioned, and any notable risks or opportunities. "
        "Do not make specific price predictions.\n\nHeadlines:\n{headlines}"
    ),
}


@dataclass
class AgentTool:
    """Wraps a callable tool that the agent can invoke during a multi-turn session."""

    name: str
    description: str
    parameters: dict  # JSON Schema for the function parameters
    handler: Callable[..., Any]

    def to_function_declaration(self) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )


class AIService:
    """
    Central LLM integration point for the application.

    Initialised once on startup; all features should use the singleton
    returned by get_ai_service() rather than constructing their own instance.
    """

    def __init__(self):
        self._client: Optional[genai.Client] = None

    def _ensure_init(self):
        if self._client is not None:
            return
        if not settings.vertex_project:
            raise RuntimeError(
                "VERTEX_PROJECT is not set. Add it to your .env file."
            )
        self._client = genai.Client(
            vertexai=True,
            project=settings.vertex_project,
            location=settings.vertex_location,
        )
        logger.info(
            "Vertex AI client initialised (project=%s, location=%s, model=%s)",
            settings.vertex_project,
            settings.vertex_location,
            settings.vertex_model,
        )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.4,
        max_tokens: int = 1024,
    ) -> str:
        """
        One-shot text generation. Returns the model's response as a string.

        Args:
            prompt: The full prompt to send.
            temperature: Sampling temperature (lower = more deterministic).
            max_tokens: Maximum tokens in the response.
        """
        self._ensure_init()
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
        try:
            response = await self._client.aio.models.generate_content(
                model=settings.vertex_model,
                contents=prompt,
                config=config,
            )
            return response.text.strip()
        except Exception:
            logger.exception("generate() failed")
            raise

    async def run_agent(
        self,
        query: str,
        tools: list[AgentTool],
        temperature: float = 0.2,
        max_turns: int = 6,
    ) -> str:
        """
        Multi-turn agentic loop with function calling.

        The model may call any of the provided tools zero or more times.
        Tool handlers are called synchronously inside the loop.
        Returns the final text response once the model stops issuing function calls.

        Args:
            query: Initial user query / task description.
            tools: List of AgentTool instances the model can call.
            temperature: Sampling temperature.
            max_turns: Maximum number of model turns before giving up.
        """
        self._ensure_init()

        tool_map = {t.name: t.handler for t in tools}
        vertex_tool = types.Tool(
            function_declarations=[t.to_function_declaration() for t in tools]
        )
        config = types.GenerateContentConfig(
            tools=[vertex_tool],
            temperature=temperature,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        chat = self._client.aio.chats.create(
            model=settings.vertex_model,
            config=config,
        )

        message = query

        for turn in range(max_turns):
            response = await chat.send_message(message)
            candidate = response.candidates[0]

            # Check if the model wants to call a function
            function_calls = [
                part.function_call
                for part in candidate.content.parts
                if part.function_call and part.function_call.name
            ]

            if not function_calls:
                # No more tool calls — return the final text
                text_parts = [
                    p.text for p in candidate.content.parts if p.text
                ]
                return " ".join(text_parts).strip()

            # Execute each requested function and collect results
            function_responses = []
            for fc in function_calls:
                handler = tool_map.get(fc.name)
                if handler is None:
                    result = {"error": f"Unknown tool: {fc.name}"}
                else:
                    try:
                        result = handler(**dict(fc.args))
                        if not isinstance(result, dict):
                            result = {"result": result}
                    except Exception as e:
                        logger.warning("Tool %s raised: %s", fc.name, e)
                        result = {"error": str(e)}

                function_responses.append(
                    types.Part.from_function_response(
                        name=fc.name, response=result
                    )
                )

            message = function_responses

        logger.warning("run_agent() hit max_turns=%d without a final text response", max_turns)
        return ""


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_instance: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Return the shared AIService instance, creating it on first call."""
    global _instance
    if _instance is None:
        _instance = AIService()
    return _instance
