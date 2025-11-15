"use client";

import * as React from "react";
import { GripVerticalIcon } from "lucide-react";

import { cn } from "./utils";

type DivProps = React.HTMLAttributes<HTMLDivElement>;

/**
 * Fallback, dependency-free resizable primitives.
 * These mimic the original component signatures so other modules can import them
 * without requiring the heavy react-resizable-panels runtime.
 */
function ResizablePanelGroup({ className, ...props }: DivProps) {
  return (
    <div
      data-slot="resizable-panel-group"
      className={cn("flex h-full w-full", className)}
      {...props}
    />
  );
}

function ResizablePanel({ className, ...props }: DivProps) {
  return (
    <div
      data-slot="resizable-panel"
      className={cn("flex-1", className)}
      {...props}
    />
  );
}

type HandleProps = DivProps & {
  withHandle?: boolean;
};

function ResizableHandle({ withHandle, className, ...props }: HandleProps) {
  return (
    <div
      data-slot="resizable-handle"
      role="separator"
      aria-orientation="vertical"
      className={cn(
        "relative flex w-px items-center justify-center bg-border/50 data-[orientation=vertical]:h-px data-[orientation=vertical]:w-full",
        className,
      )}
      {...props}
    >
      {withHandle ? (
        <div className="bg-border text-muted-foreground flex size-4 items-center justify-center rounded-sm border shadow-sm">
          <GripVerticalIcon className="size-3.5" />
          <span className="sr-only">Resize</span>
        </div>
      ) : null}
    </div>
  );
}

export { ResizablePanelGroup, ResizablePanel, ResizableHandle };
