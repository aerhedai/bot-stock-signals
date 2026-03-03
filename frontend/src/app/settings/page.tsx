"use client";

import { useApi } from "@/hooks/useApi";
import { getHealth } from "@/lib/api";
import { formatDate } from "@/lib/format";

export default function SettingsPage() {
  const health = useApi(getHealth);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Backend Connection</h2>
        <div className="border border-gray-700 rounded-lg p-4 bg-gray-900">
          {health.loading && (
            <p className="text-gray-400 text-sm">Checking connection...</p>
          )}
          {health.error && (
            <p className="text-red-400 text-sm">
              Backend unreachable: {health.error}
            </p>
          )}
          {health.data && (
            <div className="text-sm space-y-1">
              <p>
                <span className="text-gray-400">Status:</span>{" "}
                <span className="text-green-400">{health.data.status}</span>
              </p>
              <p>
                <span className="text-gray-400">Timestamp:</span>{" "}
                {formatDate(health.data.timestamp)}
              </p>
            </div>
          )}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Configuration</h2>
        <p className="text-sm text-gray-400">
          Configuration is managed via environment variables in the root .env
          file. See .env.example for available options.
        </p>
      </section>
    </div>
  );
}
