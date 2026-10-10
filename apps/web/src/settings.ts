/**
 * Settings for the simulator UI (spec §14), from `VITE_CAREMERGE_*` variables
 * in the repository's `.env` or the environment at build time. No other module
 * hard-codes them.
 *
 * The defaults wait a little longer than the simulator host waits for the
 * add-on (`CAREMERGE_ADDON_TIMEOUT_S`, `CAREMERGE_ADDON_INTAKE_TIMEOUT_S`), so
 * the host's own error arrives first.
 */

export interface Settings {
  /** How long to wait for the host to answer a request. */
  readonly requestTimeoutMs: number
  /** How long to wait for the host to add a visit; it compiles the visit first. */
  readonly intakeTimeoutMs: number
}

const DEFAULTS: Settings = { requestTimeoutMs: 15_000, intakeTimeoutMs: 100_000 }

export function loadSettings(env: Readonly<Record<string, unknown>>): Settings {
  return {
    requestTimeoutMs: milliseconds(env, 'VITE_CAREMERGE_REQUEST_TIMEOUT_MS', DEFAULTS.requestTimeoutMs),
    intakeTimeoutMs: milliseconds(env, 'VITE_CAREMERGE_INTAKE_TIMEOUT_MS', DEFAULTS.intakeTimeoutMs),
  }
}

function milliseconds(env: Readonly<Record<string, unknown>>, name: string, fallback: number): number {
  const value = env[name]
  if (value === undefined || value === '') {
    return fallback
  }
  const parsed = typeof value === 'string' ? Number(value) : Number.NaN
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new Error(`${name} must be a positive number of milliseconds.`)
  }
  return parsed
}
