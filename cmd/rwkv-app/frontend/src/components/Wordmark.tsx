// R▮WKV 点阵字标：R 是已输入，▮ 是光标，WKV 是灰色补全提示。
// 1 = 已输入，2 = 光标，3 = 补全；每个字形 5×7（光标 2×7），字间空一列。
const GLYPHS: Record<string, string[]> = {
  R: ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
  C: ['22', '22', '22', '22', '22', '22', '22'],
  W: ['10001', '10001', '10001', '10101', '10101', '10101', '01010'],
  K: ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
  V: ['10001', '10001', '10001', '10001', '01010', '01010', '00100'],
}
const SEQUENCE: [string, string][] = [['R', '1'], ['C', '2'], ['W', '3'], ['K', '3'], ['V', '3']]
const SIZE = 0.86
const ROWS = GLYPHS.R.map((_, y) => SEQUENCE.map(([glyph, kind]) => GLYPHS[glyph][y].replace(/[12]/g, kind)).join('0'))
const CELLS = ROWS.flatMap((row, y) => [...row].flatMap((kind, x) => (kind === '0' ? [] : [{ x, y, kind }])))
const WIDTH = ROWS[0].length - (1 - SIZE)
const HEIGHT = ROWS.length - (1 - SIZE)

/** 颜色跟随 color（已输入与光标），补全用 --ink-ghost；光标 530ms 闪烁，减少动态效果时常亮。 */
export default function Wordmark({ className, height = 16 }: { className?: string; height?: number }) {
  return <svg role="img" aria-label="RWKV" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} height={height} width={(height * WIDTH) / HEIGHT} className={`flex-none ${className || ''}`}>
    {CELLS.map(({ x, y, kind }) => <rect key={`${x}-${y}`} x={x} y={y} width={SIZE} height={SIZE} rx={SIZE * 0.22} className={kind === '2' ? 'animate-wordmark-blink motion-reduce:animate-none fill-current' : kind === '3' ? 'fill-ink-ghost' : 'fill-current'} />)}
  </svg>
}
