/** Tests for the simulator API client: the session token, refused requests, and timeouts. */

import { describe, expect, it } from 'vitest'
import visitAdded from '../test/fixtures/visit_added.json'
import whatsChanged from '../test/fixtures/whats_changed.json'
import { ApiError, TOKEN_HEADER, createSimulatorApi, type Timeouts } from './client'

const TIMEOUTS: Timeouts = { requestTimeoutMs: 1000, intakeTimeoutMs: 1000 }

function respond(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

/** A host that answers after `delayMs`, unless the request is aborted first. */
function answerAfter(delayMs: number, body: unknown) {
  return (request: Request) =>
    new Promise<Response>((resolve, reject) => {
      const timer = setTimeout(() => resolve(respond(body)), delayMs)
      request.signal.addEventListener('abort', () => {
        clearTimeout(timer)
        reject(request.signal.reason)
      })
    })
}

describe('simulator API client', () => {
  it('sends the session token on every request after connecting', async () => {
    const seen: Request[] = []
    const fakeFetch = async (request: Request) => {
      seen.push(request.clone())
      return new URL(request.url).pathname === '/api/session'
        ? respond({ token: 'launch-token' })
        : respond(whatsChanged)
    }
    const api = createSimulatorApi(fakeFetch as typeof fetch, 'http://localhost', TIMEOUTS)
    await api.connect()
    const turn = await api.say('What changed in my care plan?')
    expect(turn.speech).toBe(whatsChanged.speech)
    expect(seen[0].headers.get(TOKEN_HEADER)).toBeNull()
    expect(seen[1].headers.get(TOKEN_HEADER)).toBe('launch-token')
    expect(await seen[1].json()).toEqual({ text: 'What changed in my care plan?' })
  })

  it('rejects with the status when the host refuses', async () => {
    const fakeFetch = async () => respond({ detail: 'nothing is waiting for that' }, 409)
    const api = createSimulatorApi(fakeFetch as typeof fetch, 'http://localhost', TIMEOUTS)
    await expect(api.confirm('pend_404', 'yes')).rejects.toEqual(new ApiError(409))
  })

  it('gives up on a request the host takes too long to answer', async () => {
    const slowHost = answerAfter(200, whatsChanged)
    const api = createSimulatorApi(slowHost as typeof fetch, 'http://localhost', {
      requestTimeoutMs: 10,
      intakeTimeoutMs: 1000,
    })
    await expect(api.say('What changed in my care plan?')).rejects.toMatchObject({
      name: 'TimeoutError',
    })
  })

  it('waits longer for a visit to be added, since the host compiles it first', async () => {
    const slowHost = answerAfter(50, visitAdded)
    const api = createSimulatorApi(slowHost as typeof fetch, 'http://localhost', {
      requestTimeoutMs: 10,
      intakeTimeoutMs: 1000,
    })
    expect((await api.addVisit('visit-2')).speech).toBe(visitAdded.speech)
  })
})
