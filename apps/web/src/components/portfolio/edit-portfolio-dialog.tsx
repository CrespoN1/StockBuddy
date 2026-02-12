"use client";

import { useState, useEffect } from "react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useUpdatePortfolio } from "@/hooks/use-portfolios";
import type { PortfolioRead } from "@/types";

interface EditPortfolioDialogProps {
  portfolio: PortfolioRead | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EditPortfolioDialog({
  portfolio,
  open,
  onOpenChange,
}: EditPortfolioDialogProps) {
  const [name, setName] = useState("");
  const updatePortfolio = useUpdatePortfolio();

  useEffect(() => {
    if (portfolio) setName(portfolio.name);
  }, [portfolio]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!portfolio || !name.trim()) return;
    updatePortfolio.mutate(
      { id: portfolio.id, data: { name: name.trim() } },
      {
        onSuccess: () => {
          toast.success("Portfolio updated");
          onOpenChange(false);
        },
        onError: (err) => {
          toast.error(err.message);
        },
      }
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Portfolio</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="py-4">
            <Input
              placeholder="Portfolio name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!name.trim() || updatePortfolio.isPending}
            >
              {updatePortfolio.isPending ? "Saving..." : "Save"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
