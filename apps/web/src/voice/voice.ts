/**
 * Browser voice for the simulator: speech synthesis for replies, speech
 * recognition for requests (spec §12.1).
 *
 * Recognition is Chrome's Web Speech API; elsewhere the text box is the way in.
 * Everything spoken is the host's template-rendered `speech`, unchanged.
 */

interface RecognitionResult {
  readonly isFinal: boolean
  readonly 0: { readonly transcript: string }
}

interface RecognitionEvent {
  readonly results: ArrayLike<RecognitionResult>
}

interface SpeechRecognitionLike {
  lang: string
  interimResults: boolean
  continuous: boolean
  onresult: ((event: RecognitionEvent) => void) | null
  onend: (() => void) | null
  onerror: (() => void) | null
  start(): void
  stop(): void
}

type RecognitionConstructor = new () => SpeechRecognitionLike

export interface Recognizer {
  start(): void
  stop(): void
}

function recognitionConstructor(): RecognitionConstructor | null {
  const scope = globalThis as unknown as {
    SpeechRecognition?: RecognitionConstructor
    webkitSpeechRecognition?: RecognitionConstructor
  }
  return scope.SpeechRecognition ?? scope.webkitSpeechRecognition ?? null
}

export function canListen(): boolean {
  return recognitionConstructor() !== null
}

export function createRecognizer(handlers: {
  onText: (text: string) => void
  onEnd: () => void
}): Recognizer | null {
  const Recognition = recognitionConstructor()
  if (Recognition === null) {
    return null
  }
  const recognition = new Recognition()
  recognition.lang = 'en-US'
  recognition.interimResults = false
  recognition.continuous = false
  recognition.onresult = (event) => {
    const text = Array.from(event.results)
      .filter((result) => result.isFinal)
      .map((result) => result[0].transcript)
      .join(' ')
      .trim()
    if (text) {
      handlers.onText(text)
    }
  }
  recognition.onend = handlers.onEnd
  recognition.onerror = handlers.onEnd
  return { start: () => recognition.start(), stop: () => recognition.stop() }
}

export function speak(text: string, handlers: { onStart?: () => void; onEnd?: () => void } = {}): void {
  const synthesis = (globalThis as { speechSynthesis?: SpeechSynthesis }).speechSynthesis
  if (!synthesis || !text) {
    handlers.onEnd?.()
    return
  }
  synthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.onstart = () => handlers.onStart?.()
  utterance.onend = () => handlers.onEnd?.()
  synthesis.speak(utterance)
}

export function stopSpeaking(): void {
  ;(globalThis as { speechSynthesis?: SpeechSynthesis }).speechSynthesis?.cancel()
}
