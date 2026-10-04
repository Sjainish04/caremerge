# Market research — basic sizing for product ideas

Researched 2026-10-01 for the "Real products" bucket in [`ideas.md`](../../../ideas.md).
Rules: every number has its source; analyst-firm sizes are labelled as estimates; anything unconfirmed says UNVERIFIED.

**Cross-cutting finding — the Ring Appstore.** It launched Mar 31 2026 for US Ring subscribers with ~15 apps, already covering elder care (Density Routines), rentals (Minut), package theft (Package Protect), and small-business analytics (QueueFlow, Lumeo, StoreTraffic, ProxView). Ring takes 10%; TechCrunch reports ">100M cameras in the field" ([TechCrunch](https://techcrunch.com/2026/03/31/ring-app-store-bets-on-ai-to-go-beyond-home-security/)). Several home categories therefore already have competitors inside Ring.

## Home, care, and the front door

### Aging in place and family caregiving → P8 Care Circle

- 61.2M Americans were 65+ in 2024 — 18.0% of the population, +3.1% year over year ([US Census, Jun 2025](https://www.census.gov/newsroom/press-releases/2025/older-adults-outnumber-children.html)).
- 75% of adults 50+ want to stay in their current home ([AARP, Dec 2024](https://www.aarp.org/press/releases/2024-12-10-new-aarp-report-majority-adults-50-plus-age-place-policies-communities-catch-up.html)).
- 63M family caregivers (~1 in 4 adults, +20M since 2015) spend ~$7,200/yr out of pocket ([AARP/NAC, Jul 2025](https://www.aarp.org/press/releases/2025-07-24-new-report-reveals-crisis-point-for-americas-63-million-family-caregivers.html)).
- Alexa Together ($19.99/mo): Amazon's page carries "Update May 21, 2025: Alexa Together is no longer available" and points to Emergency Assist ([Amazon](https://www.aboutamazon.com/news/devices/alexa-together-launches-to-help-customers-remotely-care-for-loved-ones)). A June 2024 end date appears only in third-party posts (UNVERIFIED).
- Competitors: Vayyar Care's consumer sensor was sold exclusively with Alexa Together ([Vayyar](https://vayyar.com/care-docs/b2c/)); Lively remains a Best Buy brand while Best Buy exited Current Health ([10-K](https://www.sec.gov/Archives/edgar/data/764478/000076447826000009/bby-20260131.htm)); Cherish Serenity radar with AT&T ([AT&T](https://about.att.com/story/2023/cherish-serenity.html)); Aloe Care Smart Hub 2 ([Aloe Care](https://www.aloecare.com/post/aloe-care-health-launches-smart-hub-2-at-ces-2025)); CarePredict moved to senior-living operators.
- **Gap:** Amazon dropped the paid family-dashboard layer; a no-new-hardware caregiver layer (Alexa+ check-ins, Ring events, Fire TV) is open. Density Routines is the closest rival.

### Accessible alerts for Deaf/HoH and blind/low-vision people → P1 DoorSense

- 37.5M US adults (15%) report trouble hearing ([NIDCD](https://www.nidcd.nih.gov/health/statistics/quick-statistics-hearing)); 430M people worldwide need rehabilitation for disabling hearing loss ([WHO, Mar 2026](https://www.who.int/news-room/fact-sheets/detail/deafness-and-hearing-loss)).
- ~7M Americans have vision impairment, including 1M who are blind ([CDC](https://www.cdc.gov/vision-health/data-research/vision-loss-facts/index.html)); 2.2B worldwide have some vision impairment ([WHO, Feb 2026](https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment)).
- Competitors: Bellman & Symfon flash/bed-shaker receivers ([Bellman](https://us.bellman.com/collections/door-notification)); Serene CentralAlert ([Independent Living](https://independentliving.com/serene-centralalert-ca-380-wearable-notification-system/)); Be My Eyes (~800K users, 8.5M volunteers, free — [Be My Eyes](https://www.bemyeyes.com/blog/be-my-eyes-announces-major-community-milestones-and-new-services-for-people-who-are-blind-or-have-low-vision/)); Seeing AI (free, [site](https://www.seeingai.com/)).
- Built-ins: Fire TV auto picture-in-picture for doorbells (2020 report lists three devices; current coverage UNVERIFIED — [AFTVnews](https://www.aftvnews.com/fire-tvs-can-now-automatically-show-picture-in-picture-feeds-of-video-doorbells-and-security-cameras/)); Ring Video Descriptions beta, Ring Home Premium only ([The Register, Jun 2025](https://www.theregister.com/2025/06/25/amazons_ring_ai_video_description/)).
- **Gap:** alert kits are closed radio systems with no camera context; nobody fans one event out to TV overlay, light flash, wearable haptic, and spoken description.

### Short-term rental access and party monitoring (not shortlisted)

- 1.69M US listings in 2025, forecast 1.77M in 2026 (AirDNA via [StayFi](https://stayfi.com/vrm-insider/2026/04/20/vacation-rental-statistics/)); AirDNA cut 2026 supply growth to 2.7% ([PR Newswire](https://www.prnewswire.com/news-releases/steady-demand-and-slower-new-supply-define-us-short-term-rentals-in-2026-airdna-finds-302820776.html)). Airbnb: 9M+ active listings at end of 2025 ([Q4 letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526048670/d58192dex991.htm)).
- Airbnb banned indoor cameras from Apr 30 2024 (doorbell cameras and decibel-only monitors allowed — [Airbnb](https://news.airbnb.com/an-update-on-our-policy-on-security-cameras/)) and issues per-stay lock codes itself ([Airbnb](https://news.airbnb.com/smart-lock-integrations-available-to-all-us-and-canada-hosts)).
- Competitors: Minut ($20M Series B), NoiseAware → Rest, Operto (bought Dack), RemoteLock, Guesty lock manager.
- **Gap:** lock codes are commoditized; hardware-free party detection (doorbell entry count vs booked guests) is open, but Minut on the Ring Appstore is the one to beat.

### Package theft (not shortlisted — detection is taken)

- ≥ 58M packages stolen and up to $16B lost in 2024 (Security.org figures cited by the [USPS OIG](https://www.uspsoig.gov/sites/default/files/reports/2025-05/RISC-WP-25-002.pdf), which notes "no single authoritative source"); SafeWise: 104.3M packages, $14.9B, year to Aug 2025 ([SafeWise](https://www.safewise.com/blog/metro-areas-porch-theft/)).
- Detection is common (Ring and Nest package alerts, Package Protect on the Ring Appstore). **Open angle:** the post-theft evidence pack for carrier/retailer claims and police reports.

### Small-business front door → P3 Front Desk

- Visitor-management systems: $2.16B (2025) → $6.77B (2034), 13.6% CAGR, Envoy ~14% share — analyst estimate ([Fortune Business Insights](https://www.fortunebusinessinsights.com/visitor-management-system-vms-market-105882)).
- Verkada: $5.8B valuation, > $1B annualized bookings, 30K customers ([CNBC, Dec 2025](https://www.cnbc.com/2025/12/03/verkada-capitalg-valuation-security.html)); Spot AI > $110M raised, channel-only from May 2026 ([Spot AI](https://www.spot.ai/blog/spot-ai-goes-100-channel-launches-industry-first-2m-equity-program-as-video-ai-evolves-from-task-completion-to-full-ai-coworker)); [Ring for Business](https://ring.com/collections/security-cams-rfb); Ring Virtual Security Guard $99/mo per location ([review](https://www.cunninghamsecurity.com/ring-virtual-security-guard-review/)).
- **Gap:** no self-serve visitor check-in or after-hours AI summary for micro-businesses on Ring; no visitor-management app among the Appstore launch apps.

### DIY smart home → P2 Ring Bridge for Home Assistant

- 691,885 opt-in Home Assistant installs vs 514,553 a year earlier (+34%) ([analytics](https://analytics.home-assistant.io/data.json)); "over 2M" installs total ([HA](https://www.home-assistant.io/blog/2025/04/16/state-of-the-open-home-recap/)).
- Ring integration: 34,495 installs (6.3% of reporting installs), Bronze quality, cloud polling ([integration](https://www.home-assistant.io/integrations/ring/)); a forum thread calls it "abandoned" ([forum](https://community.home-assistant.io/t/ring-integration-abandoned-iso-dev-to-submit-existing-pr-ready-since-nov-2025/978712)).
- Unofficial libraries: dgreif/ring 1,523★, ring-mqtt 792★, python-ring-doorbell 699★.
- **Gap:** an open-source bridge on the official API. Whether Ring permits personal-use/open-source apps is UNVERIFIED (Private Apps for ≤ 10 accounts is the likely path).

### At-home physical therapy → P9 HomePT

- US MSK direct spending $661B (2023), ~$1.3T with indirect costs; Hinge's addressable market ~$27B (company estimates, [Hinge prospectus](https://www.sec.gov/Archives/edgar/data/1673743/000119312525125262/d829170d424b4.htm)).
- Hinge Health: IPO May 2025 at $32; Q2 2026 revenue $213M (+53%); 2026 guidance $856–860M; GAAP-profitable ([Q2 release](https://www.sec.gov/Archives/edgar/data/1673743/000162828026052558/hnge-q2202684xex991.htm)). Sword Health valued at $3B in Jun 2024 ([TechCrunch](https://techcrunch.com/2024/06/04/sword-healths-raises-130m-valuation-3b-ai-physical-therapy/)); later valuation UNVERIFIED. Omada Health IPO'd Jun 2025 with an MSK program.
- RTM codes 98975–98981 cover 16–30 days (98977 = MSK); CPT 2026 and the CMS 2026 fee schedule added 98984/98985 (MSK)/98986 for 2–15 days plus 98979 ([AMA](https://www.ama-assn.org/press-center/ama-press-releases/ama-releases-cpt-2026-code-set), [Federal Register](https://www.federalregister.gov/documents/2025/11/05/2025-19787/medicare-and-medicaid-programs-cy-2026-payment-policies-under-the-physician-fee-schedule-and-other)). Comments quoted in the rule say 98977 requires an FDA-regulated device.
- **Gap:** incumbents sell to employers and plans; short-episode codes make RTM workable for independent PT clinics.

### Senior-friendly screens (signal for Fire TV caretaking ideas)

- Families already pay: ElliQ $249 + $39–59/mo ([ElliQ](https://elliq.com/products/elliq)); ViewClix $179–269 + $9.95/mo ([ViewClix](https://www.viewclix.com/shop/)); Alexa Together was $19.99/mo; Alexa+ is $19.99/mo or free with Prime ([Amazon](https://www.aboutamazon.com/news/devices/new-alexa-generative-artificial-intelligence)). Konnekt is often government-subsidized in Australia ([Konnekt](https://www.konnekt.com.au/pricing/)); GrandPad pricing UNVERIFIED.
- **Gap:** check-ins and calling on the TV the senior already owns, managed by family, with no new device.

## Personal, TV, and voice

### AI wearables and memory → P4 Promise Keeper, Bee ideas

- Plaud: 2M+ devices shipped, > $100M subscription ARR, ~50% of device users on paid plans ([TechCrunch, Jun 2026](https://techcrunch.com/2026/06/16/plaud-says-its-software-business-topped-100m-in-arr-after-shipping-over-2m-ai-notetakers/)).
- Consolidation: Amazon bought Bee ($49.99 + $19/mo at the time; $7M raised — [TechCrunch](https://techcrunch.com/2025/07/22/amazon-acquires-bee-the-ai-wearable-that-records-everything-you-say/)); Meta bought Limitless and stopped pendant sales ([CNBC](https://www.cnbc.com/2025/12/05/meta-limitless-ai-wearable.html)); Humane sold assets to HP for $116M ([PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2025/humane-whose-ai-pin-flopped-to-sell-assets-to-hp/)). Friend v2 costs $249 after a 5,000-unit first run ([SF Standard](https://sfstandard.com/2026/08/02/avi-schiffmann-new-ai-friend-can-talk/)); Omi raised $2M (unit sales UNVERIFIED).
- AI-glasses shipments +263% year over year in H1 2026; Meta holds 94% of the display-less segment (Counterpoint via [9to5Mac](https://9to5mac.com/2026/09/21/report-ai-glasses-shipments-surged-263-in-h1-2026-as-apple-prepares-to-enter-the-market/)) — analyst data.
- **Gap:** recording is a commodity; *using* that memory (actions, home surfaces) with visible privacy controls is not owned.

### AI meeting notetakers → P4

- Otter: $100M ARR, 35M users, 1B+ meetings ([Otter, Dec 2025](https://otter.ai/blog/otter-ai-caps-transformational-2025-with-100m-arr-milestone-industry-first-ai-meeting-agents-and-global-enterprise-expansion)). Fireflies: $1B valuation, 20M users, profitable (secondary source: [UrbanGeekz](https://urbangeekz.com/2025/06/fireflies-ai-unicorn-status-perplexity/)). Granola: $125M at $1.5B ([TechCrunch, Mar 2026](https://techcrunch.com/2026/03/25/granola-raises-125m-hits-1-5b-valuation-as-it-expands-from-meeting-notetaker-to-enterprise-ai-app/)). Fathom (400K MAU) acquired by Superhuman ([TechCrunch, Sep 2026](https://techcrunch.com/2026/09/14/superhuman-acquires-yc-backed-notetaker-fathom-as-productivity-platforms-push-for-agentic-work/)).
- **Gap:** video-call notes are saturated; in-person conversations and notes → tracked actions across tools are open.

### Personal CRM → P4 (follow-ups)

- Clay acquired by Automattic after raising > $9M ([TechCrunch](https://techcrunch.com/2025/06/12/automattic-acquires-relationship-manager-clay-to-add-an-identity-layer-to-online-tools/)), now "Mesh" at $19.99/mo or $119.99/yr ([App Store](https://apps.apple.com/us/app/mesh-contacts-crm/id1463073824)); open-source Monica has 25.4k★ ([GitHub](https://github.com/monicahq/monica)); Dex metrics UNVERIFIED.
- **Gap:** manual data entry is why people quit — passive capture (Bee) removes it.

### Developer status reporting and ADRs → P5 Decision Ledger

- 50% of developers lose 10+ hours/week to organizational inefficiency; "finding information" is the top friction ([Atlassian DevEx 2025](https://www.atlassian.com/blog/developer/developer-experience-report-2025), 3,500 respondents). 84% use or plan to use AI tools, but 46% distrust its accuracy ([Stack Overflow 2025](https://survey.stackoverflow.co/2025/ai)).
- Incumbents: Atlassian Rovo (80%+ of the Fortune 500; Atlassian MCP + CLI passed 1M MAU — [Q4 FY26 letter](https://www.atlassian.com/blog/company-news/shareholder-letter-q4fy26)); Linear ($1.25B, 15,000+ customers — [Linear](https://linear.app/now/building-our-way)); Geekbot ($2.50/participant/mo, ships an MCP server — [pricing](https://geekbot.com/pricing/)).
- ADRs: adr-tools 5.7k★ ([GitHub](https://github.com/npryce/adr-tools)); the UK GDS ADR framework (Dec 2025) is required for Technical Design Council submissions ([GDS](https://technology.blog.gov.uk/2025/12/08/the-architecture-decision-record-adr-framework-making-better-technology-decisions-across-the-public-sector/)).
- **Gap:** each incumbent summarizes only its own tool; decisions made out loud are captured nowhere.

### Student study tools → P6 Lecture Loop

- Quizlet: 60M+ users, reaches 2 in 3 US high schoolers, acquired Coconote on Feb 5 2026 ([PR Newswire](https://www.prnewswire.com/news-releases/quizlet-supercharges-studying-with-new-product-innovations-and-strategic-acquisition-302679622.html)). Turbo AI: 5M users, eight-figure ARR ([TechCrunch](https://techcrunch.com/2025/10/23/20-year-old-dropouts-built-ai-notetaker-turbo-ai-to-5-million-users/)). Chegg Q2 2026 revenue $51.8M, −51% ([SEC](https://www.sec.gov/Archives/edgar/data/0001364954/000136495426000085/a9901-financialresultsq220.htm)). Anki used by 86.2% of US medical students in a 2024 study (secondary: [Wikipedia](https://en.wikipedia.org/wiki/Anki_(software))).
- Free substitutes: [ChatGPT study mode](https://openai.com/index/chatgpt-study-mode/), Gemini guided learning plus a free AI Pro year for students ([TechCrunch](https://techcrunch.com/2025/08/06/google-takes-on-chatgpts-study-mode-with-new-guided-learning-tool-in-gemini/)).
- **Gap:** lecture → notes is commoditized and consolidating; retention (spaced repetition) via voice or TV review is open.

### Life-story and memoir services → P7 Hearthside

- Storyworth: 1M+ books printed since 2013; $69 / $99 / $199 plans ([about](https://welcome.storyworth.com/what-is-storyworth), [pricing](https://welcome.storyworth.com/storyworth-pricing)). Remento: $99/yr, $300K from Mark Cuban on Shark Tank (Mar 2025 — [Yahoo Finance](https://finance.yahoo.com/news/remento-lands-deal-mark-cuban-130000571.html)). StoryKeeper: $99 or $139 one-time, 12,000+ books ([StoryKeeper](https://storykeeper.com/)). Total market size UNVERIFIED.
- **Gap:** every service needs app, email, or call setup; a zero-setup voice interviewer on the elder's existing Echo doesn't exist.

### Connected fitness and camera form coaching → W2 Rep Vision, P9 HomePT

- Peloton FY26: $2.446B revenue, first annual profit ($63M), connected-fitness subscriptions 2.553M (−8.8%) (secondary: [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/peloton-pton-turns-corner-subscribers-105159091.html)). Peloton IQ camera form feedback and rep counting only on premium "Plus" machines ([Peloton](https://investor.onepeloton.com/news-releases/news-release-details/peloton-enters-new-era-ai-powered-peloton-iq-and-new-product)).
- Apple Fitness+ "under review" with layoffs ([MacRumors](https://www.macrumors.com/2026/02/08/apple-fitness-remains-under-review/), [9to5Mac](https://9to5mac.com/2026/09/21/apple-fitness-team-hit-by-layoffs-as-major-changes-reportedly-loom/)); Tempo moved to "Tempo Move" on the user's own TV ([GarageGymReviews](https://www.garagegymreviews.com/tonal-vs-tempo)); Zing Coach $10M Series A ([Athletech News](https://athletechnews.com/zing-coach-raises-10m-for-feature-packed-ai-fitness-app/)); Kemtai $5.8M total ([Crunchbase](https://www.crunchbase.com/organization/kemtai)).
- **Gap:** camera form coaching at app pricing on the TV people already own.

### TV party games with phone controllers → W4 Living Room Arena

- Jackbox: 826M+ player joins since Dec 2022 ([announcement](https://www.mkaugaming.com/the-party-returns-to-tens-of-millions-of-players-jackbox-games-announces-the-jackbox-party-pack-12/)); AirConsole 18M+ players ([AirConsole](https://corp.airconsole.com/)); Netflix TV party games with phone controllers from Nov 13 2025 ([NBC News](https://www.nbcnews.com/pop-culture/pop-culture-news/netflix-games-announcement-rcna243613)); **Amazon Luna GameNight: 45+ phone-controlled games on Fire TV, included with Prime** ([Amazon](https://www.aboutamazon.com/news/entertainment/what-is-amazon-luna)).
- **Gap:** fixed content packs; AI-generated personal rounds are open.

### Sports second screen → P11 Rookie Mode

- 77% of fans do a game-related second activity while watching at home ([Deloitte 2023](https://www.deloitte.com/us/en/insights/industry/sports/immersive-sports-fandom.html), 3,004 fans); 26% often can't tell which service carries an event ([Nielsen/Gracenote, Sep 2026](https://www.nielsen.com/news-center/2026/gracenote-study-85-of-sports-fans-want-tv-home-screens-to-show-when-and-where-to-watch-favorite-teams/)).
- Prime Video Thursday Night Football averaged 15.3M viewers in 2025 (+16%), 122M unique viewers ([Amazon Ads](https://advertising.amazon.com/library/news/prime-video-tnf-2025-viewership-advertising)); streaming reached a record 49.0% of US TV viewing in Jul 2026 ([Nielsen](https://www.nielsen.com/news-center/2026/tv-usage-kicks-usual-summer-slowdown-fueled-by-world-cup-and-streaming-in-nielsens-july-gauge-reports/)).
- **Gap:** an AI co-viewer on the TV itself — explainers, catch-up recaps, where-to-watch.

### Agentic and voice commerce for small businesses → M6 (moonshot)

- 36.2M US small businesses, ~29.8M with no employees ([SBA Advocacy](https://advocacy.sba.gov/2025/06/30/new-advocacy-report-shows-the-number-of-small-businesses-in-the-u-s-exceeds-36-million/), [state profile](https://advocacy.sba.gov/wp-content/uploads/2025/06/United_States_2025-State-Profile.pdf)).
- 2030 forecasts (analyst estimates): McKinsey up to $1T US / $3–5T global ([Digital Commerce 360](https://www.digitalcommerce360.com/2025/10/20/mckinsey-forecast-5-trillion-agentic-commerce-sales-2030/)); Morgan Stanley $190–385B ([Morgan Stanley](https://www.morganstanley.com/insights/articles/agentic-commerce-market-impact-outlook)); Bain $300–500B ([Bain](https://www.bain.com/insights/2030-forecast-how-agentic-ai-will-reshape-us-retail-snap-chart/)).
- Slang AI: $36M Series B, 2,000+ restaurant locations, 25M+ calls ([Slang](https://www.slang.ai/post/series-b)); Loman $3.5M seed ([Antler](https://www.antler.co/press-releases/loman-ai-raises-3-5-million-to-transform-restaurant-operations-with-voice-ai)). Alexa for Shopping active users "close to doubling" year over year ([Amazon Q2 2026](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/default.aspx)).
- **Gap:** ~30M solo operators have no cheap way to become "agent-ready".

### MCP ecosystem → P10 Voicecheck

- 10,000+ active public MCP servers and 97M+ monthly SDK downloads as of Dec 9 2025; MCP donated to the Linux Foundation's Agentic AI Foundation ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)).
- Official registry on Oct 1 2026: 38,255 servers (latest versions) from 22,443 publishers; the four largest bulk publishers account for ~6,000 ([registry API](https://registry.modelcontextprotocol.io/v0/servers?version=latest), counted by our research agent).
- Alexa+ accepts brands' own MCP servers since Jul 23 2026 on spec 2025-11-25 ([Amazon](https://developer.amazon.com/alexaplus/blogs/2026/07/alexa-plus-new-ways-to-build-experiences)).
- **Gap:** no quality bar — conformance, security, voice-readiness, and observability testing are open.

### Platform reach (for Potential Impact claims)

- Fire TV: 250M+ devices worldwide (undated page — [Amazon](https://developer.amazon.com/fire-tv)).
- Alexa: 600M+ devices ([Amazon](https://www.aboutamazon.com/news/devices/new-alexa-generative-artificial-intelligence)); Alexa+ is US-wide, free with Prime or $19.99/mo, after "tens of millions" joined Early Access ([Amazon](https://www.aboutamazon.com/news/devices/alexa-plus-available-free-prime-members-us)); customers talk to Alexa+ on Fire TV ~2× more than to the original Alexa ([Amazon](https://www.aboutamazon.com/news/devices/alexa-plus-fire-tv-free-ai)). No standalone Alexa+ user count found.
- Ring: > 100M cameras in the field ([TechCrunch](https://techcrunch.com/2026/03/31/ring-app-store-bets-on-ai-to-go-beyond-home-security/)).

## Caveats

- Web-search quotas ran out partway through; later facts were confirmed by fetching primary pages directly. Newer figures may exist.
- Secondary sources are named where used (Peloton via Yahoo Finance, Fireflies via UrbanGeekz, Tempo via GarageGymReviews, Kemtai via Crunchbase, Anki via Wikipedia, AirDNA via StayFi).
