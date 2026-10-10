/** Open questions for the care team, in full (spec F7). */
import type { CardOf } from '../../api/types'
import { Slip } from './Slip'
import { SourceLine } from './SourceLine'

export function QuestionsSlip({ card }: { card: CardOf<'open_questions'> }) {
  const { data } = card
  if (data.questions.length === 0) {
    return null
  }
  return (
    <Slip tone="clarify" title="Needs clarifying">
      <ul className="mt-3 space-y-4">
        {data.questions.map((question) => (
          <li key={question.issue_id}>
            <p className="text-xl leading-snug font-semibold">{question.question}</p>
            <SourceLine source={question.source} />
          </li>
        ))}
      </ul>
    </Slip>
  )
}
