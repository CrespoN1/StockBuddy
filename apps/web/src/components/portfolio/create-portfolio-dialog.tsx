"use client";

import { useState } from "react";
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
import { useCreatePortfolio } from "@/hooks/use-portfolios";

interface CreatePortfolioDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreatePortfolioDialog({
  open,
  onOpenChange,
}: CreatePortfolioDialogProps) {
  const [name, setName] = useState("");
  const createPortfolio = useCreatePortfolio();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    createPortfolio.mutate(
      { name: name.trim() },
      {
        onSuccess: () => {
          toast.success("Portfolio created");
          setName("");
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
          <DialogTitle>Create Portfolio</DialogTitle>
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
            <Button type="submit" disabled={!name.trim() || createPortfolio.isPending}>
              {createPortfolio.isPending ? "Creating..." : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
