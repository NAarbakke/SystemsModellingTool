import type { Band } from "./api"

/* Small chart helpers shared by the flow chart and the compressor drawing. */

export type Scale = (v: number) => number

export const linear = (d0: number, d1: number, r0: number, r1: number): Scale =>
  (v) => r0 + ((v - d0) / (d1 - d0 || 1)) * (r1 - r0)

/* SVG path of a band; sign -1 draws its mirror image below the centreline */
export function bandPath(b: Band, sx: Scale, sy: Scale, sign = 1): string {
  const top = b.x.map((x, i) => `${sx(x).toFixed(1)},${sy(sign * b.hi[i]).toFixed(1)}`)
  const bottom = b.x.map((x, i) => `${sx(x).toFixed(1)},${sy(sign * b.lo[i]).toFixed(1)}`).reverse()
  return `M${top.join("L")}L${bottom.join("L")}Z`
}

/* Line through points, broken wherever a value is missing (never interpolated across a gap) */
export function gappedLine(points: [number, number | null][]): string {
  let d = ""
  let pen = false
  for (const [x, y] of points) {
    if (y == null) { pen = false; continue }
    d += `${pen ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`
    pen = true
  }
  return d
}

/* Round tick values covering [lo, hi] */
export function niceTicks(lo: number, hi: number, count = 3): number[] {
  if (lo === hi) return [lo]
  const raw = (hi - lo) / count
  const mag = 10 ** Math.floor(Math.log10(raw))
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? raw
  const ticks = []
  for (let t = Math.ceil(lo / step) * step; t <= hi + step * 1e-9; t += step) ticks.push(Number(t.toPrecision(12)))
  return ticks
}
