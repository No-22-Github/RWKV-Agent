import { describe, expect, it } from 'vitest'
import { metaStats, shortRunName } from './runNames'

describe('shortRunName', () => {
  it('keeps the part that tells models apart', () => {
    expect(shortRunName('rwkv7-g1k-7.2b-20260930-ctx25600')).toBe('g1k-7.2b-20260930-…')
    expect(shortRunName('v141b-s1224.pth')).toBe('v141b-s1224')
    expect(shortRunName('/models/rwkv7-g1k-13.3b.pth')).toBe('g1k-13.3b')
  })
})

describe('metaStats', () => {
  it('keeps only the step count and duration', () => {
    expect(metaStats('2 步 · 9.2 秒 · rwkv7-g1k-7.2b-20260930-ctx25600 · MiSS rwkv7-g1k-7b-r16-lr3e-5-e2-miss · v141b-s1224.pth'))
      .toEqual(['2 步', '9.2 秒'])
    expect(metaStats(undefined)).toEqual([])
  })
})
