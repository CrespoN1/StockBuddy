"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu } from "lucide-react";
import { UserButton } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Sidebar, SidebarNav } from "@/components/layout/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-14 items-center justify-between border-b bg-background px-4 md:px-6">
          <div className="flex items-center gap-3">
            {/* Mobile hamburger */}
            <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-56 p-0">
                <SheetHeader className="border-b px-4 py-4">
                  <SheetTitle>
                    <Link
                      href="/dashboard"
                      className="text-xl font-bold text-primary"
                      onClick={() => setMobileOpen(false)}
                    >
                      StockBuddy
                    </Link>
                  </SheetTitle>
                </SheetHeader>
                <SidebarNav onNavigate={() => setMobileOpen(false)} />
              </SheetContent>
            </Sheet>
            <h1 className="text-lg font-semibold">StockBuddy</h1>
          </div>
          <UserButton />
        </header>
        <main className="flex-1 overflow-y-auto p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
