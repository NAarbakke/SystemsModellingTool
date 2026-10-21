import { useEffect, useMemo, useState, type ReactNode } from "react"

import { CompressorChart } from "@/components/CompressorChart"
import { FlowChart } from "@/components/FlowChart"
import { Sidebar } from "@/components/Sidebar"
import { StageTable } from "@/components/StageTable"
import { StationReadout } from "@/components/StationReadout"
import { Tiles } from "@/components/Tiles"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { defaults, downloadReport, evaluate, fetchEngines, type EngineDef, type Snapshot, type Value } from "@/lib/api"
import { fmt } from "@/lib/format"
import { HEAT_GRADIENT } from "@/lib/heat"

const DEFAULT_PANELS = ["Temperature", "Pressure", "Velocity", "Mass flow"]

const FLOW_NOTE =
  "To scale where the model has geometry (axial compressor annulus and blade rows, fan, reactor length, nozzle exit areas); " +
  "other lengths are nominal. Bright rows are rotors, dim rows stators. Colour is total temperature, linear between stations."

export default function App() {
  const [engines, setEngines] = useState<EngineDef[]>([])
  const [engineId, setEngineId] = useState("conventional")
  const [values, setValues] = useState<Record<string, Record<string, Value>>>({})     // per engine, kept when switching
  const [snap, setSnap] = useState<Snapshot | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)
  const [latency, setLatency] = useState<number | null>(null)
  const [panelNames, setPanelNames] = useState(DEFAULT_PANELS)
  const [hovered, setHovered] = useState("6")
  const [stage, setStage] = useState<number | null>(null)

  useEffect(() => {
    fetchEngines()
      .then((list) => {
        setEngines(list)
        setValues(Object.fromEntries(list.map((e) => [e.id, defaults(e)])))
      })
      .catch(() => setApiError("Can't reach the model API. Start it from the repo root: .venv\\Scripts\\python -m interface.api.app"))
  }, [])

  const engine = engines.find((e) => e.id === engineId)
  const current = values[engineId]

  // Live: every change re-evaluates; a newer request cancels the one in flight
  useEffect(() => {
    if (!current) return
    const ctrl = new AbortController()
    const t0 = performance.now()
    evaluate(engineId, current, ctrl.signal)
      .then((s) => { setSnap(s); setLatency(performance.now() - t0); setApiError(null) })
      .catch((e) => { if (e.name !== "AbortError") setApiError(String(e.message ?? e)) })
    return () => ctrl.abort()
  }, [engineId, current])

  const panels = useMemo(() => engine?.panels.filter((p) => panelNames.includes(p.name)) ?? [], [engine, panelNames])
  const TtRange = useMemo<[number, number]>(() => {
    const Tt = snap?.stations?.map((s) => s.Tt ?? 0) ?? [0, 1]
    return [Math.min(...Tt), Math.max(...Tt)]
  }, [snap])
  const station = snap?.stations?.find((s) => s.key === hovered) ?? snap?.stations?.at(-1)

  if (!engine || !current) {
    return (
      <div className="grid h-screen place-items-center">
        <p className="tabular text-[13px] text-fg-3">{apiError ?? "Loading engines…"}</p>
      </div>
    )
  }

  return (
    <div className="grid h-screen grid-cols-[288px_1fr] grid-rows-[minmax(0,1fr)] overflow-hidden">
      <Sidebar
        engines={engines} engine={engine} values={current}
        onEngine={setEngineId}
        onChange={(key, v) => setValues((all) => ({ ...all, [engineId]: { ...all[engineId], [key]: v } }))}
        onReset={() => setValues((all) => ({ ...all, [engineId]: defaults(engine) }))}
      />

      <main className="min-w-0 overflow-y-auto">
        <header className="sticky top-0 z-10 flex h-12 items-center justify-between border-b border-line bg-bg/80 px-8 backdrop-blur">
          <nav className="flex items-center gap-2 text-[13px]">
            <Logo />
            <span className="text-fg-2">SKYF</span><Slash />
            <span className="text-fg-2">Propulsion</span><Slash />
            <span className="text-fg">{engine.label} turbojet</span>
          </nav>
          <div className="flex items-center gap-5">
            <ExportReport engine={engineId} values={current} disabled={!!snap?.error || !!apiError} onError={setApiError} />
            <div className="tabular flex items-center gap-2 text-[12px] text-fg-3">
              <span className={`size-1.5 rounded-full ${apiError ? "bg-bad" : "bg-good shadow-[0_0_8px_var(--good)]"}`} />
              {apiError ? "API unreachable" : `Live · ${latency == null ? "–" : Math.round(latency)} ms`}
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-[1680px] px-8 pt-8 pb-16">
          <h1 className="text-[26px] font-semibold tracking-tight">{snap?.title ?? engine.title}</h1>
          <p className="tabular mt-1 text-[12.5px] text-fg-3">{snap?.subtitle}</p>

          {apiError && <Banner>{apiError}</Banner>}
          {snap?.error && <Banner>{snap.error}</Banner>}

          {snap && !snap.error && snap.layout && snap.stations && station && (
            <>
              <Tiles tiles={snap.kpis!} className="mt-6" />

              <Section title="Flow path" aside={<Legend TtRange={TtRange} />}>
                <div className="flex items-center gap-3 border-b border-line px-4 py-2.5">
                  <ToggleGroup type="multiple" variant="chip" value={panelNames} onValueChange={setPanelNames}>
                    {engine.panels.map((p) => <ToggleGroupItem key={p.name} value={p.name}>{p.name}</ToggleGroupItem>)}
                  </ToggleGroup>
                </div>
                <div className="grid grid-cols-[1fr_272px]">
                  <div className="min-w-0 px-2 pt-4 pb-2">
                    <FlowChart layout={snap.layout} stations={snap.stations} streams={snap.streams!} panels={panels} hovered={station.key} onHover={setHovered} />
                  </div>
                  <div className="border-l border-line">
                    <StationReadout station={station} TtRange={TtRange} />
                  </div>
                </div>
              </Section>
              <p className="mt-2.5 max-w-[110ch] text-[12px] text-fg-3">{FLOW_NOTE}</p>

              {snap.compressor && snap.sizing && (
                <Section title="Compressor" aside={<span className="tabular text-[12px] text-fg-3">sized at the operating point</span>}>
                  <div className="grid grid-cols-[1fr_272px]">
                    <div className="min-w-0 px-2 pt-4">
                      <CompressorChart compressor={snap.compressor} stage={stage} onStage={setStage} />
                    </div>
                    <div className="border-l border-line">
                      <StageTable sizing={snap.sizing} compressor={snap.compressor} stage={stage} onStage={setStage} />
                    </div>
                  </div>
                </Section>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  )
}

function Section({ title, aside, children }: { title: string; aside?: ReactNode; children: ReactNode }) {
  return (
    <section className="mt-10">
      <div className="mb-3 flex items-end justify-between">
        <h2 className="text-[15px] font-medium text-fg">{title}</h2>
        {aside}
      </div>
      <div className="overflow-hidden rounded-xl border border-line bg-surface">{children}</div>
    </section>
  )
}

function Legend({ TtRange }: { TtRange: [number, number] }) {
  return (
    <div className="tabular flex items-center gap-5 text-[11.5px] text-fg-3">
      <span className="flex items-center gap-1.5"><span className="h-[2px] w-4 bg-fg" />Total</span>
      <span className="flex items-center gap-1.5"><span className="h-[2px] w-4 bg-heat" />Static</span>
      <span className="flex items-center gap-2">
        Tₜ {fmt(TtRange[0], 3)}
        <span className="h-1.5 w-24 rounded-full" style={{ background: HEAT_GRADIENT }} />
        {fmt(TtRange[1], 4)} K
      </span>
    </div>
  )
}

/* Typesets the PDF report (reports/) for the current inputs and downloads it; takes ~15-30 s */
function ExportReport({ engine, values, disabled, onError }: {
  engine: string; values: Record<string, Value>; disabled: boolean; onError: (e: string) => void
}) {
  const [busy, setBusy] = useState(false)
  const run = () => {
    setBusy(true)
    downloadReport(engine, values)
      .catch((e) => onError(`Report failed: ${e.message ?? e}`))
      .finally(() => setBusy(false))
  }
  return (
    <button
      onClick={run}
      disabled={disabled || busy}
      title="PDF engineering report: design point, flow state, compressor, airspeed sweep"
      className="tabular flex h-7 cursor-pointer items-center gap-2 rounded-md border border-line px-2.5 text-[12px] text-fg-2 transition-colors hover:border-line-strong hover:text-fg disabled:cursor-default disabled:opacity-50"
    >
      {busy
        ? <span className="size-3 animate-spin rounded-full border-[1.5px] border-heat border-t-transparent" />
        : <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M6 1.5v6M3.5 5 6 7.5 8.5 5M2 10.5h8" /></svg>}
      {busy ? "Typesetting report…" : "Export report"}
    </button>
  )
}

function Banner({ children }: { children: ReactNode }) {
  return (
    <div className="mt-6 flex items-start gap-3 rounded-xl border border-bad/40 bg-bad/[0.06] px-4 py-3 text-[13px] text-fg">
      <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-bad" />
      {children}
    </div>
  )
}

const Slash = () => <span className="text-line-strong">/</span>

/* Mark: a nozzle-shaped glyph in the heat gradient */
function Logo() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" className="mr-1">
      <defs>
        <linearGradient id="logo" x1="0" x2="1">
          <stop offset="0" stopColor="#7a2e0e" /><stop offset="0.6" stopColor="#ff8a3d" /><stop offset="1" stopColor="#ffe3b3" />
        </linearGradient>
      </defs>
      <path d="M2 4 L12 6.5 L18 5 L18 15 L12 13.5 L2 16 Z" fill="url(#logo)" />
    </svg>
  )
}
