import type { Station, StationState } from "@/lib/api"
import { fmt } from "@/lib/format"
import { heat } from "@/lib/heat"

// FlowState field -> (symbol, display unit, SI -> display scale)
const ROWS: [keyof StationState, string, string, number][] = [
  ["Tt", "Tₜ", "K", 1],
  ["T", "T", "K", 1],
  ["Pt", "Pₜ", "kPa", 1e-3],
  ["P", "P", "kPa", 1e-3],
  ["rho_t", "ρₜ", "kg/m³", 1],
  ["rho", "ρ", "kg/m³", 1],
  ["V", "V", "m/s", 1],
  ["M", "M", "–", 1],
  ["m_dot", "ṁ", "kg/s", 1],
]

/* Everything the model knows at the hovered station. */
export function StationReadout({ station, TtRange }: { station: Station; TtRange: [number, number] }) {
  const t = ((station.Tt ?? 0) - TtRange[0]) / (TtRange[1] - TtRange[0] || 1)
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-line px-4 py-3.5">
        <div className="eyebrow">Station</div>
        <div className="mt-1.5 flex items-center gap-2.5">
          <span className="tabular rounded-md border border-heat bg-heat-soft px-1.5 py-0.5 text-[13px] text-heat">{station.key}</span>
          <span className="text-[14px] text-fg">{station.name}</span>
        </div>
        <div className="mt-3 h-1 rounded-full" style={{ background: heat(t), boxShadow: `0 0 12px ${heat(t)}` }} />
      </div>
      <dl className="flex-1 divide-y divide-line px-4">
        {ROWS.map(([field, symbol, unit, scale]) => {
          const v = station[field]
          return (
            <div key={field} className="flex items-baseline justify-between py-2">
              <dt className="text-[12.5px] text-fg-2">{symbol}</dt>
              <dd className="tabular text-[13px]">
                <span className={v == null ? "text-fg-3" : "text-fg"}>{fmt(v == null ? null : v * scale)}</span>
                <span className="ml-1.5 inline-block w-11 text-[11px] text-fg-3">{unit}</span>
              </dd>
            </div>
          )
        })}
      </dl>
      <p className="border-t border-line px-4 py-3 text-[11.5px] leading-relaxed text-fg-3">
        Hover the drawing or the plots to move between stations. “—” means the model does not compute it there.
      </p>
    </div>
  )
}
