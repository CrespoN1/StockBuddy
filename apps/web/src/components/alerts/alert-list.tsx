"use client";

import { Trash2, Bell, BellRing } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useAlerts, useDeleteAlert } from "@/hooks/use-alerts";
import { formatCurrency, formatDate } from "@/lib/format";

export function AlertList() {
  const { data: alerts, isPending } = useAlerts();
  const deleteAlert = useDeleteAlert();

  if (isPending) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <EmptyState
        icon={<Bell className="h-10 w-10" />}
        title="No price alerts"
        description="Create an alert above to get notified when a stock reaches your target price."
      />
    );
  }

  const active = alerts.filter((a) => !a.triggered);
  const triggered = alerts.filter((a) => a.triggered);

  function handleDelete(id: number) {
    deleteAlert.mutate(id, {
      onSuccess: () => toast.success("Alert deleted"),
      onError: (err) => toast.error(err.message),
    });
  }

  return (
    <div className="space-y-6">
      {active.length > 0 && (
        <div>
          <h3 className="mb-3 text-sm font-medium text-muted-foreground">
            Active Alerts ({active.length})
          </h3>
          <div className="space-y-2">
            {active.map((a) => (
              <Card key={a.id}>
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <Bell className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <span className="font-medium">{a.ticker}</span>
                      <span className="ml-2 text-sm text-muted-foreground">
                        {a.direction === "above" ? ">" : "<"}{" "}
                        {formatCurrency(a.target_price)}
                      </span>
                    </div>
                    <Badge variant="secondary">{a.direction}</Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(a.id)}
                    disabled={deleteAlert.isPending}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {triggered.length > 0 && (
        <div>
          <h3 className="mb-3 text-sm font-medium text-muted-foreground">
            Triggered ({triggered.length})
          </h3>
          <div className="space-y-2">
            {triggered.map((a) => (
              <Card key={a.id} className="border-green-200 dark:border-green-900">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <BellRing className="h-4 w-4 text-green-600" />
                    <div>
                      <span className="font-medium">{a.ticker}</span>
                      <span className="ml-2 text-sm text-muted-foreground">
                        hit {formatCurrency(a.target_price)} (was{" "}
                        {a.triggered_price != null
                          ? formatCurrency(a.triggered_price)
                          : "--"}
                        )
                      </span>
                    </div>
                    <Badge variant="default">triggered</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    {a.triggered_at && (
                      <span className="text-xs text-muted-foreground">
                        {formatDate(a.triggered_at)}
                      </span>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(a.id)}
                      disabled={deleteAlert.isPending}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
