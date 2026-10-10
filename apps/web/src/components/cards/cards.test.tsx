/**
 * Tests for the cards on the simulated screen. The fixtures are real turns
 * recorded from the simulator (apps/simulator/tests/test_web_fixtures.py).
 */

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { TurnResult } from '../../api/types'
import openQuestions from '../../test/fixtures/open_questions.json'
import planForDay from '../../test/fixtures/plan_for_day.json'
import reminderProposal from '../../test/fixtures/reminder_proposal.json'
import visitUpdates from '../../test/fixtures/visit_updates.json'
import whatsChanged from '../../test/fixtures/whats_changed.json'
import { CardView } from './CardView'

function show(fixture: unknown, onAnswer = vi.fn()) {
  const turn = fixture as TurnResult
  if (!turn.card) {
    throw new Error('fixture has no card')
  }
  render(<CardView card={turn.card} pending={turn.pending ?? null} onAnswer={onAnswer} />)
  return onAnswer
}

describe('cards', () => {
  it('shows each new item with its exact quote and offers to add them', async () => {
    const onAnswer = show(visitUpdates)
    expect(screen.getByRole('heading', { name: 'New from Dr. Lee' })).toBeInTheDocument()
    expect(
      screen.getByText('a hold on Medication A starting Sunday, October 25'),
    ).toBeInTheDocument()
    expect(screen.getByText('hold Medication A starting Sunday, October 25')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Add to my care plan' }))
    expect(onAnswer).toHaveBeenCalledWith('yes')
  })

  it('marks a change that starts later, is temporary, and has no captured end', () => {
    show(whatsChanged)
    const change = screen.getByRole('article', { name: 'Medication A' })
    expect(within(change).getByText('Starts later')).toBeInTheDocument()
    expect(within(change).getByText('Temporary')).toBeInTheDocument()
    expect(within(change).getByText('End not captured')).toBeInTheDocument()
    expect(within(change).getByText('on hold')).toBeInTheDocument()
    expect(screen.getByText('1 question needs clarifying')).toBeInTheDocument()
  })

  it('reads the plan for a day with where each line came from', () => {
    show(planForDay)
    expect(screen.getByRole('heading', { name: /Your plan for/ })).toBeInTheDocument()
    expect(screen.getByText('on hold')).toBeInTheDocument()
    expect(screen.getAllByText('Dr. Lee').length).toBeGreaterThan(0)
  })

  it('shows open questions in full', () => {
    show(openQuestions)
    expect(
      screen.getByText('When should the temporary hold of Medication A for the procedure end?'),
    ).toBeInTheDocument()
  })

  it('shows the exact reminder text and asks before adding it', async () => {
    const onAnswer = show(reminderProposal)
    expect(
      screen.getByText(
        'Ask your care team: When should the temporary hold of Medication A for the procedure end?',
      ),
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(onAnswer).toHaveBeenCalledWith('no')
  })
})
