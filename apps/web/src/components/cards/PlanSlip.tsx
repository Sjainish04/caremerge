/** The confirmed plan on one day, with where each line came from (spec F6). */
import type { CardOf } from '../../api/types'
import { dimensionLabel, shortDate } from '../../format'
import { Slip, Tag } from './Slip'
import { SourceLine } from './SourceLine'

export function PlanSlip({ card }: { card: CardOf<'plan_for_day'> }) {
  const { data } = card
  if (data.entries.length === 0) {
    return null
  }
  return (
    <Slip tone="info" title={`Your plan for ${shortDate(data.day)}`}>
      <dl className="mt-3 space-y-3">
        {data.entries.map((entry) => (
          <div key={`${entry.subject}-${entry.dimension}`}>
            <dt className="text-sm text-pencil">
              {entry.subject}, {dimensionLabel(entry.dimension).toLowerCase()}
            </dt>
            <dd className="flex flex-wrap items-center gap-2">
              <span className="text-lg font-semibold">{entry.values.join(' or ')}</span>
              {entry.temporary ? <Tag tone="info">Temporary</Tag> : null}
              {entry.temporary && !entry.end_captured ? <Tag tone="clarify">End not captured</Tag> : null}
            </dd>
            <dd>
              <SourceLine source={entry.source} quote={false} />
            </dd>
          </div>
        ))}
      </dl>
    </Slip>
  )
}
