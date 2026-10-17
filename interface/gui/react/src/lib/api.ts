/* The FastAPI contract (interface/api/serialise.py). Lengths in metres, everything SI unless a tile says otherwise. */

export type Value = number | string

export interface InputDef {
  key: string
  label: string
  default: Value
  lo: number
  hi: number
  step: number
  options?: { value: string; label: string }[]
}

export interface PanelDef {
  name: string
  unit: string
  scale: number
  series: { field: keyof StationState; symbol: string; kind: "total" | "static" | null }[]
}

export interface EngineDef {
  id: string
  label: string
  title: string
  inputs: { group: string; items: InputDef[] }[]
  panels: PanelDef[]
}

export interface Tile {
  label: string
  value: string
  unit: string
  status: "good" | "critical" | null
  hero: boolean
}

/* Upper half of a shape: lower and upper radius curves over x */
export interface Band { x: number[]; lo: number[]; hi: number[] }

export interface StationState {
  Tt: number | null; Pt: number | null; T: number | null; P: number | null; M: number | null
  V: number | null; rho: number | null; rho_t: number | null; m_dot: number | null
}

export interface Station extends StationState { key: string; name: string; x: number }

export interface EngineLayout {
  x_range: [number, number]
  r_max: number
  label_room: number
  gas_paths: (Band & { stops: { x: number; Tt: number }[] })[]
  solids: (Band & { kind: "body" | "casing" })[]
  rotors: Band[]
  stators: Band[]
  labels: { text: string; x: number; r: number | null }[]
  rods: { x0: number; x1: number; r: number[] } | null
  liner: Band | null
}

export interface Compressor {
  length: number
  annulus: Band
  rotors: Band[]
  stators: Band[]
  spans: { name: string; x0: number; x1: number }[]
  stages: { n: number; length: number; r_hub: number; r_tip: number }[]
}

export interface Snapshot {
  title: string
  subtitle: string
  error: string | null
  kpis?: Tile[]
  stations?: Station[]
  streams?: Record<string, string[]>
  layout?: EngineLayout
  sizing?: Tile[]
  compressor?: Compressor
}

export async function fetchEngines(): Promise<EngineDef[]> {
  const res = await fetch("/api/engines")
  if (!res.ok) throw new Error(`GET /api/engines: ${res.status}`)
  return res.json()
}

export async function evaluate(engine: string, values: Record<string, Value>, signal?: AbortSignal): Promise<Snapshot> {
  const res = await fetch(`/api/engines/${engine}/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(values),
    signal,
  })
  if (!res.ok) throw new Error((await res.json()).detail ?? `evaluate: ${res.status}`)
  return res.json()
}

export const defaults = (engine: EngineDef): Record<string, Value> =>
  Object.fromEntries(engine.inputs.flatMap((g) => g.items.map((i) => [i.key, i.default])))
