"use client";

import { useState } from "react";
import { Plus, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { PortfolioCard } from "@/components/portfolio/portfolio-card";
import { CreatePortfolioDialog } from "@/components/portfolio/create-portfolio-dialog";
import { EditPortfolioDialog } from "@/components/portfolio/edit-portfolio-dialog";
import { DeletePortfolioDialog } from "@/components/portfolio/delete-portfolio-dialog";
import { usePortfolios } from "@/hooks/use-portfolios";
import { useUsage } from "@/hooks/use-subscription";
import type { PortfolioRead } from "@/types";

export default function PortfoliosPage() {
  const { data: portfolios, isPending, isError, error, refetch } = usePortfolios();
  const { data: usage } = useUsage();
  const [createOpen, setCreateOpen] = useState(false);
  const [editPortfolio, setEditPortfolio] = useState<PortfolioRead | null>(null);
  const [deletePortfolio, setDeletePortfolio] = useState<PortfolioRead | null>(null);

  if (isPending) {
    return (
      <div>
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight">Portfolios</h2>
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="mt-3 h-4 w-24" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Portfolios</h2>
        <div className="mt-6">
          <ErrorState message={error.message} onRetry={() => refetch()} />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Portfolios</h2>
        <div className="flex flex-col items-end gap-1">
          <Button
            onClick={() => setCreateOpen(true)}
            disabled={usage !== undefined && !usage.can_create_portfolio}
          >
            <Plus className="mr-2 h-4 w-4" />
            New Portfolio
          </Button>
          {usage && !usage.can_create_portfolio && (
            <p className="text-xs text-muted-foreground">
              Free plan allows 1 portfolio.{" "}
              <a href="/billing" className="text-primary underline">Upgrade to Pro</a>
            </p>
          )}
        </div>
      </div>

      {portfolios && portfolios.length > 0 ? (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {portfolios.map((p) => (
            <PortfolioCard
              key={p.id}
              portfolio={p}
              onEdit={setEditPortfolio}
              onDelete={setDeletePortfolio}
            />
          ))}
        </div>
      ) : (
        <div className="mt-6">
          <EmptyState
            icon={<Briefcase className="h-12 w-12" />}
            title="No portfolios yet"
            description="Create your first portfolio to start tracking your investments."
            action={
              <Button onClick={() => setCreateOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Create Portfolio
              </Button>
            }
          />
        </div>
      )}

      <CreatePortfolioDialog open={createOpen} onOpenChange={setCreateOpen} />
      <EditPortfolioDialog
        portfolio={editPortfolio}
        open={!!editPortfolio}
        onOpenChange={(open) => !open && setEditPortfolio(null)}
      />
      <DeletePortfolioDialog
        portfolio={deletePortfolio}
        open={!!deletePortfolio}
        onOpenChange={(open) => !open && setDeletePortfolio(null)}
      />
    </div>
  );
}
