# Ideas — Amazon Developer Hackathon

Idea backlog for **Build, Ship, Shape** ([Devpost](https://amazonappdev2026.devpost.com/)), researched on **2026-10-01**.
The deadline is **Fri Oct 23, 2026, 3:00 PM EDT**, which leaves 22 days.
Platform facts and their sources are in [`docs/research/research_notes/`](docs/research/research_notes). Market figures are in [`docs/research/reports/market-research.md`](docs/research/reports/market-research.md).

**How to read this.** There are four buckets, as requested:

1. [Out of the box](#1-out-of-the-box) — unexpected uses of the platforms
2. [Moonshots](#2-moonshots--too-big-for-22-days) — too big to finish, each with a hackathon-sized slice
3. [Wow factor](#3-wow-factor--demo-first) — ideas that look spectacular on video
4. [Real products](#4-real-products--with-market-notes) — each with a one-line market note

Every card lists its **primary track ★** and other fits and its **mini challenges**. All except the moonshots also list **effort** (S = a few days, M = about two weeks, L = the whole window or more).
After the buckets come a [scorecard](#scorecard), a [shortlist](#shortlist), and the [ideas already taken](#already-taken--avoid).

---

## What the research changed

These facts reshaped the list. Every idea below was checked against them.

- **Alexa+ access to the real platform is gated.** The MCP Toolkit is private preview for select partners, so plan on a **real Streamable HTTP MCP server plus a simulated Alexa+ web app**. The organizers' own hint: *"an agentic workflow that orchestrates across services or keeps context across sessions stands out more."* The niches already filled include dining, food delivery, rides, ticketing, home services, beauty booking, travel, music, meditation, and education. Alexa+ renders **MCP Apps** (`ui://`) for visuals. Source: [notes](docs/research/research_notes/alexa-plus-mcp.md).
- **The Ring API is read-only.** It offers devices, event history, webhooks (human, vehicle, and motion, plus button presses), snapshots, clips, and 30–60-second live view. There is **no control of locks, alarms, or lights, and no two-way talk**, and Ring's own AI descriptions are not exposed, so you bring your own computer vision. The **Playground** simulates package, vehicle, and motion events without hardware. Ring policy bans face matching, plate reading, apps aimed at children, and anything life-safety-critical. **Accessibility is the gap no live Ring app covers.** Source: [notes](docs/research/research_notes/ring.md).
- **Bee is easy to plug in, so the use case is what wins.** It can write back only **facts and todos (with alarms)**. Speaker labels are unreliable, which makes **voice notes (journals) the clean channel for owner commands**. Real time is best-effort. Run it locally, because its private CA breaks serverless hosting. Data must be recorded on a real Bee or an Apple Watch, so **start recording now**. Source: [notes](docs/research/research_notes/bee.md).
- **Bedrock image and video generation is gone.** Nova Canvas and Nova Reel reached end-of-life on Sep 30, 2026, so "generated visuals" ideas need procedural graphics (SVG, Canvas, Skia, Lottie) or another provider. Still available: Claude 5.5 vision, **Nova 2 Sonic** speech-to-speech, Strands `BidiAgent` voice, AgentCore Runtime (it hosts MCP servers), AgentCore Gateway (it turns OpenAPI specs into MCP tools), and **Kiro Crew**, which is open source with a PR-curated App registry. Source: [notes](docs/research/research_notes/aws-and-open-source.md).
- **Fire TV has no camera, and apps can't use the remote's mic.** Computer vision has to run on a phone, laptop, or the cloud and stream to the TV over WebSockets (supported on Vega, Socket.io included). Catalog, voice search, personalization, Live TV, DIAL, and Matter casting are Amazon-gated, so don't demo on them. Web apps run in Vega's Chromium WebView, and the Android TV emulator is accepted for the video. The organizers suggested "a computer vision fitness app" by name, so expect that niche to be crowded. Source: [notes](docs/research/research_notes/fire-tv-vega.md).
- **Reach, for Potential Impact claims:** there are 250M+ Fire TV devices ([Amazon](https://developer.amazon.com/fire-tv)) and 600M+ Alexa devices ([Amazon](https://www.aboutamazon.com/news/devices/new-alexa-generative-artificial-intelligence)). Alexa+ is free with Prime across the US ([Amazon](https://www.aboutamazon.com/news/devices/alexa-plus-available-free-prime-members-us)), and more than 100M Ring cameras are in the field ([TechCrunch](https://techcrunch.com/2026/03/31/ring-app-store-bets-on-ai-to-go-beyond-home-security/)).
- **Prize math.** A project can win **one track prize plus one mini-challenge prize**. Alexa+ and Fire TV each pay $25k/$15k/$4k and will draw the most entrants. Bee and Ring each pay $12k/$8k, and their entrants need hardware or a Ring developer account, so they will likely draw fewer. AWS Builder and Open Source pay $5k each and stack on any track.

---

## 1. Out of the box

### O1. Curb Sense — your doorbell camera as a chore sensor

**Track:** Ring ★ · **Mini:** AWS Builder · **Effort:** S

- **Pitch:** On trash night, the camera checks whether the bins are actually at the curb. After pickup, it reminds you to bring them back before the HOA notices. It also catches a garage door left open at 11 PM or a porch light left burning at noon.
- **How:** Scheduled snapshots go to a vision model (Claude 5.5 on Bedrock) with a yes/no prompt per "chore". If the chore isn't done, you get a nudge by push, SMS, or a Fire TV banner. There's no people tracking at all, which keeps it squarely inside Ring policy.
- **Demo moment:** A split screen shows the real curb, then the bins appear and the reminder card flips to ✅.
- **Risk:** Snapshot framing varies by house, so offer a one-tap "draw where your bins go" region (and never touch privacy zones).

### O2. Curiosity Jar — kids' questions become a Saturday TV show

**Track:** Bee ★ · Fire TV · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** All week, a parent drops a kid's questions into the jar with a Bee voice note: "Why do cats purr?" On Saturday the TV plays a personalized 5-minute "Curiosity Show" that answers them, with narration, procedural visuals, and a quiz played with the remote.
- **How:** Read Bee `journals` (deliberate owner input, which avoids the speaker-label problem). Claude writes the scripts. Amazon Polly or Nova 2 Sonic provides the voice. A Fire TV app plays the episode, and the quiz runs on D-pad input.
- **Demo moment:** Saying "Curiosity jar: do fish sleep?" into the Bee is followed by a cut to the TV, where that exact question opens the episode.
- **Risk:** Children's data. The data is the parent's own voice notes and nothing is stored about the child, but write the consent story explicitly.

### O3. Kitchen-Table Broadcast — your board game, televised

**Track:** Fire TV ★ · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** Point a phone at the chessboard and the TV becomes an esports broadcast, with an evaluation bar, move history, "blunder!" replays, and an AI color commentator.
- **How:** A phone web app captures the board. Each move goes to a vision model that reads the position as FEN, Stockfish (WASM) evaluates it, and the result streams over a local WebSocket to the Fire TV app, which renders the broadcast overlay.
- **Demo moment:** A family chess game where the commentator roasts Grandpa's opening.
- **Risk:** Board-recognition accuracy. Constrain the camera angle and fall back to "tap to confirm move".

### O4. Lingo Mirror — Bee as a speaking coach for language learners

**Track:** Bee ★ · **Mini:** AWS Builder · **Effort:** S–M

- **Pitch:** Record a 2-minute Bee voice note in the language you're learning each day. Every morning you get corrections, your three most frequent mistakes, and a drill built from your own sentences. Saved Bee facts track your progress over weeks.
- **How:** Bee transcribes up to 40 languages. Voice notes are owner-only input, so speaker labels don't matter. Claude grades the transcript against a CEFR rubric, and Bee `facts` persist learner-profile items such as "struggles with the subjunctive".
- **Demo moment:** Day 1 versus day 10, with the error heatmap cooling down.
- **Risk:** Transcription can quietly "fix" grammar mistakes. Test early with deliberately wrong sentences.

### O5. Intent ↔ Evidence — what you said meets what actually happened at the door

**Track:** Bee ★ · Ring · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** Suppose you told your partner "the plumber's coming at 2" and told the dog walker "I'll leave the side gate open". The system matches those spoken intentions against Ring events: the plumber arrived at 2:07 ✅, and the dog walker hasn't shown up by 4 ⚠️.
- **How:** Claude extracts expected-visit intents from Bee conversations and stores them as Bee todos. Ring `motion_detected` (human) and `button_press` webhooks are matched by time window, never by identity. Mismatches become Bee todo alarms.
- **Demo moment:** A timeline lays spoken promises against real arrivals.
- **Risk:** Two hardware ecosystems in one demo. Use the Ring Playground and a replay harness for the Ring side.

### O6. Gesture Remote — control the TV with your hands, for people who can't use a remote

**Track:** Fire TV ★ · **Mini:** Open Source · **Effort:** M

- **Pitch:** For people with limited grip or tremor, simple hand or head gestures (detected by a phone or webcam camera) drive Fire TV navigation: swipe, select, back, and volume.
- **How:** MediaPipe hand or face landmarks run on the phone (web app), since Fire TV has no camera. The phone sends gesture events over a WebSocket to a Fire TV app, which maps them to focus navigation.
- **Demo moment:** Someone browses and plays a show without touching the remote.
- **Risk:** Platform input-injection limits. Scope it to navigation inside your own app if system-wide control isn't allowed.

---

## 2. Moonshots — too big for 22 days

### M1. The Home Narrator — one memory across the front door, the living room, and your day

**Tracks:** Ring · Bee · Fire TV · Alexa+ (pick one primary) · **Mini:** AWS Builder (AgentCore Memory)

- **Vision:** A household agent with long-term memory fuses who came to the door (Ring), what you committed to (Bee), and what's on the TV (Fire TV), and you talk to it through Alexa+. It handles questions like "Did the contractor come while I was out, and did they fix what I asked?"
- **Why it's too big:** Four integrations, cross-device identity, a privacy model for a shared household, and proactive behavior that isn't creepy.
- **Hackathon slice:** Ring events plus Bee todos feed a nightly "home brief" on Fire TV, with follow-up questions through a simulated Alexa+ backed by an MCP server.

### M2. Your Personal Channel — a 24/7 TV channel generated for one household

**Track:** Fire TV ★ · **Mini:** AWS Builder

- **Vision:** A live channel assembled from your interests, your day (Bee), local news, and weather. It's narrated, scored, and visual, and it never repeats.
- **Why it's too big:** Bedrock video generation is end-of-life, real-time generation is expensive, and content rights get complicated.
- **Hackathon slice:** A 3-minute nightly "Evening Edition" built from procedural motion graphics and TTS narration, played on Fire TV.

### M3. ASL at the Door and on the Couch

**Tracks:** Ring · Fire TV · **Mini:** Open Source

- **Vision:** Visitors can sign to a Deaf resident through the doorbell camera, and every TV show gets an on-demand signing avatar.
- **Why it's too big:** Continuous sign-language recognition and fluent avatar synthesis are open research problems.
- **Hackathon slice:** Fingerspelling plus 20 common signs ("delivery", "help", "wait") recognized from a Ring clip, with captions shown on Fire TV.

### M4. Aging-in-Place Signals — early, non-diagnostic decline awareness

**Tracks:** Ring · Bee · Fire TV · **Mini:** AWS Builder

- **Vision:** Gradual changes in routine (door activity), conversation vitality (Bee), and TV habits form an early-warning picture for families, months before a crisis.
- **Why it's too big:** Clinical validation, medical-device regulation, Ring's ban on life-safety dependence (§2.8), and consent from the person being observed.
- **Hackathon slice:** A weekly "routine report" for family that is explicitly non-diagnostic.

### M5. The Agent Neighborhood — home agents negotiating with each other

**Tracks:** Alexa+ ★ · **Mini:** AWS Builder (Strands A2A)

- **Vision:** Your home agent negotiates with your neighbors' agents to hold a package, lend a ladder, or coordinate a carpool, using privacy-preserving A2A protocols.
- **Why it's too big:** Trust, identity, abuse prevention, and the network effects of a two-sided marketplace.
- **Hackathon slice:** A Ring package event triggers two Strands agents that negotiate a package hold over A2A, shown in the simulated Alexa+ web app.

### M6. Every Small Business, Voice-Ready

**Track:** Alexa+ ★ · **Mini:** Open Source

- **Vision:** Point a tool at any small business's website or POS and it generates a certification-ready Alexa+ add-on: an MCP server, MCP Apps cards, OAuth, and Amazon Wallet checkout.
- **Why it's too big:** Arbitrary websites, payments, account linking, and certification. Booking niches are also crowded (Square, Vagaro, OpenTable).
- **Hackathon slice:** Generate an MCP server from one menu page or one class schedule and run it through the simulator with Alexa+ design rules enforced.

---

## 3. Wow factor — demo-first

### W1. Haunt Mode — the house that reacts to trick-or-treaters

**Track:** Ring ★ · Fire TV · Alexa+ · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** A doorbell press or person detection starts a spooky scene on the Fire TV in the front window, plays a scream on the Ring Chime, and has an Alexa+-style narrator welcome the visitor in character. A live candy tally runs on the side.
- **How:** Ring webhooks (`button_press`, `motion_detected` with sub-type human) feed an event bus. That bus triggers the Fire TV app over WebSocket, Ring Chime audio playback (an Early Access API), and Polly or Nova 2 Sonic for the narrator. Counts only, with no images stored.
- **Demo moment:** A trick-or-treater rings, the window TV erupts, the chime screams, and the tally ticks up, all within 10 seconds.
- **Why now:** Halloween falls 8 days after the deadline, so it's a ready-made seasonal hook for the video and social posts. The same event engine can run holiday "porch shows" all year.
- **Risk:** Chime playback is Early Access. Keep the TV scene as the core so the demo doesn't depend on it.

### W2. Rep Vision — a pose-tracking coach on the big screen

**Track:** Fire TV ★ · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** Prop up your phone and the TV shows your skeleton overlay, live rep counts, a form score, and spoken cues ("knees out!").
- **How:** MediaPipe Pose runs on the phone, which is the camera because Fire TV has none. It streams keypoints over a WebSocket to the Fire TV app, which renders the overlay and counters. Claude writes a post-workout summary.
- **Demo moment:** A side-by-side of a bad squat and a corrected squat, with the counter refusing to count the bad rep.
- **Risk:** The organizers suggested computer-vision fitness by name, so many entrants will build it. Win on polish, or use the same pipeline for P9.

### W3. Glass-Box Alexa+ — watch the agent think

**Track:** Alexa+ ★ · **Mini:** AWS Builder / Open Source · **Effort:** M

- **Pitch:** A simulated Alexa+ in the browser where you talk by voice (Nova 2 Sonic) while a live map shows the plan, every MCP tool call across servers, latency against the 500 ms budget, and MCP Apps cards rendering like on an Echo Show.
- **Why it matters:** It turns the "simulated" path from a compromise into the feature, and it can be the shell for any Alexa+ idea (P7, P8, P10).
- **Demo moment:** You ask a multi-step question and the tool-call graph lights up like a subway map.

### W4. Living Room Arena — phones as controllers, an AI as host

**Track:** Fire TV ★ · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** A party game where everyone joins by QR code and an AI host improvises rounds from **your family's own material** (photos, in-jokes, this week's calendar), judges answers, and roasts the winner.
- **How:** A Fire TV app is the stage and a phone web app is the controller, connected through a lightweight relay (WebSocket). Claude writes the host lines and Polly voices them. All visuals are procedural.
- **Demo moment:** Four phones and one TV in a full round lasting 45 seconds.
- **Risk:** Amazon's own **Luna GameNight** already offers 45+ phone-controlled party games on Fire TV with Prime ([Amazon](https://www.aboutamazon.com/news/entertainment/what-is-amazon-luna)), and Jackbox has logged 826M+ player joins. Personalized content is the only defensible angle.

### W5. Your Day, Directed — a cinematic recap of your day on TV

**Track:** Bee ★ · Fire TV · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** Each evening the TV plays a 60-second title sequence of your day: an animated map of the places you went (Bee locations), the moments that mattered, the promises you made, and tomorrow's top three.
- **How:** Bee `daily`, `locations`, `conversations`, and `todos` feed a Claude script, which drives a procedural motion-graphics renderer on Fire TV (no generated video). The voice comes from Polly or Nova 2 Sonic.
- **Demo moment:** The camera pulls back from a glowing map trail to "Tomorrow: send Priya the deck."

### W6. Door Diary — your front door as a daily comic strip

**Track:** Ring ★ · **Mini:** AWS Builder · **Effort:** S–M

- **Pitch:** Your day at the door, told as a four-panel comic: the mail came, a cat inspected the porch, and Sam got home at 5:42. Stylization means no real faces ever appear.
- **How:** Ring event history and snapshots go to Claude, which writes captions and picks panels. Panels are rendered from SVG character templates (or Stable Image style transfer, if it is still available on Bedrock).
- **Demo moment:** Scrolling a week of comics on Fire TV.

---

## 4. Real products — with market notes

Each idea has a market line with sources. Fuller figures are in the [market report](docs/research/reports/market-research.md).

### P1. DoorSense — an accessible front door for Deaf, hard-of-hearing, and blind users

**Track:** Ring ★ · Fire TV · **Mini:** AWS Builder · Open Source · **Effort:** M

- **Pitch:** Doorbell presses and visitors turn into alerts you can see and feel: colored light flashes (through Hue or Home Assistant, since Ring can't control lights), distinct haptic patterns on phone or watch, and a Fire TV banner showing a snapshot. For blind and low-vision users, it reads out a narrated scene description such as "a courier holding a large box". It can also caption what the visitor said, if the clip carries audio (unverified, so check this early).
- **Why it wins:** The Ring research found **no live Ring Appstore app covering accessibility**, and it is a named Ring priority category. The UX guide's own requirements (WCAG 2.2 AA, privacy-zone masking) become features.
- **Build notes:** Ring webhooks trigger the alert, then a snapshot or clip fetch, a vision model and transcription, and finally the alert fan-out. There is no face recognition, only descriptions. Demo with the Playground and a webhook replay harness.
- **Market:** 37.5M US adults report trouble hearing ([NIDCD](https://www.nidcd.nih.gov/health/statistics/quick-statistics-hearing)) and about 7M have vision loss, 1M of them blind ([CDC](https://www.cdc.gov/vision-health/data-research/vision-loss-facts/index.html)). Today's options are closed radio flash-and-vibrate kits with no camera context (Bellman & Symfon, Serene) or free photo describers (Be My Eyes, Seeing AI), and Ring's own Video Descriptions are a Premium-tier beta. Nobody routes one door event to light, wrist, TV, and voice at once.

### P2. Ring Bridge for Home Assistant — the official-API integration

**Track:** Ring ★ · **Mini:** Open Source · **Effort:** M

- **Pitch:** A Home Assistant custom integration built on the **official** Amazon Vision API (OAuth plus HMAC-verified webhooks), exposing Ring human, vehicle, and button events and snapshots as HA entities. Every light, lock, and Matter device can then react to Ring events, which the read-only Ring API can't do on its own.
- **Why it wins:** Today's popular Ring integrations rely on reverse-engineered APIs that conflict with Ring's "approved auth methods only" rule. This fills the IoT home-automation priority category and is a credible open-source contribution.
- **Market:** Home Assistant reports 2M+ installs ([HA](https://www.home-assistant.io/blog/2025/04/16/state-of-the-open-home-recap/)), with 691,885 opted into analytics, up 34% in a year ([analytics](https://analytics.home-assistant.io/data.json)). 34,495 of those run the Ring integration, which polls Ring's cloud through a reverse-engineered library and has a forum thread calling it "abandoned" ([integration](https://www.home-assistant.io/integrations/ring/), [forum](https://community.home-assistant.io/t/ring-integration-abandoned-iso-dev-to-submit-existing-pr-ready-since-nov-2025/978712)). A distribution path exists: each user creates a Ring **Private App** (up to 10 accounts, no certification). Whether Ring's terms allow this for an open-source integration is UNVERIFIED.

### P3. Front Desk — visitor triage for small offices with a Ring doorbell

**Track:** Ring ★ · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** For dental offices, studios, and small agencies: a doorbell press posts to Slack or Teams within seconds with a snapshot, a "courier / expected guest / unknown" triage (matched against today's calendar by time, never by face), and one-tap responses. It also keeps an after-hours log and a weekly visitor report.
- **Why it wins:** It covers Ring's "business systems" priority. Envoy-class visitor management is priced for enterprises, while tiny offices already own a doorbell.
- **Market:** An analyst estimate puts visitor-management software at about $2.2B in 2025, growing to $6.8B by 2034, with Envoy holding roughly 14% ([Fortune Business Insights](https://www.fortunebusinessinsights.com/visitor-management-system-vms-market-105882)). Verkada ($5.8B valuation, [CNBC](https://www.cnbc.com/2025/12/03/verkada-capitalg-valuation-security.html)) and Spot AI serve the mid-market, and Ring's Virtual Security Guard costs $99/mo per location. No self-serve check-in exists for micro-businesses already on Ring, and none launched on the Ring Appstore.

### P4. Promise Keeper — never drop a spoken commitment

**Track:** Bee ★ · **Mini:** AWS Builder (Kiro Crew) · Open Source (Crew App PR) · **Effort:** M

- **Pitch:** "I'll send you the deck by Friday" becomes a Bee todo with an alarm, plus a drafted follow-up email and a weekly "promises kept" score. Commitments other people made to you become "waiting on" items.
- **Why it wins:** It uses **Bee's one write path** (todos with alarms, suggestion accept/dismiss) as the human-in-the-loop. It fits the personal-productivity priority use case. Built as a **Kiro Crew App** (scheduled job, local-first, which suits Bee's private CA), it qualifies for AWS Builder on its own, and a PR to the Crew App registry is an open-source contribution.
- **Market:** People pay for captured conversations. Otter has $100M ARR and 35M users ([Otter](https://otter.ai/blog/otter-ai-caps-transformational-2025-with-100m-arr-milestone-industry-first-ai-meeting-agents-and-global-enterprise-expansion)), Granola raised at a $1.5B valuation ([TechCrunch](https://techcrunch.com/2026/03/25/granola-raises-125m-hits-1-5b-valuation-as-it-expands-from-meeting-notetaker-to-enterprise-ai-app/)), and Plaud has shipped 2M+ wearable recorders with $100M+ subscription ARR ([TechCrunch](https://techcrunch.com/2026/06/16/plaud-says-its-software-business-topped-100m-in-arr-after-shipping-over-2m-ai-notetakers/)). But they summarize video calls. In-person commitments, and turning notes into tracked actions, are still open.

### P5. Decision Ledger — the "why" behind your code, captured from conversations

**Track:** Bee ★ · **Mini:** AWS Builder (Kiro) · **Effort:** M

- **Pitch:** Engineering decisions made in hallways and calls ("let's use Postgres, not Dynamo, because of the reporting queries") become draft **ADRs** opened as pull requests in the right repo, linked to issues. Later you can ask "why did we choose X?" and get the transcript-backed answer.
- **Why it wins:** It fits the developer-experience priority use case. It is knowledge capture, not task execution, so it doesn't overlap with *ringfence*, which already turns spoken tasks into coding-agent runs.
- **Market:** 50% of developers lose 10+ hours a week to organizational inefficiency, and "finding information" is the top friction ([Atlassian DevEx 2025](https://www.atlassian.com/blog/developer/developer-experience-report-2025)). Incumbents summarize only their own tool: Atlassian Rovo, Linear, and Geekbot at $2.50 per participant per month ([Geekbot](https://geekbot.com/pricing/)). ADRs have grassroots pull (adr-tools has 5.7k★, [GitHub](https://github.com/npryce/adr-tools)) and are now required by the UK government's design council ([GDS](https://technology.blog.gov.uk/2025/12/08/the-architecture-decision-record-adr-framework-making-better-technology-decisions-across-the-public-sector/)), but nothing captures decisions where they're actually made: out loud.

### P6. Lecture Loop — lectures become spaced-repetition study sessions

**Track:** Bee ★ · Fire TV (optional study mode) · **Mini:** AWS Builder · **Effort:** S–M

- **Pitch:** Wear Bee to class. That evening you get a quiz on what was actually said, flashcards exported to Anki, and a "you were in class but missed this" summary. Spaced repetition then schedules reviews as Bee todos with alarms.
- **Why it wins:** It fits the education priority use case, and lecture speech doesn't need speaker labels.
- **Market:** Large but consolidating. Quizlet has 60M+ users and bought Coconote, a lecture notetaker ([PR Newswire](https://www.prnewswire.com/news-releases/quizlet-supercharges-studying-with-new-product-innovations-and-strategic-acquisition-302679622.html)). Turbo AI reached 5M users ([TechCrunch](https://techcrunch.com/2025/10/23/20-year-old-dropouts-built-ai-notetaker-turbo-ai-to-5-million-users/)), and ChatGPT and Gemini give study modes away. Lecture-to-notes is commoditized. Passive in-room capture plus a **retention** loop (spaced repetition delivered as alarms or TV review) is the open angle.

### P7. Hearthside — a voice biographer that interviews your parents

**Track:** Alexa+ ★ · **Mini:** AWS Builder (AgentCore Memory/Runtime) · **Effort:** M

- **Pitch:** Over weeks of short voice sessions, an Alexa+ add-on interviews an older relative about their life. It remembers every earlier answer, asks better follow-ups, and turns the stories into chapters shown as MCP Apps cards and compiled into a family book.
- **Why it wins:** **Cross-session memory** is the organizers' explicit hint, the niche is uncrowded on Alexa+, and voice is the natural interface for people who won't type their memoirs.
- **Market:** Storyworth has printed 1M+ books since 2013 at $69–199 a year ([Storyworth](https://welcome.storyworth.com/what-is-storyworth), [pricing](https://welcome.storyworth.com/storyworth-pricing)). Remento ($99/yr) landed a Shark Tank deal ([Yahoo Finance](https://finance.yahoo.com/news/remento-lands-deal-mark-cuban-130000571.html)), and StoryKeeper has printed 12,000+ books ([StoryKeeper](https://storykeeper.com/)). Every one of them needs an app, email, or scheduled-call setup. A zero-setup voice interviewer on the Echo the elder already owns doesn't exist, and there are 600M+ Alexa devices ([Amazon](https://www.aboutamazon.com/news/devices/new-alexa-generative-artificial-intelligence)).

### P8. Care Circle — voice-first coordination for family caregivers

**Track:** Alexa+ ★ · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** Alexa+ becomes the shared hub for caring for a parent. It handles medication schedules, "who's taking Mom to the cardiologist Thursday?", refill reminders, and a daily check-in that summarizes for the family group chat.
- **Why it wins:** It orchestrates **across services and sessions** (the organizers' hint). Amazon's own **Alexa Together** is no longer offered, which leaves a gap. It fits caretaking.
- **Market:** There are 63M US family caregivers (1 in 4 adults), spending about $7,200 a year out of pocket ([AARP/NAC 2025](https://www.aarp.org/press/releases/2025-07-24-new-report-reveals-crisis-point-for-americas-63-million-family-caregivers.html)). 61.2M Americans are 65+ ([Census](https://www.census.gov/newsroom/press-releases/2025/older-adults-outnumber-children.html)), and 75% of adults 50+ want to stay in their current home ([AARP](https://www.aarp.org/press/releases/2024-12-10-new-aarp-report-majority-adults-50-plus-age-place-policies-communities-catch-up.html)). Amazon's $19.99/mo Alexa Together is "no longer available" ([Amazon](https://www.aboutamazon.com/news/devices/alexa-together-launches-to-help-customers-remotely-care-for-loved-ones)), so the family-coordination layer is vacant.

### P9. HomePT — physical-therapy adherence on the living-room TV

**Track:** Fire TV ★ · **Mini:** AWS Builder · **Effort:** M–L

- **Pitch:** Your physical therapist prescribes exercises, and the TV guides each session with rep counting and form feedback from a phone camera. The clinician gets an adherence report, the kind of data remote-therapeutic-monitoring billing codes are built on.
- **Why it wins:** It fits the fitness and computer-vision priority categories, and it gives clinics a business model.
- **Market:** Hinge Health guides $856–860M in 2026 revenue, growing 53% year over year in Q2 ([SEC](https://www.sec.gov/Archives/edgar/data/1673743/000162828026052558/hnge-q2202684xex991.htm)), and Sword Health was valued at $3B ([TechCrunch](https://techcrunch.com/2024/06/04/sword-healths-raises-130m-valuation-3b-ai-physical-therapy/)). Both sell to employers and health plans. CMS 2026 added short-episode remote-monitoring codes for 2–15 days of data ([Federal Register](https://www.federalregister.gov/documents/2025/11/05/2025-19787/medicare-and-medicaid-programs-cy-2026-payment-policies-under-the-physician-fee-schedule-and-other)), which opens a lane for independent PT clinics. Some of these codes may require an FDA-regulated device, so pitch it as an adherence tool first.

### P10. Voicecheck — certification readiness for Alexa+ add-ons

**Track:** Alexa+ ★ (Agent Skill) · **Mini:** Open Source · **Effort:** M

- **Pitch:** An Agent Skill plus CLI that audits any MCP server against Alexa+ add-on rules: tool round trips under 500 ms, at most 5 options, read-back confirmations, no IDs spoken, one tool per intent, OAuth 2.1 Protected Resource Metadata and PKCE, `Origin` validation, MCP Apps checks, and 2025-11-25 versus 2026-07-28 compatibility. It also runs scripted multi-turn voice conversations against the server.
- **Why it wins:** It serves every brand in the Alexa+ preview queue, and an Agent Skill entry is explicitly legitimate. It is a strong open-source candidate.
- **Market:** The official MCP registry listed 38,255 servers from 22,443 publishers on Oct 1, 2026 ([registry API](https://registry.modelcontextprotocol.io/v0/servers?version=latest)), and the SDKs drew 97M+ monthly downloads as of Dec 2025 ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)). Alexa+ began accepting brands' own MCP servers in Jul 2026 ([Amazon](https://developer.amazon.com/alexaplus/blogs/2026/07/alexa-plus-new-ways-to-build-experiences)). There is no quality bar yet: conformance, security, voice-readiness, and observability testing are all open. The near-term buyer pool is small, though, because add-ons are partner-only for now.

### P11. Rookie Mode — a live game companion that teaches the sport as you watch

**Track:** Fire TV ★ · **Mini:** AWS Builder · **Effort:** M

- **Pitch:** It's built for new fans: partners, kids, and international viewers. A TV app follows the live game from a play-by-play feed and explains each play in plain language ("they punted because 4th-and-9 is too far to risk"). A "catch me up" button recaps what you missed, and anyone can ask questions from their phone.
- **Why it wins:** Sports is a named Fire TV priority that nothing else here covers. It starts from the `vega-sports-app` sample and needs no copyrighted footage, because the demo is data plus explanations.
- **Build notes:** For the demo, replay a historical game's play-by-play as if it were live. Claude explains, Polly narrates, and phone Q&A runs over WebSocket.
- **Risk:** Real-time sports-data rights are the main production cost.
- **Market:** 77% of fans do something game-related on a second screen while watching at home ([Deloitte](https://www.deloitte.com/us/en/insights/industry/sports/immersive-sports-fandom.html)). Prime's Thursday Night Football averaged 15.3M viewers in 2025, up 16% ([Amazon Ads](https://advertising.amazon.com/library/news/prime-video-tnf-2025-viewership-advertising)), and 26% of fans often can't tell which service carries a game ([Nielsen/Gracenote](https://www.nielsen.com/news-center/2026/gracenote-study-85-of-sports-fans-want-tv-home-screens-to-show-when-and-where-to-watch-favorite-teams/)). League and ESPN companions live on the phone. A newcomer-tuned explainer on the TV itself is open.

---

## Scorecard

These are my subjective 1–5 scores against the four judging criteria, which are weighted equally. **Feasibility** (a solo build in 22 days, 5 = easy) is a gate, not part of the total. Moonshots are left out. Use one as the "vision" slide for a smaller build.

| # | Idea | Primary track | Tech | Design | Impact | Idea | **Total /20** | Feasibility |
| --- | --- | --- | :-: | :-: | :-: | :-: | :-: | :-: |
| P1 | DoorSense | Ring | 4 | 5 | 5 | 5 | **19** | 4 |
| P7 | Hearthside | Alexa+ | 4 | 5 | 4 | 5 | **18** | 3 |
| P8 | Care Circle | Alexa+ | 4 | 4 | 5 | 4 | **17** | 3 |
| P4 | Promise Keeper | Bee | 4 | 4 | 4 | 4 | **16** | 3 |
| O2 | Curiosity Jar | Bee | 4 | 4 | 3 | 5 | **16** | 3 |
| O3 | Kitchen-Table Broadcast | Fire TV | 4 | 5 | 2 | 5 | **16** | 3 |
| O6 | Gesture Remote | Fire TV | 4 | 4 | 4 | 4 | **16** | 3 |
| W3 | Glass-Box Alexa+ (a shell for P7/P8/P10) | Alexa+ | 5 | 5 | 3 | 3 | **16** | 3 |
| W5 | Your Day, Directed | Bee | 4 | 5 | 3 | 4 | **16** | 3 |
| P2 | Ring Bridge for Home Assistant | Ring | 5 | 3 | 4 | 3 | 15 | 4 |
| P3 | Front Desk | Ring | 4 | 4 | 4 | 3 | 15 | 4 |
| P5 | Decision Ledger | Bee | 4 | 3 | 4 | 4 | 15 | 4 |
| P10 | Voicecheck | Alexa+ | 5 | 3 | 3 | 4 | 15 | 4 |
| W1 | Haunt Mode | Ring | 4 | 5 | 2 | 4 | 15 | 4 |
| O5 | Intent ↔ Evidence | Bee | 4 | 3 | 3 | 5 | 15 | 2 |
| P9 | HomePT | Fire TV | 4 | 4 | 4 | 3 | 15 | 2 |
| P11 | Rookie Mode | Fire TV | 3 | 4 | 4 | 3 | 14 | 4 |
| W2 | Rep Vision | Fire TV | 4 | 5 | 3 | 2 | 14 | 3 |
| W4 | Living Room Arena | Fire TV | 4 | 5 | 3 | 2 | 14 | 3 |
| O4 | Lingo Mirror | Bee | 3 | 3 | 3 | 4 | 13 | 4 |
| P6 | Lecture Loop | Bee | 3 | 4 | 3 | 3 | 13 | 4 |
| W6 | Door Diary | Ring | 3 | 4 | 2 | 4 | 13 | 4 |
| O1 | Curb Sense | Ring | 3 | 3 | 2 | 4 | 12 | 5 |

**What each track needs to get started:**

- **Bee:** a Bee device or the Apple Watch app, plus days of real recorded data.
- **Ring:** a Ring developer account; the Playground covers demos without hardware.
- **Fire TV:** the Vega SDK (Apple Silicon Mac or Ubuntu) or the Android TV emulator, plus a phone for any camera work.
- **Alexa+:** nothing gated on the simulated path.

## Shortlist

My recommendation, weighing score, feasibility, and likely competition:

1. **P1 DoorSense (Ring ★).**
   - **Why:** It has the top score, and the accessibility gap is verified: no live Ring app covers it, and Ring names accessibility as a priority. The Ring field is probably smaller, since it needs Ring developer onboarding, Ring-specific APIs, and US-located devices for real-device testing.
   - **Layers:** Use Fire TV as an alert surface. Claude vision on Bedrock plus Strands covers AWS Builder. For Open Source, contribute a webhook-signature verifier and replay harness to `ring-api-helloworld`, which also fixes two friction-log items.
   - **Day-1 spike:** Ring console → Playground → simulated event → snapshot → vision description → HMAC-verified webhook through a tunnel. Confirm the Playground works for an account with no devices, which is still UNVERIFIED.
2. **P7 Hearthside on a W3 Glass-Box simulator (Alexa+ ★).**
   - **Why:** Alexa+ has the biggest prizes (tied with Fire TV). Cross-session memory is exactly what the organizers said stands out, and a voice-native memoir interviewer doesn't exist yet.
   - **Layers:** For AWS Builder, AgentCore Runtime hosts the MCP server, with AgentCore Memory and Nova 2 Sonic voice. For Open Source, publish the reusable Alexa+-style MCP add-on starter.
   - **Alternative:** Swap in **P8 Care Circle** for higher impact at higher complexity.
   - **Day-1 spike:** A three-tool Streamable HTTP MCP server (Python `mcp` v2 or TS v2) → MCP Inspector → web client → one Nova 2 Sonic round trip in us-east-1.
3. **P4 Promise Keeper as a Kiro Crew App (Bee ★).**
   - **When:** Only if a Bee or the Apple Watch app is in hand within about 2 days, because the demo needs real recorded data.
   - **Why:** It fits three ways at once: the Bee track, Kiro Crew (which qualifies for AWS Builder on its own), and a Crew App registry PR (Open Source).
   - **Day-1 spike:** Developer Mode → `bee login` → `bee now --json` → create a todo with an alarm → `kirocrew doctor`. Open bug [#14](https://github.com/bee-computer/bee-cli/issues/14) reports `/v1/todos` returning 500, so test this first.

**Fast, fun fallback:** W1 Haunt Mode has the smallest scope, a high Design score, and a seasonal hook.

**Before anything else:** pick the track, then request the AWS credits. The form rejects requests that don't name a track, closes Oct 21, and needs a Paid-plan AWS account.

## Already taken — avoid

Found during research. Building a near-copy wastes the "Quality of the Idea" score.

| Idea | Already exists as |
| --- | --- |
| Elder-care routine and fall alerts from Ring | Density Routines, Beside Care, memories.ai; hackathon entrant "Porchlight" |
| Package tracking or theft alerts | Package Protect |
| Short-term-rental monitoring | Minut |
| Bird ID from Ring cameras | WhatsThatBird.AI |
| Foot traffic, queues, loitering | StoreTraffic, QueueFlow, Lumeo, ProxView |
| Multi-camera wall on TV | Video Wall Live |
| Phone-controlled party games on Fire TV | Amazon Luna GameNight (45+ games, included with Prime) |
| Camera form-coaching fitness | Peloton IQ (Plus machines); the organizers suggested it by name, so expect many entries |
| Spoken tasks → coding-agent runs | *ringfence* (hackathon entrant) |
| Bee consent/redaction layer, weather, journaling | *bee-bystander*, *ambient-guard*, *beereflect-ai* (hackathon entrants) |
| Household-ops MCP, voice-commerce POS add-on | Entrants building a "stateful HomeOps MCP" and "AgentPOS" |
| Restaurant booking, food delivery, rides, tickets, home services, salon booking, travel | Already live Alexa+ partners (OpenTable, Grubhub, Uber, Ticketmaster, Thumbtack, Vagaro/Square, Expedia) |
