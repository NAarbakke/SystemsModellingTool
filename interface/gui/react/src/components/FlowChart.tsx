import { useMemo } from "react"

import type { EngineLayout, PanelDef, Station } from "@/lib/api"
import { bandPath, gappedLine, linear, niceTicks } from "@/lib/chart"
import { fmt } from "@/lib/format"
import { heat } from "@/lib/heat"
import { useWidth } from "@/lib/useWidth"

const M = { left: 64, right: 20 }      // [px] plot margins
const TAG_ROW = 30                      // [px] station tags above the engine
const PANEL_H = 128                     // [px] one station plot
const PANEL_GAP = 36
const TITLE_ROW = 30                    // [px] panel title + legend above each plot, kept clear of vertical lines
const AXIS_H = 44                       // [px] station names under the plots
const DASHES = ["", "5 4"]              // per stream

// Drawing colours are theme tokens (index.css)
const ROTOR = "var(--rotor)"
const STATOR = "var(--stator)"
const SOLID = { body: { fill: "var(--body)", stroke: "var(--body-line)" }, casing: { fill: "var(--casing)", stroke: "var(--casing-line)" } }
const SERIES = { total: "var(--fg)", static: "var(--heat)", none: "var(--fg-2)" }
const LEGEND_CHAR = 6.4                 // [px] width of one 10.5 px mono character
const LEGEND_SWATCH = 18                // [px] line sample + gap before its label
const LEGEND_GAP = 18                   // [px] between legend entries

interface LegendEntry { label: string; stroke: string; dash: string }

/* Panel legend, right-aligned to x = right */
function Legend({ entries, right, y }: { entries: LegendEntry[]; right: number; y: number }) {
  const widths = entries.map((e) => e.label.length * LEGEND_CHAR + LEGEND_SWATCH)
  const placed = entries.map((e, i) => ({
    ...e,
    at: right - widths.slice(i).reduce((a, b) => a + b, 0) - (entries.length - 1 - i) * LEGEND_GAP,
  }))
  return (
    <g>
      {placed.map((e) => (
        <g key={e.label} transform={`translate(${e.at}, ${y})`}>
          <line x1={0} x2={12} y1={-3.5} y2={-3.5} stroke={e.stroke} strokeWidth={1.5} strokeDasharray={e.dash} />
          <text x={LEGEND_SWATCH} className="font-mono text-[10.5px]" fill="var(--fg-2)">{e.label}</text>
        </g>
      ))}
    </g>
  )
}

interface Props {
  layout: EngineLayout
  stations: Station[]
  streams: Record<string, string[]>
  panels: PanelDef[]
  hovered: string
  onHover: (station: string) => void
}

/* Engine cross-section on top, station plots underneath, all on one axial scale; the crosshair snaps to stations. */
export function FlowChart({ layout, stations, streams, panels, hovered, onHover }: Props) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const byKey = useMemo(() => Object.fromEntries(stations.map((s) => [s.key, s])), [stations])

  const [x0, x1] = layout.x_range
  const sx = linear(x0, x1, M.left, Math.max(width - M.right, M.left + 1))
  const ppm = (sx(1) - sx(0))                                   // [px/m] same both ways: true to shape
  const engineH = 2 * (layout.r_max + layout.label_room) * ppm
  const cy = TAG_ROW + engineH / 2
  const sy = (r: number) => cy - r * ppm
  const panelsTop = TAG_ROW + engineH + 24
  const height = panelsTop + panels.length * (PANEL_H + PANEL_GAP) + AXIS_H
  const panelTop = (row: number) => panelsTop + row * (PANEL_H + PANEL_GAP)

  // Vertical lines (stations, crosshair) run top to bottom but break over each panel's title row
  const bottom = height - AXIS_H + 4
  const breaks = panels.map((_, row) => [panelTop(row) - 10, panelTop(row) + TITLE_ROW - 12])
  const spans = (y0: number): [number, number][] =>
    [y0, ...breaks.flat(), bottom].reduce<[number, number][]>((out, y, i, ys) => (i % 2 === 0 ? [...out, [y, ys[i + 1]]] : out), [])

  const Tt = stations.map((s) => s.Tt ?? 0)
  const [TtLo, TtHi] = [Math.min(...Tt), Math.max(...Tt)]
  const colour = (T: number) => heat((T - TtLo) / (TtHi - TtLo || 1))

  // Stations sharing a position share a tag
  const positions = [...new Set(stations.map((s) => s.x))].sort((a, b) => a - b)
  const atX = (x: number) => stations.filter((s) => s.x === x).map((s) => s.key)
  const hoveredX = byKey[hovered]?.x
  const roomForNames = positions.every((x, i) => i === 0 || sx(x) - sx(positions[i - 1]) > 84)

  const nearest = (px: number) => {
    const x = positions.reduce((best, p) => (Math.abs(sx(p) - px) < Math.abs(sx(best) - px) ? p : best), positions[0])
    onHover(atX(x).at(-1)!)
  }

  // Flow arrows: into the first gas path, out of every path that ends in the atmosphere
  const starts = new Set(layout.gas_paths.map((p) => p.x[0]))
  const arrows = [
    { path: layout.gas_paths[0], end: 0, dir: -1 },
    ...layout.gas_paths.filter((p) => !starts.has(p.x.at(-1)!)).map((path) => ({ path, end: path.x.length - 1, dir: 1 })),
  ]

  return (
    <div ref={ref} className="w-full">
      {width > 0 && (
        <svg width={width} height={height} className="block select-none" onPointerMove={(e) => nearest(e.clientX - e.currentTarget.getBoundingClientRect().left)}>
          <defs>
            <pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="0.7" fill="var(--dots)" />
            </pattern>
            {layout.gas_paths.map((p, i) => {
              const xs = p.stops.map((s) => s.x)
              const [a, b] = [Math.min(...xs), Math.max(...xs)]
              return (
                <linearGradient key={i} id={`gas-${i}`} gradientUnits="userSpaceOnUse" x1={sx(a)} x2={sx(b)} y1="0" y2="0">
                  {p.stops.map((s, k) => <stop key={k} offset={(s.x - a) / (b - a || 1)} stopColor={colour(s.Tt)} />)}
                </linearGradient>
              )
            })}
          </defs>

          {/* Drawing board */}
          <rect x={M.left} y={TAG_ROW} width={width - M.left - M.right} height={engineH} fill="url(#dots)" />
          <line x1={M.left} x2={width - M.right} y1={cy} y2={cy} stroke="var(--line-strong)" strokeDasharray="8 4 2 4" />

          {/* Station lines through everything */}
          {positions.map((x) => (
            <g key={x}>
              {spans(TAG_ROW - 4).map(([y1, y2]) => <line key={y1} x1={sx(x)} x2={sx(x)} y1={y1} y2={y2} stroke="var(--line)" />)}
            </g>
          ))}

          {/* Engine, mirrored about the centreline */}
          {[1, -1].map((sign) => (
            <g key={sign}>
              {layout.gas_paths.map((p, i) => <path key={i} d={bandPath(p, sx, sy, sign)} fill={`url(#gas-${i})`} />)}
              {layout.rods?.r.map((r) => (
                <line key={r} x1={sx(layout.rods!.x0)} x2={sx(layout.rods!.x1)} y1={sy(sign * r)} y2={sy(sign * r)} stroke="var(--rods)" />
              ))}
              {layout.liner && <path d={bandPath(layout.liner, sx, sy, sign)} fill="none" stroke="var(--liner)" strokeDasharray="3 2" />}
              {layout.stators.map((b, i) => <path key={`s${i}`} d={bandPath(b, sx, sy, sign)} fill={STATOR} />)}
              {layout.rotors.map((b, i) => <path key={`r${i}`} d={bandPath(b, sx, sy, sign)} fill={ROTOR} />)}
              {layout.solids.map((b, i) => (
                <path key={`b${i}`} d={bandPath(b, sx, sy, sign)} fill={SOLID[b.kind].fill} stroke={SOLID[b.kind].stroke} strokeWidth={0.75} />
              ))}
            </g>
          ))}

          {arrows.map(({ path, end, dir }, i) => {
            const r = (path.lo[end] + path.hi[end]) / 2
            const xa = sx(path.x[end]) + dir * 10
            const xb = sx(path.x[end]) + dir * Math.min(0.2 * ppm, 70)
            const [tail, head] = dir > 0 ? [xa, xb] : [xb, xa]
            return [r, -r].map((rr) => (
              <g key={`${i}${rr}`} stroke="var(--fg-3)" strokeWidth={1.25} fill="none">
                <line x1={tail} x2={head} y1={sy(rr)} y2={sy(rr)} />
                <polyline points={`${head - 6},${sy(rr) - 4} ${head},${sy(rr)} ${head - 6},${sy(rr) + 4}`} />
              </g>
            ))
          })}

          {layout.labels.map((l) => (
            <text
              key={l.text} x={sx(l.x)} y={l.r == null ? sy(-(layout.r_max + layout.label_room * 0.55)) : sy(l.r)}
              textAnchor="middle" dominantBaseline="middle" className="font-mono text-[10px] tracking-[0.08em] uppercase" fill="var(--fg-3)"
            >
              {l.text}
            </text>
          ))}

          {/* Station tags */}
          {positions.map((x) => {
            const keys = atX(x)
            const on = x === hoveredX
            const text = keys.join(" / ")
            const w = 10 + text.length * 6.6
            return (
              <g key={x} transform={`translate(${sx(x)}, ${TAG_ROW - 16})`}>
                <rect x={-w / 2} y={-9} width={w} height={18} rx={4} fill={on ? "var(--heat-soft)" : "var(--surface)"} stroke={on ? "var(--heat)" : "var(--line-strong)"} />
                <text textAnchor="middle" dominantBaseline="central" className="font-mono text-[11px]" fill={on ? "var(--heat)" : "var(--fg-2)"}>{text}</text>
              </g>
            )
          })}

          {/* Station plots */}
          {panels.map((panel, row) => {
            const top = panelTop(row)
            const plotTop = top + TITLE_ROW
            const values = panel.series.flatMap((s) => stations.map((st) => st[s.field])).filter((v): v is number => v != null).map((v) => v * panel.scale)
            const [lo, hi] = values.length ? [Math.min(...values), Math.max(...values)] : [0, 1]
            const pad = (hi - lo || Math.abs(hi) || 1) * 0.12
            const ys = linear(lo - pad, hi + pad, top + PANEL_H, plotTop)
            const streamNames = Object.keys(streams)
            const legend: LegendEntry[] = [
              ...panel.series.map((s) => ({ label: s.kind ? `${s.symbol} ${s.kind}` : s.symbol, stroke: SERIES[s.kind ?? "none"], dash: "" })),
              ...(streamNames.length > 1 ? streamNames.map((n, si) => ({ label: n.toLowerCase(), stroke: "var(--fg-3)", dash: DASHES[si] })) : []),
            ]
            return (
              <g key={panel.name}>
                <text x={M.left} y={top + 6} className="text-[12px] font-medium" fill="var(--fg)">
                  {panel.name} <tspan className="font-mono text-[11px]" fill="var(--fg-3)">[{panel.unit}]</tspan>
                </text>
                <Legend entries={legend} right={width - M.right} y={top + 6} />
                {niceTicks(lo - pad, hi + pad, 3).map((t) => (
                  <g key={t}>
                    <line x1={M.left} x2={width - M.right} y1={ys(t)} y2={ys(t)} stroke="var(--line)" />
                    <text x={M.left - 10} y={ys(t)} textAnchor="end" dominantBaseline="middle" className="tabular text-[10px]" fill="var(--fg-3)">{fmt(t, 3)}</text>
                  </g>
                ))}
                {Object.entries(streams).map(([stream, keys], si) => panel.series.map((s) => {
                  const pts = keys.map((k) => [sx(byKey[k].x), byKey[k][s.field] == null ? null : ys(byKey[k][s.field]! * panel.scale)] as [number, number | null])
                  const stroke = SERIES[s.kind ?? "none"]
                  return (
                    <g key={`${stream}${s.field}`}>
                      <path d={gappedLine(pts)} fill="none" stroke={stroke} strokeWidth={1.5} strokeDasharray={DASHES[si]} />
                      {pts.map(([x, y], k) => y != null && (
                        <circle key={k} cx={x} cy={y} r={keys[k] === hovered ? 4.5 : 3} fill="var(--bg)" stroke={stroke} strokeWidth={keys[k] === hovered ? 2 : 1.5} />
                      ))}
                    </g>
                  )
                }))}
              </g>
            )
          })}

          {/* Station axis */}
          {positions.map((x) => {
            const keys = atX(x)
            return (
              <g key={x} transform={`translate(${sx(x)}, ${height - AXIS_H + 18})`}>
                <text textAnchor="middle" className="font-mono text-[11px]" fill={x === hoveredX ? "var(--heat)" : "var(--fg-2)"}>{keys.join(" / ")}</text>
                {roomForNames && <text y={15} textAnchor="middle" className="text-[11px]" fill="var(--fg-3)">{byKey[keys[0]].name}</text>}
              </g>
            )
          })}

          {/* Crosshair */}
          {hoveredX != null && (
            <g pointerEvents="none">
              {spans(TAG_ROW - 7).map(([y1, y2]) => <line key={y1} x1={sx(hoveredX)} x2={sx(hoveredX)} y1={y1} y2={y2} stroke="var(--heat)" strokeOpacity={0.6} />)}
            </g>
          )}
        </svg>
      )}
    </div>
  )
}
