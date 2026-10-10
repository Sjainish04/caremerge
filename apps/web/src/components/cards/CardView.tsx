/** Chooses the slip for a turn's card; acknowledgements need no slip of their own. */
import type { Card, PendingView } from '../../api/types'
import { ChangesSlip } from './ChangesSlip'
import { PlanSlip } from './PlanSlip'
import { QuestionsSlip } from './QuestionsSlip'
import { ReminderSlip } from './ReminderSlip'
import { VisitUpdatesSlip } from './VisitUpdatesSlip'

export function CardView({
  card,
  pending,
  onAnswer,
}: {
  card: Card
  pending: PendingView | null
  onAnswer: (answer: 'yes' | 'no') => void
}) {
  switch (card.tool) {
    case 'visit_updates':
      return <VisitUpdatesSlip card={card} pending={pending} onAnswer={onAnswer} />
    case 'whats_changed':
      return <ChangesSlip card={card} />
    case 'plan_for_day':
      return <PlanSlip card={card} />
    case 'open_questions':
      return <QuestionsSlip card={card} />
    case 'propose_reminder':
      return card.data.reminder ? (
        <ReminderSlip reminder={card.data.reminder} pending={pending} onAnswer={onAnswer} />
      ) : null
    case 'confirm_reminder':
      return <ReminderSlip reminder={card.data.reminder} pending={null} onAnswer={onAnswer} />
    default:
      return null
  }
}
