/** What the user said, and Alexa's reply as captions (read aloud as well). */
export function SpeechLine({
  heard,
  speech,
  compact,
}: {
  heard: string | null
  speech: string | null
  compact: boolean
}) {
  return (
    <div className="max-w-[62ch]">
      {heard ? <p className="mb-2 text-paper/60">“{heard}”</p> : null}
      <p
        aria-live="polite"
        className={`${compact ? 'text-xl' : 'text-2xl'} leading-snug font-medium text-balance text-paper`}
      >
        {speech}
      </p>
    </div>
  )
}
