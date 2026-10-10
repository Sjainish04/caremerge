/** How the user talks to the simulated Alexa: microphone, text box, or a suggested request. */
import { useState, type FormEvent } from 'react'

export function TalkBar({
  onSay,
  onListen,
  busy,
  listening,
  canListen,
  suggestions,
}: {
  onSay: (text: string) => void
  onListen: (listening: boolean) => void
  busy: boolean
  listening: boolean
  canListen: boolean
  suggestions: readonly string[]
}) {
  const [text, setText] = useState('')

  function submit(event: FormEvent) {
    event.preventDefault()
    const said = text.trim()
    if (said) {
      onSay(said)
      setText('')
    }
  }

  return (
    <div className="mt-5 space-y-3">
      <form onSubmit={submit} className="flex items-center gap-3">
        {canListen ? (
          <button
            type="button"
            aria-pressed={listening}
            onClick={() => onListen(!listening)}
            disabled={busy && !listening}
            className="grid size-14 shrink-0 place-items-center rounded-full bg-ink text-paper shadow-md transition-colors hover:bg-ink-soft disabled:opacity-50 aria-pressed:bg-alexa aria-pressed:text-ink focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
          >
            <span className="sr-only">{listening ? 'Stop listening' : 'Talk'}</span>
            <svg aria-hidden="true" viewBox="0 0 24 24" className="size-6 fill-current">
              <path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3Zm5-3a1 1 0 1 1 2 0 7 7 0 0 1-6 6.93V21h3a1 1 0 1 1 0 2H8a1 1 0 1 1 0-2h3v-2.07A7 7 0 0 1 5 12a1 1 0 1 1 2 0 5 5 0 0 0 10 0Z" />
            </svg>
          </button>
        ) : null}
        <label className="sr-only" htmlFor="request">
          Ask about your care plan
        </label>
        <input
          id="request"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder={canListen ? 'Or type what you would say' : 'Type what you would say to Alexa'}
          maxLength={500}
          autoComplete="off"
          className="min-w-0 flex-1 rounded-full border border-ink/15 bg-white px-5 py-3 text-lg text-ink placeholder:text-pencil/70 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
        />
        <button
          type="submit"
          disabled={busy || !text.trim()}
          className="rounded-full bg-ink px-6 py-3 text-lg font-semibold text-paper hover:bg-ink-soft disabled:opacity-40 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
        >
          Send
        </button>
      </form>
      <ul className="flex flex-wrap gap-2" aria-label="Things you can ask">
        {suggestions.map((suggestion) => (
          <li key={suggestion}>
            <button
              type="button"
              onClick={() => onSay(suggestion)}
              disabled={busy}
              className="rounded-full border border-ink/15 bg-white/70 px-4 py-1.5 text-sm text-ink hover:border-ink/40 disabled:opacity-40 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
            >
              {suggestion}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
