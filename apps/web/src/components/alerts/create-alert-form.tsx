"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCreateAlert } from "@/hooks/use-alerts";

interface Props {
  defaultTicker?: string;
}

export function CreateAlertForm({ defaultTicker }: Props) {
  const [ticker, setTicker] = useState(defaultTicker ?? "");
  const [price, setPrice] = useState("");
  const [direction, setDirection] = useState<"above" | "below">("above");
  const createAlert = useCreateAlert();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const t = ticker.trim().toUpperCase();
    const p = parseFloat(price);
    if (!t || isNaN(p) || p <= 0) {
      toast.error("Enter a valid ticker and price");
      return;
    }
    createAlert.mutate(
      { ticker: t, target_price: p, direction },
      {
        onSuccess: () => {
          toast.success(`Alert created: ${t} ${direction} $${p.toFixed(2)}`);
          if (!defaultTicker) setTicker("");
          setPrice("");
        },
        onError: (err) => toast.error(err.message),
      }
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3">
      <div className="space-y-1">
        <label className="text-sm font-medium">Ticker</label>
        <Input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="AAPL"
          className="w-28"
          disabled={!!defaultTicker}
        />
      </div>
      <div className="space-y-1">
        <label className="text-sm font-medium">Direction</label>
        <Select
          value={direction}
          onValueChange={(v) => setDirection(v as "above" | "below")}
        >
          <SelectTrigger className="w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="above">Above</SelectItem>
            <SelectItem value="below">Below</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1">
        <label className="text-sm font-medium">Target Price</label>
        <Input
          type="number"
          step="0.01"
          min="0.01"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          placeholder="150.00"
          className="w-32"
        />
      </div>
      <Button type="submit" disabled={createAlert.isPending}>
        <Plus className="mr-2 h-4 w-4" />
        Add Alert
      </Button>
    </form>
  );
}
