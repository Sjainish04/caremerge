/**
 * The two answers to a pending change; a tap is the same as saying yes or no.
 * They stick to the bottom of the screen so the choice stays in view.
 */
export function AnswerButtons({
  yes,
  no,
  onAnswer,
}: {
  yes: string
  no: string
  onAnswer: (answer: 'yes' | 'no') => void
}) {
  return (
    <div className="sticky bottom-0 mt-4 flex flex-wrap gap-3 bg-paper pt-3 pb-5">
      <button
        type="button"
        onClick={() => onAnswer('yes')}
        className="rounded-full bg-ink px-5 py-2 font-semibold text-paper hover:bg-ink-soft focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
      >
        {yes}
      </button>
      <button
        type="button"
        onClick={() => onAnswer('no')}
        className="rounded-full border border-ink/25 px-5 py-2 font-semibold text-ink hover:bg-ink/5 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-alexa"
      >
        {no}
      </button>
    </div>
  )
}
