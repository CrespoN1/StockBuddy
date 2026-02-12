"use client";

import Link from "next/link";
import { MoreVertical, Pencil, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { formatDate } from "@/lib/format";
import type { PortfolioRead } from "@/types";

interface PortfolioCardProps {
  portfolio: PortfolioRead;
  onEdit: (portfolio: PortfolioRead) => void;
  onDelete: (portfolio: PortfolioRead) => void;
}

export function PortfolioCard({ portfolio, onEdit, onDelete }: PortfolioCardProps) {
  return (
    <Card className="transition-colors hover:bg-accent/50">
      <CardHeader className="flex flex-row items-start justify-between pb-2">
        <Link href={`/portfolios/${portfolio.id}`} className="flex-1">
          <CardTitle className="text-base">{portfolio.name}</CardTitle>
        </Link>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(portfolio)}>
              <Pencil className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onDelete(portfolio)}
              className="text-destructive"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </CardHeader>
      <CardContent>
        <Link href={`/portfolios/${portfolio.id}`}>
          <p className="text-sm text-muted-foreground">
            Created {formatDate(portfolio.created_at)}
          </p>
        </Link>
      </CardContent>
    </Card>
  );
}
