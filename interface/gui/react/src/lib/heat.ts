/* Total temperature -> colour. The scale comes from the theme (appearance.ts): on dark themes cold is near-black
 * and hot white; on light themes cold is pale and hot deep red. */
export type HeatStops = [number, [number, number, number]][]

let STOPS: HeatStops = [
  [0.0, [38, 20, 12]],
  [0.35, [122, 46, 14]],
  [0.65, [224, 86, 27]],
  [0.85, [255, 157, 77]],
  [1.0, [255, 227, 179]],
]

export function setHeatStops(stops: HeatStops) {
  STOPS = stops
}

export function heat(t: number): string {
  const u = Math.min(1, Math.max(0, t))
  const i = Math.max(0, STOPS.findIndex(([s]) => s >= u) - 1)
  const [s0, c0] = STOPS[i]
  const [s1, c1] = STOPS[Math.min(i + 1, STOPS.length - 1)]
  const f = s1 === s0 ? 0 : (u - s0) / (s1 - s0)
  const c = c0.map((v, k) => Math.round(v + f * (c1[k] - v)))
  return `rgb(${c[0]} ${c[1]} ${c[2]})`
}

export const heatGradient = () => `linear-gradient(90deg, ${STOPS.map(([s]) => `${heat(s)} ${s * 100}%`).join(", ")})`
