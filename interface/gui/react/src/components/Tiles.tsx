import type { Tile } from "@/lib/api"
import { cn } from "@/lib/utils"

/* One bordered strip split by hairlines (the 1px gap shows the line colour behind the cells). */
export function Tiles({ tiles, className }: { tiles: Tile[]; className?: string }) {
  return (
    <div className={cn("flex flex-wrap gap-px overflow-hidden rounded-xl border border-line bg-line", className)}>
      {tiles.map((t) => (
        <div key={t.label} className={cn("min-w-[150px] flex-1 bg-surface px-4 py-3.5", t.hero && "min-w-[300px] flex-[2] bg-[radial-gradient(120%_140%_at_0%_0%,var(--heat-soft),transparent_60%),var(--surface)]")}>
          <div className="text-[12px] text-fg-3">{t.label}</div>
          <div className={cn("mt-1.5 flex items-baseline gap-1.5 leading-none tabular-nums", t.hero ? "text-[44px] font-medium tracking-[-0.03em]" : "text-[24px] tracking-tight")}>
            {t.status ? (
              <span className={cn("flex items-center gap-2 text-[17px]", t.status === "good" ? "text-good" : "text-bad")}>
                <span className={cn("size-2 rounded-full", t.status === "good" ? "bg-good" : "bg-bad")} />
                {t.value}
              </span>
            ) : (
              <>
                <span className="text-fg">{t.value}</span>
                {t.unit && <span className="font-mono text-[11.5px] text-fg-3">{t.unit}</span>}
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
