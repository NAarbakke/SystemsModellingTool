import type { ReactNode } from "react"
import { DropdownMenu } from "radix-ui"
import { CheckIcon, PaletteIcon } from "lucide-react"

import { FONTS, THEME_FONT, THEMES, type Appearance } from "@/lib/appearance"

/* Header menu: site theme and font. Each font is previewed in itself, each theme by its colours. */
export function AppearanceMenu({ value, onChange }: { value: Appearance; onChange: (a: Appearance) => void }) {
  const theme = THEMES.find((t) => t.id === value.theme) ?? THEMES[0]
  const themeFont = FONTS.find((f) => f.id === theme.font)!

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        title="Theme and font"
        className="tabular flex h-7 cursor-pointer items-center gap-2 rounded-md border border-line px-2.5 text-[12px] text-fg-2 transition-colors outline-none hover:border-line-strong hover:text-fg data-[state=open]:border-line-strong data-[state=open]:text-fg"
      >
        <PaletteIcon className="size-3.5" />
        {theme.label}
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end" sideOffset={6}
          className="z-50 max-h-[var(--radix-dropdown-menu-content-available-height)] w-[300px] overflow-y-auto rounded-lg border border-line-strong bg-surface-2 p-1.5 text-fg shadow-2xl shadow-shadow"
        >
          <DropdownMenu.Label className="eyebrow px-2 pt-1.5 pb-2">Theme</DropdownMenu.Label>
          <DropdownMenu.RadioGroup value={value.theme} onValueChange={(theme) => onChange({ ...value, theme })}>
            {THEMES.map((t) => (
              <Item key={t.id} value={t.id}>
                <span className="flex overflow-hidden rounded-[5px] border border-line-strong">
                  {t.swatch.map((c, i) => <span key={i} className="h-5 w-3" style={{ background: c }} />)}
                </span>
                <span className="flex flex-col">
                  <span className="text-[13px]">{t.label}</span>
                  <span className="text-[11.5px] text-fg-3">{t.description}</span>
                </span>
              </Item>
            ))}
          </DropdownMenu.RadioGroup>

          <DropdownMenu.Separator className="my-1.5 h-px bg-line" />

          <DropdownMenu.Label className="eyebrow px-2 pt-1.5 pb-2">Font</DropdownMenu.Label>
          <DropdownMenu.RadioGroup value={value.font} onValueChange={(font) => onChange({ ...value, font })}>
            <Item value={THEME_FONT}>
              <span className="text-[13px]" style={{ fontFamily: themeFont.sans }}>
                Theme default <span className="text-fg-3">· {themeFont.label}</span>
              </span>
            </Item>
            {FONTS.map((f) => (
              <Item key={f.id} value={f.id}>
                <span className="flex w-full items-baseline justify-between gap-3">
                  <span className="text-[14px]" style={{ fontFamily: f.sans }}>{f.label}</span>
                  <span className="text-[11.5px] text-fg-3" style={{ fontFamily: f.mono }}>1,117 K</span>
                </span>
              </Item>
            ))}
          </DropdownMenu.RadioGroup>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}

function Item({ value, children }: { value: string; children: ReactNode }) {
  return (
    <DropdownMenu.RadioItem
      value={value}
      onSelect={(e) => e.preventDefault()}        // keep the menu open to compare choices
      className="flex cursor-pointer items-center gap-3 rounded-md py-1.5 pr-2 pl-7 outline-none relative data-[highlighted]:bg-surface data-[state=checked]:text-fg"
    >
      <DropdownMenu.ItemIndicator className="absolute left-2 text-heat">
        <CheckIcon className="size-3.5" />
      </DropdownMenu.ItemIndicator>
      {children}
    </DropdownMenu.RadioItem>
  )
}
