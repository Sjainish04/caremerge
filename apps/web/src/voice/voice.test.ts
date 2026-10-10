/** Tests for the browser voice: spoken replies, and where listening is offered. */

import { afterEach, describe, expect, it, vi } from 'vitest'
import { canListen, speak } from './voice'

class FakeUtterance {
  text: string
  onstart: (() => void) | null = null
  onend: (() => void) | null = null
  constructor(text: string) {
    this.text = text
  }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('voice', () => {
  it('speaks a reply after cancelling the previous one, and reports when it ends', () => {
    const spoken: FakeUtterance[] = []
    const synthesis = { cancel: vi.fn(), speak: vi.fn((u: FakeUtterance) => spoken.push(u)) }
    vi.stubGlobal('speechSynthesis', synthesis)
    vi.stubGlobal('SpeechSynthesisUtterance', FakeUtterance)
    const onEnd = vi.fn()
    speak('Added to your care plan.', { onEnd })
    expect(synthesis.cancel).toHaveBeenCalledOnce()
    expect(spoken.map((u) => u.text)).toEqual(['Added to your care plan.'])
    spoken[0].onend?.()
    expect(onEnd).toHaveBeenCalledOnce()
  })

  it('reports the end at once when the browser cannot speak', () => {
    vi.stubGlobal('speechSynthesis', undefined)
    const onEnd = vi.fn()
    speak('Hello.', { onEnd })
    expect(onEnd).toHaveBeenCalledOnce()
  })

  it('listens only where the browser offers speech recognition', () => {
    expect(canListen()).toBe(false)
    vi.stubGlobal('webkitSpeechRecognition', class {})
    expect(canListen()).toBe(true)
  })
})
