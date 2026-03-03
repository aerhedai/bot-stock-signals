"use client";

import { useApi } from "@/hooks/useApi";
import { getStatus } from "@/lib/api";
import { formatDate } from "@/lib/format";

export default function Dashboard() {
  const { data, loading, error } = useApi(getStatus);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      {loading && <p className="text-gray-400">Loading status...</p>}
      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded p-4 mb-4">
          <p className="text-red-400">Failed to connect to backend: {error}</p>
          <p className="text-sm text-gray-400 mt-1">
            Make sure the backend is running on port 8000.
          </p>
        </div>
      )}

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data.services.map((service) => (
            <div
              key={service.name}
              className="border border-gray-700 rounded-lg p-4 bg-gray-900"
            >
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-medium capitalize">
                  {service.name.replace("_", " ")}
                </h3>
                <span
                  className={`text-xs px-2 py-1 rounded ${
                    service.running
                      ? "bg-green-900 text-green-400"
                      : "bg-gray-800 text-gray-400"
                  }`}
                >
                  {service.running ? "Running" : "Stopped"}
                </span>
              </div>
              <div className="text-sm text-gray-400 space-y-1">
                <p>Total runs: {service.total_runs}</p>
                <p>
                  Last run: {formatDate(service.last_run)}
                </p>
                <p>
                  Next run: {formatDate(service.next_run)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
