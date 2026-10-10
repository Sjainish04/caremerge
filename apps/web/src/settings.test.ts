/** Tests for the UI's settings: defaults, values from the environment, and bad values. */

import { describe, expect, it } from 'vitest'
import { loadSettings } from './settings'

describe('settings', () => {
  it('waits a little longer than the host for each request by default', () => {
    expect(loadSettings({})).toEqual({ requestTimeoutMs: 15_000, intakeTimeoutMs: 100_000 })
  })

  it('reads the timeouts from the environment', () => {
    const env = {
      VITE_CAREMERGE_REQUEST_TIMEOUT_MS: '5000',
      VITE_CAREMERGE_INTAKE_TIMEOUT_MS: '60000',
    }
    expect(loadSettings(env)).toEqual({ requestTimeoutMs: 5000, intakeTimeoutMs: 60_000 })
  })

  it('names the setting when a timeout is not a positive number', () => {
    expect(() => loadSettings({ VITE_CAREMERGE_REQUEST_TIMEOUT_MS: 'soon' })).toThrow(
      'VITE_CAREMERGE_REQUEST_TIMEOUT_MS must be a positive number of milliseconds.',
    )
    expect(() => loadSettings({ VITE_CAREMERGE_INTAKE_TIMEOUT_MS: '0' })).toThrow(
      'VITE_CAREMERGE_INTAKE_TIMEOUT_MS must be a positive number of milliseconds.',
    )
  })
})
