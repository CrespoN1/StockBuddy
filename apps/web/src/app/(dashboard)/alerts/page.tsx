"use client";

import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CreateAlertForm } from "@/components/alerts/create-alert-form";
import { AlertList } from "@/components/alerts/alert-list";

export default function AlertsPage() {
  const searchParams = useSearchParams();
  const ticker = searchParams.get("ticker") ?? undefined;

  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight">Price Alerts</h2>
      <p className="mt-2 text-muted-foreground">
        Set target prices for stocks and get notified when they hit your levels.
      </p>

      <div className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Create Alert</CardTitle>
          </CardHeader>
          <CardContent>
            <CreateAlertForm defaultTicker={ticker} />
          </CardContent>
        </Card>
      </div>

      <div className="mt-6">
        <AlertList />
      </div>
    </div>
  );
}
