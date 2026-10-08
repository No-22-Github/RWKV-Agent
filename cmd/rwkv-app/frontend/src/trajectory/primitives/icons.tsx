/** DSH product icons mapped onto lucide glyphs. */
import {
  Check, ChevronRight, Code, Copy, Search, Settings, Sparkle, User, WrapText,
} from 'lucide-react'

export interface IconProps {
  size?: number
  className?: string
}

// DSH icons are 16px-grid strokes at 1px; lucide at strokeWidth 1.5 reads the same at 12–16px.
const icon = (Glyph: typeof Check) => ({ size = 16, className }: IconProps) => (
  <Glyph size={size} className={className} strokeWidth={1.5} aria-hidden="true" />
)

export const IconCheckOutlineRegular = icon(Check)
export const IconChevronRightOutlineRegular = icon(ChevronRight)
export const IconCodeOutlineRegular = icon(Code)
export const IconWrapLinesOutlineRegular = icon(WrapText)
export const IconCopyOutlineRegular = icon(Copy)
export const IconSettingsOutlineRegular = icon(Settings)
export const IconSparkleRegular = icon(Sparkle)
export const IconUserOutlineRegular = icon(User)
export const IconSearchOutlineRegular = icon(Search)

