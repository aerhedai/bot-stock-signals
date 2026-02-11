"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface Tab {
  href: string;
  label: string;
}

interface Props {
  tabs: Tab[];
}

export default function TabBar({ tabs }: Props) {
  const pathname = usePathname();

  return (
    <div className="flex gap-1 border-b border-border-primary mb-6">
      {tabs.map((tab) => {
        const active = pathname === tab.href;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`px-3 py-2 text-sm transition-colors relative ${
              active
                ? "text-text-primary"
                : "text-text-muted hover:text-text-secondary"
            }`}
          >
            {tab.label}
            {active && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent" />
            )}
          </Link>
        );
      })}
    </div>
  );
}
