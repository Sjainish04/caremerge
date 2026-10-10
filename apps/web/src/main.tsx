/**
 * Entry point and composition root: loads the fonts, styles, and settings,
 * builds the simulator API client, and mounts the app with it.
 */

import '@fontsource-variable/atkinson-hyperlegible-next'
import '@fontsource-variable/source-serif-4/wght-italic.css'
import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { createSimulatorApi } from './api/client'
import { loadSettings } from './settings'

const root = document.getElementById('root')
if (!root) {
  throw new Error('The page is missing its #root element.')
}

const settings = loadSettings(import.meta.env)
const api = createSimulatorApi(window.fetch.bind(window), window.location.origin, settings)

createRoot(root).render(
  <StrictMode>
    <App api={api} />
  </StrictMode>,
)
