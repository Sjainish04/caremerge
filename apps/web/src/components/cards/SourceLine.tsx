/** The exact words an item came from, and who said them when (spec F4). */
import type { SourceInfo } from '../../api/types'
import { roleLabel, shortDate } from '../../format'

export function SourceLine({ source, quote = true }: { source: SourceInfo; quote?: boolean }) {
  return (
    <div className="mt-2 text-sm text-pencil">
      {quote ? (
        <q className="block border-l-2 border-pencil/25 pl-3 font-quote text-base italic text-ink/80">
          {source.quote}
        </q>
      ) : null}
      <p className="mt-1">
        <span className="font-semibold text-ink/80">{source.clinician}</span>
        <span>, {roleLabel(source.role).toLowerCase()}, {shortDate(source.date)}</span>
      </p>
    </div>
  )
}
