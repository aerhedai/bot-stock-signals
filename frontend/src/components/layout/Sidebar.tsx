"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/stocks", label: "Stocks" },
  { href: "/crypto", label: "Crypto" },
  { href: "/news", label: "News" },
  { href: "/settings", label: "Settings" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 shrink-0 border-r border-gray-800 bg-gray-950 p-4 flex flex-col gap-1">
      <h1 className="text-lg font-bold mb-6 px-3">Signal Bot</h1>
      {links.map((link) => {
        const active = pathname === link.href;
        return (
          <Link
            key={link.href}
            href={link.href}
            className={`px-3 py-2 rounded text-sm ${
              active
                ? "bg-blue-600 text-white"
                : "text-gray-400 hover:bg-gray-800 hover:text-white"
            }`}
          >
            {link.label}
          </Link>
        );
      })}
    </aside>
  );
}
