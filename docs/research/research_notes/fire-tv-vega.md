# Fire TV and Vega OS — research notes

Verified 2026-10-01. Re-check the linked docs before relying on a detail.

## Bottom line

- **No camera, no app mic.** Vega sticks have no camera and no documented capture API; apps can't use the remote's microphone (voice goes through Alexa's cloud). **Run computer vision on a phone, laptop, or the cloud and push results to the TV** over WebSockets (supported; Socket.io 4.7.5 is on Vega's supported-library list). The organizers still suggest "a computer vision fitness app" ([update](https://amazonappdev2026.devpost.com/updates/46456-got-an-idea)) — expect that niche to be crowded.
- **Don't build the demo on Amazon-gated features:** catalog integration, voice search, content personalization, Live TV, Matter casting, DIAL. Direct Alexa+ integration isn't available to participants ([forum](https://amazonappdev2026.devpost.com/forum_topics/45263-demo-video)).
- **Demo surface:** a real Fire TV device or the Fire TV/Vega simulator per the [rules](https://amazonappdev2026.devpost.com/rules); the [FAQ](https://amazonappdev2026.devpost.com/details/faqs) adds that the Android TV Emulator is fine and no device is needed.
- **No copyrighted footage** in the demo — use generated video or the sample's catalog feed ([forum](https://amazonappdev2026.devpost.com/forum_topics/45329-media-footage-copyright-issue)).
- One project can be judged in both Fire TV and Alexa+ but can win only one track ([forum](https://amazonappdev2026.devpost.com/forum_topics/45333-can-one-project-be-submitted-to-both-fire-tv-and-alexa-tracks)).

## Amazon Devices Builder Tools (ADBT)

- Docs: [get started](https://developer.amazon.com/docs/adbt/get-started.html), [capabilities](https://developer.amazon.com/docs/adbt/capabilities.html), [troubleshooting](https://developer.amazon.com/docs/adbt/troubleshooting.html); launched May 20 2026 ([blog](https://developer.amazon.com/apps-and-games/blogs/2026/05/introducing-amazon-builder-tools)).
- npm `@amazon-devices/amazon-devices-buildertools-mcp` 1.0.13 (2026-09-25), license **UNLICENSED** (proprietary), no public source ([npm](https://www.npmjs.com/package/@amazon-devices/amazon-devices-buildertools-mcp)). Community skills are separate and MIT: [AmazonAppDev/devices-agent-skills](https://github.com/AmazonAppDev/devices-agent-skills).
- Official installer: `npx -y @amazon-devices/amazon-devices-buildertools-mcp@latest init-context --agent claude-code-cli` (`-d` MCP only, `-m` context file only, `-f` no prompts; also `check-status`, `clean-context`). **It edits user-level config**: adds a user-scope MCP server, writes skills to `~/.claude/skills`, an agent to `~/.claude/agents/adbt-agent.md`, and merges a block into the project `CLAUDE.md`.
- Project-only alternative — add to `.mcp.json`:
  `"amazon-devices-buildertools-mcp": {"type": "stdio", "command": "npx", "args": ["-y", "@amazon-devices/amazon-devices-buildertools-mcp@latest"]}`
- Optional `.adbt-config.json`, e.g. `{"platform": {"default": "vega_os"}}`. Needs Node 18+; **fails on Node 26** (sqlite3) — use Node 24.
- Tools: `search_documentation`, `list_documents`, `read_document`, `read_asset`, `analyze_perfetto_traces`, `get_app_hot_functions`, `symbolicate_acr`; 12 prompts (crash, UI fluidity, input latency, RN upgrade, media playback, Fire OS SDK upgrade); 19 skills (Vega setup, build-and-run, manifest, focus, navigation, UI components, media player, Matter casting, performance, captions, audio description, multi-TV migration, Android SDK uplevel, …).
- Full Vega support, limited Fire OS support. **Documentation-search queries are sent to Amazon.**

## Vega OS

- Devices ([specs](https://developer.amazon.com/docs/device-specs/device-specifications-fire-tv-streaming-media-player.html), updated Sep 30 2026): Fire TV Stick 4K Select (2025, OS 1.1, discontinued), Fire TV Stick HD (Apr 29 2026, OS 1.1, $34.99), **new Fire TV Stick 4K** (Sep 30 2026, **Vega OS 2.0**, $59.99; $29.99 with code 4KINTRO through Oct 7 per [AFTVnews](https://www.aftvnews.com/amazon-announces-new-3rd-gen-fire-tv-stick-4k-running-vega-os-with-an-all-new-remote/)). All 1 GB RAM, 32-bit ABI. Fire OS continues on TVs and the Cube (Fire OS 16 = API 36).
- **SDK 0.24** (Aug 6 2026, [release notes](https://developer.amazon.com/docs/vega/0.24/vega-release-notes.html)): React Native 0.83 early access (0.72 still supported), WebView on Chromium 144, requires device OS 1.2 (manifest `os-min`/`os-version` 1.2). Whether SDK 0.24 apps run on OS 2.0 is UNVERIFIED — the Stick HD or the Virtual Device is safer.
- Host ([install](https://developer.amazon.com/docs/vega/0.24/install-vega-sdk.html)): macOS 10.15+ on Apple Silicon with **Rosetta 2**, or Ubuntu 20.04/22.04/24.04 x86_64 with KVM; no Windows/WSL; 20 GB disk; Intel Mac support ends Dec 15 2026. Upgrading to macOS 27 removes Rosetta — reinstall with `softwareupdate --install-rosetta --agree-to-license` ([bulletin](https://community.amazondeveloper.com/t/developer-bulletin-issues-with-vega-devkit-after-mac-os-27-upgrade/29216)).
- Install: `curl -fsSL https://sdk-installer.vega.labcollab.net/get_vvm.sh | bash && source ~/vega/env` (CLI, SDK, Virtual Device, Vega Studio). Run: `vega virtual-device start`; package arch must match the host (aarch64 on Apple Silicon, x86_64 on Linux, armv7 for sticks) ([run apps](https://developer.amazon.com/docs/vega/0.24/run-apps.html)). Real device: `vega devmode login` ([developer mode](https://developer.amazon.com/docs/vega/0.24/developer-mode.html)).
- **Web apps run in Vega's WebView** (ADBT can wrap a URL as a WebView app). Unsupported: geolocation, file up/download, multiline text boxes, external browser, `.mov`, Advertising ID, WebGPU; `alert()`, `<select>`, `window.open()` limited ([WebView](https://developer.amazon.com/docs/vega/0.24/overview-of-webview.html)). WebGL and Web Workers documented.
- Vega can't run Android/Kotlin code or unported native libraries ([supported libraries](https://developer.amazon.com/docs/vega-api/0.24/supported-libraries.html)); no consumer sideloading; IAP and personalization don't work on the Virtual Device.
- **Fire OS vs Vega for 3 weeks:** Vega is strategic and gets full ADBT support, but it's React Native/WebView only, Mac/Ubuntu only, 1 GB devices. Fire OS works from any OS with full Android APIs and the Android TV emulator is accepted for the demo; weaker ADBT support.

## Starter samples — all in [AmazonAppDev](https://github.com/AmazonAppDev), all MIT-0

| Repo | What it is |
| --- | --- |
| `react-native-multi-tv-app-sample` | Most complete starter: Android TV, tvOS, Fire OS, Vega, web. Expo 54 / react-native-tvos 0.81; **its Vega app is still RN 0.72** |
| `react-native-multi-tv-helloworld` | Minimal shared codebase: Vega on RN 0.83 + an Expo 55 TV app |
| `hello-world-fire-tv-react-native` | 5-minute Fire OS hello world (Expo 51, react-native-tvos 0.74) |
| `vega-video-sample` | W3C media/Shaka player, DRM, IAP, Content Launcher, Live TV, focus (RN 0.83) |
| `vega-sports-app` | Themeable sports catalog app with service integration (RN 0.83) |
| `vega-audio-sample` | Music player: album, track, search, library, settings (RN 0.83) |
| `vega-tv-interfaces-sample` | Focus, i18n, navigation, scrolling patterns (RN 0.83) |
| `hello-world-fire-tv` | Kotlin + Jetpack Compose (last updated Oct 2024) |

Chrome DevTools doesn't work with RN 0.83 ([release notes](https://developer.amazon.com/docs/vega/0.24/vega-release-notes.html)).

## Capabilities

- Voice: Fire OS — Media Session, Video Skills Kit, voice scrolling (Amazon must activate) ([voice](https://developer.amazon.com/docs/fire-tv/voice-enable-your-app-and-content.html)); Vega — Media Controls for Alexa playback commands ([guide](https://developer.amazon.com/docs/vega/0.24/media-controls-guide.html)) and on-screen voice navigation via `Alexa.UIController` ([guide](https://developer.amazon.com/docs/vega/0.24/using-on-screen-nav.html)). Vega voice search and home-screen rows need catalog integration — select partners only.
- Local network: WebSockets supported ([network](https://developer.amazon.com/docs/react-native-vega/0.83/network.html)); DIAL needs a registered DIAL ID; Matter Casting needs CSA vendor/product IDs plus attestation.
- Bluetooth 5.3 + BLE on the new 4K stick; gamepads supported ([gamepad](https://developer.amazon.com/docs/react-native-vega/0.83/useGamepadEventHandler.html)); app-level Bluetooth API UNVERIFIED.
- On-device ML: nothing documented for Vega; Fire OS has no Google Play services.
- Picture-in-picture: only Amazon's own camera live-view PiP is documented. Ambient experience: no developer API found.

## Devpost facts

- Pages: [overview](https://amazonappdev2026.devpost.com/), [resources](https://amazonappdev2026.devpost.com/resources), [rules](https://amazonappdev2026.devpost.com/rules), [FAQ](https://amazonappdev2026.devpost.com/details/faqs), [dates](https://amazonappdev2026.devpost.com/details/dates).
- Submissions Aug 31 – **Oct 23, 12:00 PM PT**. Judging **Nov 9–20** per the rules and FAQ (the schedule page says Oct 26–Nov 20). Winners around Dec 3. **Keep any cloud backend running through Nov 20.**
- Judging: pass/fail first stage, then 1–5 on four **equally weighted** criteria; friction log up to a 10% bonus; product feedback required.
- Office hours promised, no schedule posted yet. Sep 3 Build Session recording: [youtu.be/ws61g53S2b4](https://youtu.be/ws61g53S2b4). Help: discord.gg/devpost.
