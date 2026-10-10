/** A reminder before and after the user's yes (spec F8). */
import type { PendingView, ReminderCard } from '../../api/types'
import { alarmTime } from '../../format'
import { AnswerButtons } from './AnswerButtons'
import { Slip } from './Slip'
import { SourceLine } from './SourceLine'

export function ReminderSlip({
  reminder,
  pending,
  onAnswer,
}: {
  reminder: ReminderCard
  pending: PendingView | null
  onAnswer: (answer: 'yes' | 'no') => void
}) {
  const stored = reminder.state === 'executed'
  return (
    <Slip tone={stored ? 'verified' : 'info'} title={stored ? 'Reminder added' : 'Add this reminder?'} aside={alarmTime(reminder.alarm_at)}>
      <p className="mt-3 text-xl leading-snug font-semibold">{reminder.text}</p>
      {reminder.based_on ? <SourceLine source={reminder.based_on} /> : null}
      {!stored && pending?.tool === 'confirm_reminder' ? (
        <AnswerButtons yes="Add reminder" no="Cancel" onAnswer={onAnswer} />
      ) : null}
    </Slip>
  )
}
