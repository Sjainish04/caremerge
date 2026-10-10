/** Tests for the talk bar: typed requests, suggested requests, and the microphone. */

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TalkBar } from './TalkBar'

const SUGGESTIONS = ['What changed in my care plan?', 'Should I take Medication A on Sunday?']

function renderBar(overrides: Partial<Parameters<typeof TalkBar>[0]> = {}) {
  const props = {
    onSay: vi.fn(),
    onListen: vi.fn(),
    busy: false,
    listening: false,
    canListen: false,
    suggestions: SUGGESTIONS,
    ...overrides,
  }
  render(<TalkBar {...props} />)
  return props
}

describe('TalkBar', () => {
  it('sends a typed request and clears the box', async () => {
    const { onSay } = renderBar()
    const box = screen.getByRole('textbox', { name: 'Ask about your care plan' })
    await userEvent.type(box, 'What changed?')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))
    expect(onSay).toHaveBeenCalledWith('What changed?')
    expect(box).toHaveValue('')
  })

  it('sends a suggested request with one tap', async () => {
    const { onSay } = renderBar()
    await userEvent.click(screen.getByRole('button', { name: SUGGESTIONS[1] }))
    expect(onSay).toHaveBeenCalledWith(SUGGESTIONS[1])
  })

  it('offers the microphone only where the browser can listen', async () => {
    renderBar()
    expect(screen.queryByRole('button', { name: 'Talk' })).not.toBeInTheDocument()
    const { onListen } = renderBar({ canListen: true })
    await userEvent.click(screen.getByRole('button', { name: 'Talk' }))
    expect(onListen).toHaveBeenCalledWith(true)
  })
})
