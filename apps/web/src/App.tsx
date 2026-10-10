/**
 * The Alexa+ simulator page: the visit inbox, the simulated Echo Show, and the
 * reminders it creates. It stands in for Amazon's Alexa+ while CareMerge runs
 * as a real MCP add-on behind the simulator host (spec §6).
 */
import { useEffect, useRef } from 'react'
import type { SimulatorApi } from './api/client'
import { CardView } from './components/cards/CardView'
import { Device } from './components/Device'
import { InboxRail } from './components/InboxRail'
import { RemindersRail } from './components/RemindersRail'
import { SpeechLine } from './components/SpeechLine'
import { TalkBar } from './components/TalkBar'
import { useSimulator } from './state/useSimulator'
import { canListen, createRecognizer, type Recognizer } from './voice/voice'

const SUGGESTIONS = [
  "What's new from my visit with Dr. Lee?",
  'What changed in my care plan?',
  'Should I take Medication A on Sunday, October 25?',
  'Remind me to ask when the hold ends.',
] as const

export default function App({ api }: { api: SimulatorApi }) {
  const simulator = useSimulator(api)
  const { state } = simulator
  const busy = state.activity === 'thinking'

  const latest = useRef(simulator)
  useEffect(() => {
    latest.current = simulator
  })
  const recognizerRef = useRef<Recognizer | null>(null)

  function listen(on: boolean) {
    recognizerRef.current ??= createRecognizer({
      onText: (text) => void latest.current.say(text),
      onEnd: () => latest.current.setListening(false),
    })
    const recognizer = recognizerRef.current
    if (!recognizer) {
      return
    }
    simulator.setListening(on)
    if (on) {
      recognizer.start()
    } else {
      recognizer.stop()
    }
  }

  const turn = state.turn
  return (
    <div className="min-h-dvh">
      <main className="mx-auto grid max-w-[90rem] gap-8 px-4 py-6 sm:px-6 lg:grid-cols-[15rem_minmax(0,1fr)_15rem] lg:py-10">
        <div className="lg:order-2">
          <p className="mb-3 text-sm text-pencil">
            A simulated Alexa+ screen. CareMerge answers from a real MCP add-on.
          </p>
          <Device connection={state.connection} activity={state.activity}>
            {turn ? (
              <div className="space-y-5">
                <SpeechLine heard={state.heard} speech={turn.speech} compact={turn.card !== null && turn.card !== undefined} />
                {turn.card ? (
                  <CardView card={turn.card} pending={turn.pending ?? null} onAnswer={(answer) => void simulator.answer(answer)} />
                ) : null}
              </div>
            ) : (
              <div className="max-w-[56ch] pt-10">
                <p className="text-3xl leading-tight font-semibold text-balance">
                  Ask about your care plan.
                </p>
                <p className="mt-3 text-lg text-paper/70">
                  Add a visit from the inbox, then ask what's new from it. CareMerge answers only from what
                  your care team said, and changes nothing until you say yes.
                </p>
              </div>
            )}
          </Device>
          <TalkBar
            onSay={(text) => void simulator.say(text)}
            onListen={listen}
            busy={busy}
            listening={state.activity === 'listening'}
            canListen={canListen()}
            suggestions={SUGGESTIONS}
          />
        </div>
        <div className="lg:order-1">
          <InboxRail visits={state.inbox} busy={busy} onAdd={(visitId) => void simulator.addVisit(visitId)} />
        </div>
        <div className="lg:order-3">
          <RemindersRail reminders={state.reminders} busy={busy} onDelete={() => void simulator.deleteData()} />
        </div>
      </main>
    </div>
  )
}
