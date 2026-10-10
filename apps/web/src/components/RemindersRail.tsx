/** Reminders the user added, and the way to delete everything (spec F8, §10.2). */
import { useState } from 'react'
import type { ReminderCard } from '../api/types'
import { alarmTime } from '../format'

export function RemindersRail({
  reminders,
  busy,
  onDelete,
}: {
  reminders: ReminderCard[]
  busy: boolean
  onDelete: () => void
}) {
  const [confirming, setConfirming] = useState(false)
  return (
    <aside aria-labelledby="reminders-title" className="flex flex-col gap-3">
      <h2 id="reminders-title" className="text-lg font-semibold">
        Reminders
      </h2>
      {reminders.length === 0 ? (
        <p className="text-sm text-pencil">No reminders yet. Ask Alexa to remind you to ask your care team.</p>
      ) : (
        <ul className="space-y-2">
          {reminders.map((reminder) => (
            <li key={reminder.action_id} className="rounded-xl bg-white/70 p-3">
              <p className="text-sm font-semibold text-pencil">{alarmTime(reminder.alarm_at)}</p>
              <p className="mt-1">{reminder.text}</p>
            </li>
          ))}
        </ul>
      )}
      <div className="mt-6 border-t border-ink/10 pt-4 text-sm">
        {confirming ? (
          <div className="space-y-2">
            <p>Delete every visit, item, question, and reminder in CareMerge?</p>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={busy}
                onClick={() => {
                  setConfirming(false)
                  onDelete()
                }}
                className="rounded-full bg-ink px-3 py-1 font-semibold text-paper focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
              >
                Delete my data
              </button>
              <button
                type="button"
                onClick={() => setConfirming(false)}
                className="rounded-full border border-ink/20 px-3 py-1 font-semibold focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
              >
                Keep it
              </button>
            </div>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setConfirming(true)}
            className="text-pencil underline underline-offset-4 hover:text-ink focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
          >
            Delete my CareMerge data
          </button>
        )}
      </div>
    </aside>
  )
}
