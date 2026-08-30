/** 台账的简化虚拟滚动：前缀和 + 400px overscan，行高为估算值。 */

export type VirtualWindow = {
  start: number
  end: number
  padTop: number
  padBottom: number
}

export type RowEstimate = (index: number) => number

export function prefixOffsets(rowCount: number, estimate: RowEstimate): number[] {
  const offsets = new Array<number>(rowCount + 1)
  offsets[0] = 0
  for (let index = 0; index < rowCount; index++) offsets[index + 1] = offsets[index] + estimate(index)
  return offsets
}

function lowerBound(offsets: readonly number[], target: number): number {
  let low = 0
  let high = offsets.length - 1
  while (low < high) {
    const mid = (low + high) >> 1
    if (offsets[mid] < target) low = mid + 1
    else high = mid
  }
  return low
}

export function virtualWindow(
  rowCount: number,
  offsets: readonly number[],
  scrollTop: number,
  viewportHeight: number,
  padPx = 400,
): VirtualWindow {
  if (rowCount === 0) return { start: 0, end: 0, padTop: 0, padBottom: 0 }
  const start = Math.max(0, lowerBound(offsets, Math.max(0, scrollTop - padPx)) - 1)
  const rawEnd = lowerBound(offsets, scrollTop + viewportHeight + padPx)
  const end = Math.min(rowCount, rawEnd + 1)
  return {
    start,
    end,
    padTop: offsets[start],
    padBottom: offsets[rowCount] - offsets[end],
  }
}

/** 行数低于阈值时直接全量渲染，规避测试与短台账的窗口边界问题。 */
export const VIRTUALIZE_THRESHOLD = 120
