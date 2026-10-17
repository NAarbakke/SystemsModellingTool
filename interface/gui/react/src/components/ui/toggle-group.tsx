import * as React from "react"
import { ToggleGroup as ToggleGroupPrimitive } from "radix-ui"

import { cn } from "@/lib/utils"

/* shadcn/ui ToggleGroup, restyled as a segmented control (variant "segment") or a row of chips (variant "chip") */
type Variant = "segment" | "chip"
const VariantContext = React.createContext<Variant>("segment")

function ToggleGroup({
  className, variant = "segment", ...props
}: React.ComponentProps<typeof ToggleGroupPrimitive.Root> & { variant?: Variant }) {
  return (
    <VariantContext.Provider value={variant}>
      <ToggleGroupPrimitive.Root
        data-slot="toggle-group"
        className={cn(
          variant === "segment"
            ? "flex w-full rounded-lg border border-line bg-bg p-0.5"
            : "flex flex-wrap gap-1.5",
          className,
        )}
        {...props}
      />
    </VariantContext.Provider>
  )
}

function ToggleGroupItem({ className, ...props }: React.ComponentProps<typeof ToggleGroupPrimitive.Item>) {
  const variant = React.useContext(VariantContext)
  return (
    <ToggleGroupPrimitive.Item
      data-slot="toggle-group-item"
      className={cn(
        "cursor-pointer text-[13px] transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-heat",
        variant === "segment"
          ? "flex-1 rounded-md px-3 py-1.5 text-fg-3 hover:text-fg-2 data-[state=on]:bg-surface-2 data-[state=on]:text-fg data-[state=on]:shadow-[inset_0_0_0_1px_var(--line-strong)]"
          : "rounded-full border border-line px-3 py-1 font-mono text-[11px] tracking-wide text-fg-3 uppercase hover:border-line-strong hover:text-fg-2 data-[state=on]:border-fg-3 data-[state=on]:text-fg",
        className,
      )}
      {...props}
    />
  )
}

export { ToggleGroup, ToggleGroupItem }
