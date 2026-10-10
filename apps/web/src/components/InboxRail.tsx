/** The visit inbox: synthetic visits the user can add for CareMerge to read (spec F1). */
import type { VisitCard } from '../api/types'
import { roleLabel, shortDate } from '../format'

export function InboxRail({
  visits,
  busy,
  onAdd,
}: {
  visits: VisitCard[]
  busy: boolean
  onAdd: (visitId: string) => void
}) {
  return (
    <aside aria-labelledby="inbox-title" className="space-y-3">
      <div>
        <h2 id="inbox-title" className="text-lg font-semibold">
          Visit inbox
        </h2>
        <p className="text-sm text-pencil">Synthetic visit transcripts. Add one and CareMerge reads it.</p>
      </div>
      <ul className="space-y-2">
        {visits.map((visit) => (
          <li key={visit.visit_id} className="rounded-xl bg-white/70 p-3">
            <p className="font-semibold">{visit.clinician}</p>
            <p className="text-sm text-pencil">
              {roleLabel(visit.role)}, {shortDate(visit.date)}
            </p>
            {visit.added ? (
              <p className="mt-2 text-sm font-semibold text-verified">Added</p>
            ) : (
              <button
                type="button"
                disabled={busy}
                onClick={() => onAdd(visit.visit_id)}
                className="mt-2 rounded-full border border-ink/20 px-3 py-1 text-sm font-semibold hover:bg-ink/5 disabled:opacity-40 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
              >
                Add visit
              </button>
            )}
          </li>
        ))}
      </ul>
    </aside>
  )
}
