/** What changed since the last visit: before and after, with their markers (spec F5). */
import type { CardOf, ChangeCard, SegmentCard } from '../../api/types'
import { dayBefore, dimensionLabel, shortDate } from '../../format'
import { Slip, Tag } from './Slip'
import { SourceLine } from './SourceLine'

function SegmentLine({ segment, last }: { segment: SegmentCard; last: boolean }) {
  return (
    <p className="flex flex-wrap items-center gap-2">
      <span className="text-lg font-semibold">{segment.values.join(' or ')}</span>
      {!last ? <span className="text-pencil">until {shortDate(dayBefore(segment.end))}</span> : null}
      {segment.temporary ? <Tag tone="info">Temporary</Tag> : null}
      {segment.temporary && !segment.end_captured ? <Tag tone="clarify">End not captured</Tag> : null}
    </p>
  )
}

function Change({ change }: { change: ChangeCard }) {
  const label = change.dimension === 'action' ? change.subject : `${change.subject}, ${dimensionLabel(change.dimension).toLowerCase()}`
  return (
    <article aria-label={change.subject} className="border-t border-ink/10 pt-3 first:border-t-0 first:pt-0">
      <header className="flex flex-wrap items-center gap-2">
        <h3 className="text-base font-semibold text-pencil">{label}</h3>
        {change.change === 'added' ? <Tag tone="quiet">New</Tag> : null}
        {change.future_effective ? <Tag tone="info">Starts later</Tag> : null}
      </header>
      {change.before.length > 0 ? (
        <p className="mt-1 text-pencil">
          Was <s className="decoration-superseded">{change.before[0].values.join(' or ')}</s>
        </p>
      ) : null}
      <div className="mt-1 space-y-1">
        {change.after.map((segment, index) => (
          <div key={segment.start} className="flex items-baseline gap-2">
            {change.after.length > 1 ? (
              <span className="w-28 shrink-0 text-sm whitespace-nowrap text-pencil">
                {index === 0 ? 'Now' : `from ${shortDate(segment.start)}`}
              </span>
            ) : null}
            <SegmentLine segment={segment} last={index === change.after.length - 1} />
          </div>
        ))}
      </div>
      {change.sources.slice(-1).map((source) => (
        <SourceLine key={source.quote} source={source} />
      ))}
    </article>
  )
}

export function ChangesSlip({ card }: { card: CardOf<'whats_changed'> }) {
  const { data } = card
  if (data.changes.length === 0) {
    return null
  }
  return (
    <Slip tone={data.open_questions > 0 ? 'clarify' : 'info'} title="What changed since your last visit">
      <div className="mt-3 space-y-4">
        {data.changes.map((change) => (
          <Change key={`${change.subject}-${change.dimension}`} change={change} />
        ))}
      </div>
      {data.open_questions > 0 ? (
        <p className="mt-4 inline-block rounded bg-highlighter/30 px-2 py-1 font-semibold">
          {data.open_questions} {data.open_questions === 1 ? 'question needs' : 'questions need'} clarifying
        </p>
      ) : null}
    </Slip>
  )
}
