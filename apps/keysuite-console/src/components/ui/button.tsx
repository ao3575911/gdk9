import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium select-none transition-[color,background-color,opacity,transform,box-shadow] duration-[150ms] ease-[cubic-bezier(0.23,1,0.32,1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-40 active:not-disabled:scale-[0.96]",
  {
    variants: {
      variant: {
        default: "bg-accent text-accent-fg hover:opacity-90",
        secondary:
          "bg-surface text-fg border border-border hover:border-border-strong hover:bg-surface-2",
        ghost: "text-muted hover:text-fg hover:bg-surface",
        outline: "border border-border text-fg bg-transparent hover:bg-surface",
        commit: "bg-accent text-accent-fg hover:opacity-90",
        abort: "border border-border text-muted hover:text-fg hover:bg-surface",
      },
      size: {
        default: "h-11 px-4 rounded-md",
        sm: "h-9 px-3 rounded-sm text-xs",
        lg: "h-12 px-5 rounded-md",
        icon: "size-11 rounded-md",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

type ButtonProps = React.ComponentProps<"button"> & VariantProps<typeof buttonVariants> & {
  asChild?: boolean;
};

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
