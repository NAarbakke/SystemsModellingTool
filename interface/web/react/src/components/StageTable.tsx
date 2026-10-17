import type { Compressor, Tile } from "@/lib/api"
import { fmt } from "@/lib/format"
import { cn } from "@/lib/utils"

interface Props {
  sizing: Tile[]
  compressor: Compressor
  stage: number | null
  onStage: (stage: number | null) => void
}

/* Compressor sizing summary and one row per stage; the row under the pointer (here or in the drawing) is lit. */
export function StageTable({ sizing, compressor, stage, onStage }: Props) {
  return (
    <div className="flex h-full flex-col">
      <dl className="divide-y divide-line border-b border-line px-4">
        {sizing.map((t) => (
          <div key={t.label} className="flex items-baseline justify-between py-2">
            <dt className="text-[12.5px] text-fg-2">{t.label}</dt>
            <dd className="tabular text-[13px] text-fg">
              {t.value}<span className="ml-1.5 inline-block w-6 text-[11px] text-fg-3">{t.unit}</span>
            </dd>
          </div>
        ))}
      </dl>
      <table className="w-full text-[12px]" onPointerLeave={() => onStage(null)}>
        <thead>
          <tr className="eyebrow text-left">
            <th className="py-2.5 pl-4 font-normal">Stage</th>
            <th className="py-2.5 text-right font-normal">L mm</th>
            <th className="py-2.5 text-right font-normal">Hub</th>
            <th className="py-2.5 pr-4 text-right font-normal">Span</th>
          </tr>
        </thead>
        <tbody className="tabular">
          {compressor.stages.map((s, i) => (
            <tr
              key={s.n}
              onPointerEnter={() => onStage(i)}
              className={cn("border-t border-line transition-colors", i === stage ? "bg-heat-soft text-fg" : "text-fg-2")}
            >
              <td className={cn("py-2 pl-4", i === stage && "text-heat")}>S{s.n}</td>
              <td className="py-2 text-right">{fmt(s.length * 1e3, 3)}</td>
              <td className="py-2 text-right">{fmt(s.r_hub, 3)}</td>
              <td className="py-2 pr-4 text-right">{fmt(s.r_tip - s.r_hub, 3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
