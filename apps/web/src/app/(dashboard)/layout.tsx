import { DashboardShell } from "@/components/layout/dashboard-shell";

// All dashboard pages require auth and client-side hooks (Clerk, React Query).
// Prevent static prerendering to avoid Clerk context errors at build time.
export const dynamic = "force-dynamic";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardShell>{children}</DashboardShell>;
}
