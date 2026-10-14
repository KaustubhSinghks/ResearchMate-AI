"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Upload,
  FileText,
  Search,
  StickyNote,
  GitCompare,
  Network,
  BookOpen,
  LogOut,
  Sparkles,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import ThemeToggle from "./ThemeToggle";

const LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/search", label: "Search", icon: Search },
  { href: "/notes", label: "Notes", icon: StickyNote },
  { href: "/compare", label: "Compare", icon: GitCompare },
  { href: "/graph", label: "Knowledge Graph", icon: Network },
  { href: "/review", label: "Literature Review", icon: BookOpen },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="glass sticky top-0 flex h-screen w-64 flex-col justify-between rounded-none border-y-0 border-l-0 px-4 py-6">
      <div>
        <div className="mb-8 flex items-center gap-2 px-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-gradient shadow-lg shadow-brand-500/30">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <span className="text-base font-semibold tracking-tight text-ink">Research AI</span>
        </div>

        <nav className="flex flex-col gap-1">
          {LINKS.map((link) => {
            const active = pathname === link.href || pathname.startsWith(`${link.href}/`);
            const Icon = link.icon;
            return (
              <Link key={link.href} href={link.href} className="relative">
                {active && (
                  <motion.div
                    layoutId="sidebar-active-pill"
                    className="absolute inset-0 rounded-xl bg-brand-gradient shadow-md shadow-brand-500/25"
                    transition={{ type: "spring", stiffness: 400, damping: 32 }}
                  />
                )}
                <span
                  className={`relative flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors duration-150 ${
                    active ? "text-white" : "text-ink-muted hover:bg-surface-raised hover:text-ink"
                  }`}
                >
                  <Icon className="h-4 w-4 shrink-0" strokeWidth={2} />
                  {link.label}
                </span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="border-t border-border pt-4">
        <div className="mb-3 flex items-center justify-between px-2">
          <span className="truncate text-xs text-ink-faint">{user?.email}</span>
          <ThemeToggle />
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-ink-muted transition-colors duration-150 hover:bg-surface-raised hover:text-ink"
        >
          <LogOut className="h-4 w-4" strokeWidth={2} />
          Log out
        </button>
      </div>
    </aside>
  );
}
