/**
 * The simulator's state: connection, what the device is doing, the last turn,
 * and the inbox and reminders it shows beside the device.
 *
 * Every reply is spoken exactly as the host returned it; the light bar
 * follows the activity (listening, thinking, speaking).
 */
import { useCallback, useEffect, useState } from 'react'
import { ApiError, type SimulatorApi } from '../api/client'
import type { ReminderCard, TurnResult, VisitCard } from '../api/types'
import { speak, stopSpeaking } from '../voice/voice'

export type Connection = 'connecting' | 'online' | 'offline'
export type Activity = 'idle' | 'listening' | 'thinking' | 'speaking'

export interface SimulatorState {
  connection: Connection
  activity: Activity
  heard: string | null
  turn: TurnResult | null
  inbox: VisitCard[]
  reminders: ReminderCard[]
}

const INITIAL: SimulatorState = {
  connection: 'connecting',
  activity: 'idle',
  heard: null,
  turn: null,
  inbox: [],
  reminders: [],
}

export function useSimulator(api: SimulatorApi) {
  const [state, setState] = useState<SimulatorState>(INITIAL)
  const patch = useCallback((update: Partial<SimulatorState>) => {
    setState((current) => ({ ...current, ...update }))
  }, [])

  const refresh = useCallback(async () => {
    const [inbox, reminders] = await Promise.all([api.inbox(), api.reminders()])
    patch({ inbox, reminders })
  }, [api, patch])

  useEffect(() => {
    let active = true
    api
      .connect()
      .then(refresh)
      .then(() => active && patch({ connection: 'online' }))
      .catch(() => active && patch({ connection: 'offline' }))
    return () => {
      active = false
    }
  }, [api, refresh, patch])

  const run = useCallback(
    async (heard: string | null, request: () => Promise<TurnResult>) => {
      stopSpeaking()
      patch({ heard, activity: 'thinking' })
      try {
        const turn = await request()
        patch({ turn, activity: 'speaking', connection: 'online' })
        speak(turn.speech, { onEnd: () => patch({ activity: 'idle' }) })
        await refresh()
      } catch (error) {
        const stale = error instanceof ApiError && error.status === 409
        patch(stale ? { activity: 'idle', turn: null } : { activity: 'idle', connection: 'offline' })
      }
    },
    [patch, refresh],
  )

  const pending = state.turn?.pending ?? null

  return {
    state,
    say: (text: string) => run(text, () => api.say(text)),
    answer: (answer: 'yes' | 'no') =>
      pending ? run(null, () => api.confirm(pending.pending_id, answer)) : Promise.resolve(),
    addVisit: (visitId: string) => run(null, () => api.addVisit(visitId)),
    deleteData: () => run(null, () => api.deleteData()),
    setListening: (listening: boolean) => patch({ activity: listening ? 'listening' : 'idle' }),
  }
}
