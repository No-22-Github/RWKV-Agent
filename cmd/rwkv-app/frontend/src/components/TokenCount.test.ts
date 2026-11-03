import { expect, it } from 'vitest'
import { formatTokens } from './TokenCount'

it.each([[0, '0'], [999, '999'], [1000, '1k'], [1099, '1k'], [1100, '1.1k'], [1280, '1.2k'], [12345, '12.3k'], [20000, '20k']])('formats %i tokens as %s', (count, text) => {
  expect(formatTokens(count)).toBe(text)
})
