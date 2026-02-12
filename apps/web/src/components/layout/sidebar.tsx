"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  Search,
  BarChart3,
  GitCompareArrows,
} from "lucide-react";
import { cn } from "@/lib/utils";

export const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/portfolios", label: "Portfolios", icon: Briefcase },
  { href: "/dashboard/stocks", label: "Stocks", icon: Search },
  { href: "/dashboard/earnings", label: "Earnings", icon: BarChart3 },
  { href: "/dashboard/compare", label: "Compare", icon: GitCompareArrows },
];

interface SidebarNavProps {
  onNavigate?: () => void;
}

export function SidebarNav({ onNavigate }: SidebarNavProps) {
  const pathname = usePathname();

  return (
    <nav className="space-y-1 p-3">
      {navItems.map((item) => {
        const isActive =
          item.href === "/dashboard"
            ? pathname === "/dashboard"
            : pathname === item.href || pathname.startsWith(item.href + "/");
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              isActive
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden w-56 border-r bg-background md:block">
      <div className="flex h-14 items-center border-b px-4">
        <Link href="/dashboard" className="text-xl font-bold text-primary">
          StockBuddy
        </Link>
      </div>
      <SidebarNav />
    </aside>
  );
}
