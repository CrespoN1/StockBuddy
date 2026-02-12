"use client";

import { Lock, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useCreateCheckout } from "@/hooks/use-subscription";

interface UpgradePromptProps {
  feature: string;
  description?: string;
}

export function UpgradePrompt({ feature, description }: UpgradePromptProps) {
  const checkout = useCreateCheckout();

  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-center justify-center py-8 text-center">
        <Lock className="h-8 w-8 text-muted-foreground" />
        <h3 className="mt-3 text-lg font-semibold">{feature}</h3>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          {description || "This feature requires a Pro subscription."}
        </p>
        <Button
          className="mt-4"
          onClick={() => checkout.mutate()}
          disabled={checkout.isPending}
        >
          <Sparkles className="mr-2 h-4 w-4" />
          {checkout.isPending ? "Redirecting..." : "Upgrade to Pro — $9.99/mo"}
        </Button>
      </CardContent>
    </Card>
  );
}
