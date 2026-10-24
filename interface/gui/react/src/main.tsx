import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

// Every font the Appearance menu offers (lib/appearance.ts); the browser downloads only the ones in use
import "@fontsource-variable/geist"
import "@fontsource-variable/geist-mono"
import "@fontsource-variable/inter"
import "@fontsource-variable/jetbrains-mono"
import "@fontsource-variable/space-grotesk"
import "@fontsource/space-mono/400.css"
import "@fontsource/space-mono/700.css"
import "@fontsource-variable/ibm-plex-sans"
import "@fontsource/ibm-plex-mono/400.css"
import "@fontsource/ibm-plex-mono/500.css"
import "@fontsource-variable/manrope"
import "@fontsource-variable/source-serif-4"
import "@fontsource-variable/fraunces"
import "./index.css"
import App from "./App.tsx"
import { applyAppearance, loadAppearance } from "@/lib/appearance"

applyAppearance(loadAppearance())       // before the first paint: no flash of the default theme

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
