import type { EngineDef, InputDef, Value } from "@/lib/api"
import { fmt } from "@/lib/format"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"

interface Props {
  engines: EngineDef[]
  engine: EngineDef
  values: Record<string, Value>
  onEngine: (id: string) => void
  onChange: (key: string, value: Value) => void
  onReset: () => void
}

/* Engine picker and every input, grouped by component. A heat dot marks values changed from the specification. */
export function Sidebar({ engines, engine, values, onEngine, onChange, onReset }: Props) {
  const changed = (i: InputDef) => values[i.key] !== i.default
  const nChanged = engine.inputs.flatMap((g) => g.items).filter(changed).length

  return (
    <aside className="flex h-full w-[288px] flex-col border-r border-line bg-surface">
      <div className="border-b border-line p-4">
        <div className="eyebrow mb-2.5">Engine</div>
        <Select value={engine.id} onValueChange={onEngine}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            {engines.map((e) => <SelectItem key={e.id} value={e.id}>{e.label}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-6">
        {engine.inputs.map(({ group, items }) => (
          <section key={group} className="border-b border-line py-4 last:border-b-0">
            <h3 className="eyebrow mb-3">{group}</h3>
            <div className="space-y-3.5">
              {items.map((i) => (
                <Control key={i.key} input={i} value={values[i.key]} changed={changed(i)} onChange={(v) => onChange(i.key, v)} />
              ))}
            </div>
          </section>
        ))}
      </div>

      <div className="flex items-center justify-between border-t border-line px-4 py-3 text-[12px]">
        <span className="text-fg-3">
          {nChanged === 0 ? "SKYF specification" : `${nChanged} changed from SKYF spec`}
        </span>
        <button
          onClick={onReset}
          disabled={nChanged === 0}
          className="cursor-pointer rounded-md border border-line px-2 py-1 text-fg-2 transition-colors hover:border-line-strong hover:text-fg disabled:cursor-default disabled:opacity-40"
        >
          Reset
        </button>
      </div>
    </aside>
  )
}

function Control({ input, value, changed, onChange }: {
  input: InputDef; value: Value; changed: boolean; onChange: (v: Value) => void
}) {
  const label = (
    <span className="flex items-center gap-1.5 text-[12.5px] text-fg-2">
      {input.label}
      {changed && <span className="size-1.5 rounded-full bg-heat" title={`Spec: ${input.default}`} />}
    </span>
  )

  if (input.options) {
    return (
      <div className="space-y-1.5">
        {label}
        <Select value={String(value)} onValueChange={onChange}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            {input.options.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-baseline justify-between">
        {label}
        <span className={changed ? "tabular text-[12px] text-heat" : "tabular text-[12px] text-fg"}>{fmt(Number(value))}</span>
      </div>
      <Slider
        data-changed={changed}
        min={input.lo} max={input.hi} step={input.step}
        value={[Number(value)]}
        onValueChange={([v]) => onChange(v)}
      />
    </div>
  )
}
