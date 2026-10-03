import type { ComponentProps } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-sm border px-2 py-0.5 text-xs font-medium tracking-wide uppercase",
  {
    variants: {
      variant: {
        default: "border-border text-muted bg-surface",
        active: "border-accent/30 text-accent-fg bg-accent",
        idle: "border-border text-muted",
        compose: "border-border-strong text-fg bg-surface-2",
        mode: "border-accent/40 text-fg bg-surface",
        error: "border-danger/40 text-danger-fg bg-danger",
        ok: "border-ok/40 text-ok bg-surface",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export function Badge({
  className,
  variant,
  ...props
}: ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
