/**
 * Typed client for the simulator's local API (spec §11).
 *
 * It reads the per-launch token from `GET /api/session` and sends it as
 * `X-CareMerge-Token` on every later request. Every request gives up after its
 * timeout; adding a visit gets a longer one. Types come from the generated
 * OpenAPI schema, so a contract change fails the type check here.
 */
import createClient from 'openapi-fetch'
import type { paths } from './schema'
import type { HealthResponse, ReminderCard, TurnResult, VisitCard } from './types'

export const TOKEN_HEADER = 'X-CareMerge-Token'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number) {
    super(`The simulator answered with status ${status}.`)
    this.status = status
  }
}

export interface Timeouts {
  /** Milliseconds to wait for the host to answer a request. */
  readonly requestTimeoutMs: number
  /** Milliseconds to wait for the host to add a visit. */
  readonly intakeTimeoutMs: number
}

export interface SimulatorApi {
  connect(): Promise<void>
  health(): Promise<HealthResponse>
  say(text: string): Promise<TurnResult>
  confirm(pendingId: string, answer: 'yes' | 'no'): Promise<TurnResult>
  inbox(): Promise<VisitCard[]>
  addVisit(visitId: string): Promise<TurnResult>
  reminders(): Promise<ReminderCard[]>
  deleteData(): Promise<TurnResult>
}

function unwrap<T>(result: { data?: T; response: Response }): T {
  if (result.data === undefined) {
    throw new ApiError(result.response.status)
  }
  return result.data
}

export function createSimulatorApi(
  fetchImpl: typeof fetch,
  baseUrl: string,
  timeouts: Timeouts,
): SimulatorApi {
  let token = ''
  const client = createClient<paths>({ baseUrl, fetch: fetchImpl })
  client.use({
    onRequest({ request }) {
      if (token) {
        request.headers.set(TOKEN_HEADER, token)
      }
      return request
    },
  })
  const timed = () => ({ signal: AbortSignal.timeout(timeouts.requestTimeoutMs) })

  return {
    async connect() {
      token = unwrap(await client.GET('/api/session', timed())).token
    },
    async health() {
      return unwrap(await client.GET('/api/health', timed()))
    },
    async say(text) {
      return unwrap(await client.POST('/api/turn', { body: { text }, ...timed() }))
    },
    async confirm(pendingId, answer) {
      return unwrap(
        await client.POST('/api/confirmations/{pending_id}', {
          params: { path: { pending_id: pendingId } },
          body: { answer },
          ...timed(),
        }),
      )
    },
    async inbox() {
      return unwrap(await client.GET('/api/inbox', timed())).visits
    },
    async addVisit(visitId) {
      return unwrap(
        await client.POST('/api/inbox/{visit_id}', {
          params: { path: { visit_id: visitId } },
          signal: AbortSignal.timeout(timeouts.intakeTimeoutMs),
        }),
      )
    },
    async reminders() {
      return unwrap(await client.GET('/api/reminders', timed())).reminders
    },
    async deleteData() {
      return unwrap(await client.DELETE('/api/data', timed()))
    },
  }
}
