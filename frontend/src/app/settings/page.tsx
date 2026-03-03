"use client";

import { useApi } from "@/hooks/useApi";
import { getHealth, getStatus } from "@/lib/api";
import { formatDate } from "@/lib/format";
import PageHeader from "@/components/layout/PageHeader";
import StatusBadge from "@/components/ui/StatusBadge";
import LoadingSkeleton from "@/components/ui/LoadingSkeleton";

export default function SettingsPage() {
  const health = useApi(getHealth);
  const status = useApi(getStatus);

  return (
    <div>
      <PageHeader title="Settings" />

      {/* Backend Connection */}
      <section className="mb-8">
        <p className="text-[11px] font-medium uppercase tracking-wider text-text-muted mb-3">
          Backend Connection
        </p>
        <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
          {health.loading && <LoadingSkeleton lines={2} />}
          {health.error && (
            <div className="flex items-center gap-2">
              <StatusBadge status="error" />
              <p className="text-sm text-semantic-error">
                Backend unreachable: {health.error}
              </p>
            </div>
          )}
          {health.data && (
            <div className="text-sm space-y-1.5">
              <div className="flex items-center gap-2">
                <StatusBadge status="running" />
                <span className="text-text-primary">{health.data.status}</span>
              </div>
              <p>
                <span className="text-text-muted">Timestamp:</span>{" "}
                <span className="text-text-secondary">{formatDate(health.data.timestamp)}</span>
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Service Overview */}
      <section className="mb-8">
        <p className="text-[11px] font-medium uppercase tracking-wider text-text-muted mb-3">
          Services
        </p>
        {status.loading && <LoadingSkeleton lines={4} />}
        {status.error && (
          <p className="text-sm text-semantic-error">{status.error}</p>
        )}
        {status.data && (
          <div className="space-y-2">
            {status.data.services.map((service) => (
              <div
                key={service.name}
                className="border border-border-primary rounded-xl p-4 bg-surface-card flex items-center justify-between"
              >
                <div>
                  <h3 className="text-sm font-medium capitalize">
                    {service.name.replace("_", " ")}
                  </h3>
                  <p className="text-xs text-text-muted mt-0.5">
                    {service.total_runs} runs &middot; Last: {formatDate(service.last_run)}
                  </p>
                </div>
                <StatusBadge status={service.running ? "running" : "stopped"} />
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Configuration */}
      <section>
        <p className="text-[11px] font-medium uppercase tracking-wider text-text-muted mb-3">
          Configuration
        </p>
        <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
          <p className="text-sm text-text-secondary">
            Configuration is managed via environment variables in the root .env
            file. See .env.example for available options.
          </p>
        </div>
      </section>
    </div>
  );
}
