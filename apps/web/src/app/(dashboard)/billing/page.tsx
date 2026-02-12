"use client";

import { CreditCard, Check, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/ui/error-state";
import { UsageBadge } from "@/components/ui/usage-badge";
import {
  useSubscription,
  useUsage,
  useCreateCheckout,
  useCreatePortal,
} from "@/hooks/use-subscription";
import { formatDate } from "@/lib/format";

const PRO_FEATURES = [
  "Unlimited portfolios & holdings",
  "Unlimited AI Earnings Analysis",
  "Unlimited AI Portfolio Analysis",
  "Stock Comparison",
  "Price Forecasting",
  "News Sentiment Scores",
  "CSV Export",
  "Priority AI Processing",
];

export default function BillingPage() {
  const {
    data: subscription,
    isPending,
    isError,
    error,
    refetch,
  } = useSubscription();
  const { data: usage } = useUsage();
  const checkout = useCreateCheckout();
  const portal = useCreatePortal();

  if (isPending) {
    return (
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Billing</h2>
        <div className="mt-6 space-y-4">
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-60 w-full" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Billing</h2>
        <div className="mt-6">
          <ErrorState message={error.message} onRetry={() => refetch()} />
        </div>
      </div>
    );
  }

  const isPro = subscription?.plan === "pro";

  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight">Billing</h2>
      <p className="mt-2 text-muted-foreground">
        Manage your subscription and view usage.
      </p>

      {/* Current Plan Card */}
      <Card className="mt-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Current Plan</CardTitle>
            <Badge variant={isPro ? "default" : "secondary"}>
              {isPro ? "Pro" : "Free"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {isPro ? (
            <>
              <p className="text-sm text-muted-foreground">
                You have access to all Pro features.
                {subscription?.cancel_at_period_end && (
                  <span className="text-destructive">
                    {" "}
                    Your plan will be downgraded at the end of the billing
                    period.
                  </span>
                )}
              </p>
              {subscription?.current_period_end && (
                <p className="text-sm text-muted-foreground">
                  Next billing date:{" "}
                  {formatDate(subscription.current_period_end)}
                </p>
              )}
              <Button
                variant="outline"
                onClick={() => portal.mutate()}
                disabled={portal.isPending}
              >
                <CreditCard className="mr-2 h-4 w-4" />
                {portal.isPending ? "Redirecting..." : "Manage Subscription"}
              </Button>
            </>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">
                You are on the Free plan with limited features.
              </p>
              <Button
                onClick={() => checkout.mutate()}
                disabled={checkout.isPending}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {checkout.isPending
                  ? "Redirecting..."
                  : "Upgrade to Pro — $9.99/mo"}
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      {/* Usage Card */}
      {usage && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle className="text-base">Monthly Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <UsageBadge
                used={usage.earnings_analysis_used}
                limit={usage.earnings_analysis_limit}
                label="Earnings Analyses"
              />
              <UsageBadge
                used={usage.portfolio_analysis_used}
                limit={usage.portfolio_analysis_limit}
                label="Portfolio Analyses"
              />
              <UsageBadge
                used={usage.portfolio_count}
                limit={usage.portfolio_limit}
                label="Portfolios"
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pro Features List */}
      {!isPro && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle className="text-base">Pro Features</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {PRO_FEATURES.map((feature) => (
                <li key={feature} className="flex items-center gap-2 text-sm">
                  <Check className="h-4 w-4 text-primary" />
                  {feature}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
