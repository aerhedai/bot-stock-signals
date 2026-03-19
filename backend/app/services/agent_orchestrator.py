"""
Central AI agent orchestrator.

All features that need agentic behaviour register their tools here
and call run_task() rather than invoking AIService.run_agent() directly.

This gives a single place to:
- Track AI API usage (prevent runaway costs)
- Enforce staleness guards (skip if result is still fresh)
- Log all agentic activity across the system
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from app.services.ai_service import AgentTool, get_ai_service

logger = logging.getLogger(__name__)

# Hard limit: max agent calls per hour across the whole system.
# Prevents runaway costs if a bug triggers rapid retries.
_MAX_CALLS_PER_HOUR = 20


class AgentOrchestrator:
    def __init__(self):
        self._tools: dict[str, AgentTool] = {}
        self._call_log: list[datetime] = []  # rolling window for rate limiting

    def register_tool(self, tool: AgentTool) -> None:
        """Register a tool so the agent can call it."""
        self._tools[tool.name] = tool
        logger.debug("Registered agent tool: %s", tool.name)

    def register_tools(self, tools: list[AgentTool]) -> None:
        for tool in tools:
            self.register_tool(tool)

    def _check_rate_limit(self) -> bool:
        """Return True if within limit, False if over budget."""
        now = datetime.now()
        cutoff = now - timedelta(hours=1)
        self._call_log = [t for t in self._call_log if t > cutoff]
        if len(self._call_log) >= _MAX_CALLS_PER_HOUR:
            logger.warning(
                "Agent rate limit reached (%d calls in last hour)", len(self._call_log)
            )
            return False
        return True

    async def run_task(
        self,
        task: str,
        tool_names: Optional[list[str]] = None,
        temperature: float = 0.2,
        max_turns: int = 8,
    ) -> str:
        """
        Run an agentic task.

        Args:
            task:        Natural language description of what the agent should do.
            tool_names:  Subset of registered tools to expose to the agent.
                         If None, all registered tools are available.
            temperature: Sampling temperature (default 0.2 for consistent reasoning).
            max_turns:   Max agent turns before giving up.

        Returns:
            The agent's final text response.
        """
        if not self._check_rate_limit():
            return "Skipped: agent rate limit reached. Try again later."

        if tool_names is not None:
            tools = [self._tools[n] for n in tool_names if n in self._tools]
        else:
            tools = list(self._tools.values())

        if not tools:
            logger.warning("run_task called with no available tools")
            return "No tools available for this task."

        self._call_log.append(datetime.now())
        logger.info("Agent task started (tools: %s)", [t.name for t in tools])

        result = await get_ai_service().run_agent(
            task, tools, temperature=temperature, max_turns=max_turns
        )
        logger.info("Agent task complete")
        return result


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Return the shared AgentOrchestrator instance, creating it on first call."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
