/** A paper slip on the device screen; its tab color says what state it is in. */
import type { ReactNode } from 'react'

export type Tone = 'info' | 'verified' | 'clarify'

const TABS: Record<Tone, string> = {
  info: 'bg-sky',
  verified: 'bg-verified',
  clarify: 'bg-highlighter',
}

export function Slip({
  tone,
  title,
  aside,
  children,
}: {
  tone: Tone
  title: string
  aside?: string
  children: ReactNode
}) {
  return (
    <section className="slip relative rounded-r-lg rounded-l-sm bg-paper pl-5 text-ink shadow-[0_1px_0_rgba(27,42,65,0.08),0_12px_28px_-18px_rgba(0,0,0,0.6)]">
      <span aria-hidden="true" className={`absolute inset-y-0 left-0 w-1.5 rounded-l-sm ${TABS[tone]}`} />
      <header className="flex items-baseline justify-between gap-4 pt-4 pr-5">
        <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
        {aside ? <p className="text-sm text-pencil">{aside}</p> : null}
      </header>
      <div className="pb-4 pr-5">{children}</div>
    </section>
  )
}

export function Tag({ tone, children }: { tone: 'info' | 'clarify' | 'quiet'; children: ReactNode }) {
  const styles = {
    info: 'border-sky/40 text-sky-deep',
    clarify: 'border-highlighter bg-highlighter/25 text-ink',
    quiet: 'border-pencil/30 text-pencil',
  }
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold ${styles[tone]}`}>
      {children}
    </span>
  )
}
