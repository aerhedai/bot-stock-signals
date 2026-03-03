"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useApi } from "@/hooks/useApi";
import { getHealth } from "@/lib/api";
import {
  LayoutDashboard,
  TrendingUp,
  Newspaper,
  Settings,
  Circle,
  BrainCircuit,
} from "@/components/icons";

const sections = [
  {
    label: "OVERVIEW",
    links: [
      { href: "/", icon: LayoutDashboard, label: "Dashboard" },
    ],
  },
  {
    label: "ANALYSIS",
    links: [
      { href: "/predictions", icon: TrendingUp, label: "Predictions" },
      { href: "/news", icon: Newspaper, label: "News" },
      { href: "/analysis", icon: BrainCircuit, label: "AI Analysis" },
    ],
  },
  {
    label: "SYSTEM",
    links: [
      { href: "/settings", icon: Settings, label: "Settings" },
    ],
  },
];

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname.startsWith(href);
}

export default function AppSidebar() {
  const pathname = usePathname();
  const health = useApi(getHealth);

  const connected = !!health.data && !health.error;

  return (
    <aside className="w-60 shrink-0 border-r border-border-primary bg-surface-root flex flex-col">
      {/* Brand */}
      <div className="px-5 py-5">
        <h1 className="text-sm font-semibold text-text-primary tracking-tight">
          Signal Bot
        </h1>
      </div>

      <div className="h-px bg-border-primary" />

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-5">
        {sections.map((section) => (
          <div key={section.label}>
            <p className="px-2 mb-1.5 text-[11px] font-medium uppercase tracking-wider text-text-muted">
              {section.label}
            </p>
            <div className="space-y-0.5">
              {section.links.map((link) => {
                const active = isActive(pathname, link.href);
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`flex items-center gap-2.5 px-2 py-1.5 rounded-lg text-sm transition-colors ${
                      active
                        ? "bg-accent/10 text-accent"
                        : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
                    }`}
                  >
                    <link.icon className="w-4 h-4" />
                    {link.label}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Health indicator */}
      <div className="h-px bg-border-primary" />
      <div className="px-5 py-3 flex items-center gap-2">
        <Circle
          className={`w-2 h-2 ${connected ? "text-semantic-success" : "text-text-muted"}`}
        />
        <span className="text-xs text-text-muted">
          {health.loading
            ? "Connecting..."
            : connected
              ? "Backend Connected"
              : "Backend Offline"}
        </span>
      </div>
    </aside>
  );
}
