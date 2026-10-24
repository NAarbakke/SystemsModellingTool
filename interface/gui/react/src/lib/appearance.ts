/*
 * Themes and fonts. A theme is a set of colour tokens in index.css (selected by <html data-theme>) plus its
 * total-temperature scale and default font; a font choice overrides the theme's font. Choices persist per browser.
 */
import { setHeatStops, type HeatStops } from "@/lib/heat"

export interface Theme {
  id: string
  label: string
  description: string
  font: string                                  // default font id
  swatch: [string, string, string]              // background, text, accent (menu preview only)
  heat: HeatStops                               // total temperature scale, cold -> hot
}

// Dark backgrounds: cold gas near-black, hot gas white
const EMBER: HeatStops = [
  [0.0, [38, 20, 12]], [0.35, [122, 46, 14]], [0.65, [224, 86, 27]], [0.85, [255, 157, 77]], [1.0, [255, 227, 179]]]
// Light backgrounds: cold gas pale, hot gas deep red
const PAPER_HEAT: HeatStops = [
  [0.0, [253, 240, 222]], [0.35, [252, 190, 120]], [0.65, [234, 96, 30]], [0.85, [190, 40, 30]], [1.0, [120, 18, 24]]]
const SEPIA_HEAT: HeatStops = [
  [0.0, [240, 230, 210]], [0.35, [214, 176, 128]], [0.65, [178, 92, 52]], [0.85, [140, 40, 36]], [1.0, [92, 18, 24]]]
const PLASMA: HeatStops = [
  [0.0, [22, 14, 58]], [0.35, [104, 36, 158]], [0.65, [214, 56, 124]], [0.85, [248, 140, 64]], [1.0, [250, 230, 120]]]

export const THEMES: Theme[] = [
  { id: "graphite", label: "Graphite", description: "Monochrome on black", font: "geist",
    swatch: ["#000000", "#ededed", "#ff8a3d"], heat: EMBER },
  { id: "daylight", label: "Daylight", description: "Light, clean", font: "inter",
    swatch: ["#fafafa", "#18181b", "#e8590c"], heat: PAPER_HEAT },
  { id: "aurora", label: "Aurora", description: "Modern, deep indigo", font: "grotesk",
    swatch: ["#07071a", "#e9e7ff", "#22d3ee"], heat: PLASMA },
  { id: "academic", label: "Academic", description: "Paper, serif, journal figure", font: "serif",
    swatch: ["#f6f1e7", "#1f1a14", "#8c1d18"], heat: SEPIA_HEAT },
  { id: "blueprint", label: "Blueprint", description: "Drafting table", font: "plex",
    swatch: ["#0b2545", "#e6f0ff", "#ffd166"], heat: EMBER },
]

export interface Font {
  id: string
  label: string
  sans: string
  mono: string
}

export const FONTS: Font[] = [
  { id: "geist", label: "Geist", sans: '"Geist Variable"', mono: '"Geist Mono Variable"' },
  { id: "inter", label: "Inter", sans: '"Inter Variable"', mono: '"JetBrains Mono Variable"' },
  { id: "grotesk", label: "Space Grotesk", sans: '"Space Grotesk Variable"', mono: '"Space Mono"' },
  { id: "plex", label: "IBM Plex", sans: '"IBM Plex Sans Variable"', mono: '"IBM Plex Mono"' },
  { id: "manrope", label: "Manrope", sans: '"Manrope Variable"', mono: '"JetBrains Mono Variable"' },
  { id: "serif", label: "Source Serif", sans: '"Source Serif 4 Variable"', mono: '"IBM Plex Mono"' },
  { id: "fraunces", label: "Fraunces", sans: '"Fraunces Variable"', mono: '"JetBrains Mono Variable"' },
]

export const THEME_FONT = "theme"               // font id meaning "the theme's own font"

export interface Appearance { theme: string; font: string }

const KEY = "appearance"
const DEFAULT: Appearance = { theme: "graphite", font: THEME_FONT }

export function loadAppearance(): Appearance {
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) ?? "{}")
    return {
      theme: THEMES.some((t) => t.id === saved.theme) ? saved.theme : DEFAULT.theme,
      font: saved.font === THEME_FONT || FONTS.some((f) => f.id === saved.font) ? saved.font : DEFAULT.font,
    }
  } catch {
    return DEFAULT
  }
}

export function applyAppearance(a: Appearance) {
  const theme = THEMES.find((t) => t.id === a.theme) ?? THEMES[0]
  const font = FONTS.find((f) => f.id === (a.font === THEME_FONT ? theme.font : a.font)) ?? FONTS[0]
  const root = document.documentElement
  root.dataset.theme = theme.id
  root.style.setProperty("--app-sans", `${font.sans}, system-ui, sans-serif`)
  root.style.setProperty("--app-mono", `${font.mono}, ui-monospace, monospace`)
  setHeatStops(theme.heat)
  try { localStorage.setItem(KEY, JSON.stringify(a)) } catch { /* private window: choice lasts this visit */ }
}
