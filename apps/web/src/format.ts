/** Display formatting for dates, times, roles, and plan dimensions. */
import type { SourceInfo } from './api/types'

const CALENDAR_DAY = new Intl.DateTimeFormat('en-US', {
  weekday: 'short',
  month: 'short',
  day: 'numeric',
  timeZone: 'UTC',
})
const LONG_DAY = new Intl.DateTimeFormat('en-US', {
  weekday: 'long',
  month: 'long',
  day: 'numeric',
  timeZone: 'UTC',
})
const ALARM = new Intl.DateTimeFormat('en-US', {
  weekday: 'short',
  month: 'short',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
})
const CLOCK = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' })

const ROLES: Record<SourceInfo['role'], string> = {
  family_physician: 'Family physician',
  specialist: 'Specialist',
  pharmacist: 'Pharmacist',
  nurse: 'Nurse',
  other_clinician: 'Clinician',
  self: 'You',
}

const DIMENSIONS: Record<string, string> = {
  action: 'Status',
  dose: 'Dose',
  time_of_day: 'Timing',
  food_relation: 'Food',
  days_of_week: 'Days',
  scheduled_for: 'Date',
  interval: 'Follow-up',
}

/** A calendar date like `Sun, Oct 25`; the date is never shifted by time zone. */
export function shortDate(isoDate: string): string {
  return CALENDAR_DAY.format(new Date(`${isoDate}T00:00:00Z`))
}

/** A calendar date like `Wednesday, October 7`. */
export function longDate(isoDate: string): string {
  return LONG_DAY.format(new Date(`${isoDate}T00:00:00Z`))
}

/** The day before `isoDate`, for showing an exclusive end as an inclusive one. */
export function dayBefore(isoDate: string): string {
  const day = new Date(`${isoDate}T00:00:00Z`)
  day.setUTCDate(day.getUTCDate() - 1)
  return day.toISOString().slice(0, 10)
}

/** An alarm time in the viewer's time zone, like `Tue, Oct 20, 10:00 AM`. */
export function alarmTime(isoDateTime: string): string {
  return ALARM.format(new Date(isoDateTime))
}

/** The time of day for the device header, like `10:02 AM`. */
export function clockTime(moment: Date): string {
  return CLOCK.format(moment)
}

export function roleLabel(role: SourceInfo['role']): string {
  return ROLES[role]
}

export function dimensionLabel(dimension: string): string {
  return DIMENSIONS[dimension] ?? dimension
}
