/** New items from one visit, each with its quote, awaiting the user's yes (spec F3). */
import type { CardOf, PendingView } from '../../api/types'
import { longDate, roleLabel } from '../../format'
import { AnswerButtons } from './AnswerButtons'
import { Slip, Tag } from './Slip'
import { SourceLine } from './SourceLine'

export function VisitUpdatesSlip({
  card,
  pending,
  onAnswer,
}: {
  card: CardOf<'visit_updates'>
  pending: PendingView | null
  onAnswer: (answer: 'yes' | 'no') => void
}) {
  const { data } = card
  if (data.items.length === 0 || !data.clinician || !data.visit_date) {
    return null
  }
  const role = roleLabel(data.items[0].source.role)
  return (
    <Slip tone="info" title={`New from ${data.clinician}`} aside={`${role}, ${longDate(data.visit_date)}`}>
      <ul className="mt-3 space-y-4">
        {data.items.map((item) => (
          <li key={item.commit_id}>
            <p className="text-lg font-semibold">
              {item.summary}
              {item.temporary ? (
                <span className="ml-2 align-middle">
                  <Tag tone="info">Temporary</Tag>
                </span>
              ) : null}
            </p>
            <SourceLine source={item.source} />
          </li>
        ))}
      </ul>
      {pending?.tool === 'confirm_items' ? (
        <AnswerButtons yes="Add to my care plan" no="Not now" onAnswer={onAnswer} />
      ) : null}
    </Slip>
  )
}
