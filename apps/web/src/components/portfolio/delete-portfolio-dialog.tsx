"use client";

import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useDeletePortfolio } from "@/hooks/use-portfolios";
import type { PortfolioRead } from "@/types";

interface DeletePortfolioDialogProps {
  portfolio: PortfolioRead | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DeletePortfolioDialog({
  portfolio,
  open,
  onOpenChange,
}: DeletePortfolioDialogProps) {
  const deletePortfolio = useDeletePortfolio();

  function handleDelete() {
    if (!portfolio) return;
    deletePortfolio.mutate(portfolio.id, {
      onSuccess: () => {
        toast.success("Portfolio deleted");
        onOpenChange(false);
      },
      onError: (err) => {
        toast.error(err.message);
      },
    });
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Portfolio</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete &quot;{portfolio?.name}&quot;? This
            action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deletePortfolio.isPending}
          >
            {deletePortfolio.isPending ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
