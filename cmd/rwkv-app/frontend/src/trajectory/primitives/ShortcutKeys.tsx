/** Minimal shortcut-key chips for tooltips (stand-in for the DSH primitive). */
export function ShortcutKeys({ keys }: { keys: readonly string[]; variant?: string; className?: string }) {
  return <span style={{ marginLeft: 8, opacity: 0.7 }}>{keys.join(' ')}</span>
}
