import * as React from "react"
import { Slider as SliderPrimitive } from "radix-ui"

import { cn } from "@/lib/utils"

/* shadcn/ui Slider, restyled: hairline track, the filled range shows how far along the input is */
function Slider({ className, ...props }: React.ComponentProps<typeof SliderPrimitive.Root>) {
  const values = props.value ?? props.defaultValue ?? [props.min ?? 0]
  return (
    <SliderPrimitive.Root
      data-slot="slider"
      className={cn(
        "group relative flex w-full touch-none items-center select-none py-2 data-[disabled]:opacity-50",
        className,
      )}
      {...props}
    >
      <SliderPrimitive.Track data-slot="slider-track" className="relative h-[2px] w-full grow overflow-hidden rounded-full bg-line-strong">
        <SliderPrimitive.Range data-slot="slider-range" className="absolute h-full bg-fg-2 group-data-[changed=true]:bg-heat" />
      </SliderPrimitive.Track>
      {values.map((_, i) => (
        <SliderPrimitive.Thumb
          data-slot="slider-thumb"
          key={i}
          className="block size-3 rounded-full border border-bg bg-fg shadow-[0_0_0_1px_var(--line-strong)] transition-[box-shadow,transform] hover:scale-110 focus-visible:shadow-[0_0_0_4px_var(--heat-soft),0_0_0_1px_var(--heat)] focus-visible:outline-none"
        />
      ))}
    </SliderPrimitive.Root>
  )
}

export { Slider }
