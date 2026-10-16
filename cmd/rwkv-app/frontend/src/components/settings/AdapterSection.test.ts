import { expect, it } from 'vitest'
import { suggestID } from './AdapterSection'

it('names an adapter after the training run directory, not the fixed file name', () => {
  expect(suggestID('/home/rwkv/train-2-0/r16-lr3e-5/adapter-final.pth')).toBe('r16-lr3e-5')
  expect(suggestID('/home/rwkv/train-2-0/r16-lr3e-5/checkpoint-134/training.pth')).toBe('r16-lr3e-5-checkpoint-134')
  expect(suggestID('C:\\miss\\my-adapter.pth')).toBe('my-adapter')
  expect(suggestID('')).toBe('')
})
