/* Numbers for display: 4 significant figures, thin grouping, no trailing noise. */
export function fmt(v: number | null | undefined, digits = 4): string {
  if (v == null || !Number.isFinite(v)) return "—"
  if (v !== 0 && (Math.abs(v) >= 1e6 || Math.abs(v) < 1e-3)) return v.toExponential(2)
  return Number(v.toPrecision(digits)).toLocaleString("en-US", { maximumFractionDigits: 6 })
}
