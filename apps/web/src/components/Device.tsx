/**
 * The simulated Echo Show: a fabric bezel, a screen with the clock and the
 * connection, and Alexa's light bar along the bottom edge.
 */
import { useEffect, useState, type ReactNode } from 'react'
import { clockTime } from '../format'
import type { Activity, Connection } from '../state/useSimulator'

const CONNECTION_TEXT: Record<Connection, string> = {
  connecting: 'Connecting to CareMerge',
  online: 'Connected to CareMerge',
  offline: 'CareMerge is not reachable. Start the simulator host and reload.',
}

function useClock(): Date {
  const [now, setNow] = useState(() => new Date())
  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 15_000)
    return () => window.clearInterval(timer)
  }, [])
  return now
}

export function Device({
  connection,
  activity,
  children,
}: {
  connection: Connection
  activity: Activity
  children: ReactNode
}) {
  const now = useClock()
  return (
    <div className="rounded-[2.75rem] bg-bezel p-4 shadow-[0_30px_60px_-30px_rgba(27,42,65,0.65)] sm:p-5">
      <div className="relative flex h-[min(64vh,38rem)] flex-col overflow-hidden rounded-[1.75rem] bg-ink text-paper">
        <header className="flex items-center justify-between px-6 pt-5 text-sm text-paper/70">
          <span className="font-semibold tracking-tight text-paper/90">CareMerge</span>
          <span className="flex items-center gap-3">
            <span className="flex items-center gap-2">
              <span
                aria-hidden="true"
                className={`size-2 rounded-full ${connection === 'online' ? 'bg-verified' : connection === 'offline' ? 'bg-highlighter' : 'bg-paper/40'}`}
              />
              <span className={connection === 'offline' ? 'text-highlighter' : undefined}>
                {CONNECTION_TEXT[connection]}
              </span>
            </span>
            <time dateTime={now.toISOString()} className="tabular-nums text-paper/90">
              {clockTime(now)}
            </time>
          </span>
        </header>
        <div className="flex-1 overflow-y-auto px-6 pt-4">
          {children}
          <div aria-hidden="true" className="h-8" />
        </div>
        <div aria-hidden="true" className={`light-bar light-bar--${activity}`} />
      </div>
    </div>
  )
}
