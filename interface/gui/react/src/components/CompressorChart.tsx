import type { Compressor } from "@/lib/api"
import { bandPath, linear } from "@/lib/chart"
import { fmt } from "@/lib/format"
import { useWidth } from "@/lib/useWidth"

const M = { side: 56, top: 56, bottom: 40 }
const MAX_H = 320           // [px] tallest drawing; wider compressors shrink to fit, always true to shape
const CASING = 0.008        // [m] nominal

interface Props {
  compressor: Compressor
  stage: number | null
  onStage: (stage: number | null) => void
}

/* Sized axial compressor as a to-scale half section: annulus, blade rows and stage boundaries. */
export function CompressorChart({ compressor: c, stage, onStage }: Props) {
  const [ref, width] = useWidth<HTMLDivElement>()

  const rTop = Math.max(...c.annulus.hi) + CASING + 0.01
  const ppm = Math.min((width - 2 * M.side) / c.length, MAX_H / rTop)     // [px/m] same both ways
  const x0 = (width - c.length * ppm) / 2                                  // centred
  const sx = linear(0, c.length, x0, x0 + c.length * ppm)
  const plotH = rTop * ppm
  const sy = (r: number) => M.top + plotH - r * ppm
  const height = M.top + plotH + M.bottom

  const hub = { x: c.annulus.x, lo: c.annulus.x.map(() => 0), hi: c.annulus.lo }
  const casing = { x: c.annulus.x, lo: c.annulus.hi, hi: c.annulus.hi.map((r) => r + CASING) }
  const rTicks = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6].filter((r) => r <= rTop)

  return (
    <div ref={ref} className="w-full">
      {width > 0 && (
        <svg width={width} height={height} className="block select-none" onPointerLeave={() => onStage(null)}>
          <defs>
            <pattern id="dots-c" width="14" height="14" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="0.7" fill="#1d1d1d" />
            </pattern>
          </defs>
          <rect x={sx(0)} y={M.top} width={c.length * ppm} height={plotH} fill="url(#dots-c)" />

          {c.spans.map((s, i) => {
            const n = i - 1                                         // spans: IGV, stages..., EGV
            const isStage = n >= 0 && n < c.stages.length
            const on = isStage && n === stage
            const mid = (sx(s.x0) + sx(s.x1)) / 2
            return (
              <g key={s.name} onPointerEnter={() => onStage(isStage ? n : null)}>
                <rect x={sx(s.x0)} y={M.top - 44} width={sx(s.x1) - sx(s.x0)} height={plotH + 44} fill={on ? "var(--heat-soft)" : "transparent"} />
                <line x1={sx(s.x0)} x2={sx(s.x0)} y1={M.top - 44} y2={M.top + plotH} stroke="var(--line)" />
                <text x={mid} y={M.top - 28} textAnchor="middle" className="font-mono text-[10px] tracking-[0.06em] uppercase" fill={on ? "var(--heat)" : "var(--fg-3)"}>
                  {isStage ? `S${n + 1}` : s.name}
                </text>
                <text x={mid} y={M.top - 13} textAnchor="middle" className="tabular text-[11px]" fill={on ? "var(--fg)" : "var(--fg-2)"}>
                  {Math.round((s.x1 - s.x0) * 1e3)}
                </text>
              </g>
            )
          })}
          <line x1={sx(c.length)} x2={sx(c.length)} y1={M.top - 44} y2={M.top + plotH} stroke="var(--line)" />

          <g pointerEvents="none">
            <path d={bandPath(c.annulus, sx, sy)} fill="rgb(255 138 61 / 0.07)" />
            {c.stators.map((b, i) => <path key={`s${i}`} d={bandPath(b, sx, sy)} fill="rgb(237 237 237 / 0.18)" />)}
            {c.rotors.map((b, i) => <path key={`r${i}`} d={bandPath(b, sx, sy)} fill="rgb(237 237 237 / 0.55)" />)}
            <path d={bandPath(hub, sx, sy)} fill="#111111" stroke="#262626" strokeWidth={0.75} />
            <path d={bandPath(casing, sx, sy)} fill="#2a2a2a" stroke="#3a3a3a" strokeWidth={0.75} />
            <line x1={sx(0) - 12} x2={sx(c.length) + 12} y1={sy(0)} y2={sy(0)} stroke="var(--line-strong)" strokeDasharray="8 4 2 4" />
          </g>

          {rTicks.map((r) => (
            <text key={r} x={sx(0) - 10} y={sy(r)} textAnchor="end" dominantBaseline="middle" className="tabular text-[10px]" fill="var(--fg-3)">{r.toFixed(1)}</text>
          ))}
          <text x={sx(0) - 10} y={M.top - 13} textAnchor="end" className="font-mono text-[10px]" fill="var(--fg-3)">mm</text>
          <text x={sx(0)} y={height - 12} className="font-mono text-[10px]" fill="var(--fg-3)">
            Radius [m] · axial lengths [mm] · flow left to right · {fmt(c.length * 1e3, 3)} mm face to EGV exit
          </text>
        </svg>
      )}
    </div>
  )
}
