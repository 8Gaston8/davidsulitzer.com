---
name: user-interview
description: Simulate data-driven user interviews for product insights, feature feedback, or design testing
disable-model-invocation: true
---
# user-interview

Simulate realistic user interviews grounded in real product data. Adapts to three modes depending on what you need.

> **Default product scope: davidsulitzer.com.** All interviews, personas, and data queries should focus on the davidsulitzer.com product (local discovery, smart search, curated spots) unless the user explicitly asks about Gluten Free Eats (GFE). If the user mentions GFE, celiac, gluten-free, or dietary safety, switch to GFE-specific personas and data. When in doubt, ask.

**Usage examples:**
- `@user-interview` — "I want to understand why trial users churn"
- `@user-interview` — "How would users react to a weekly recommendation email?"
- `@user-interview` — "Here's the new onboarding design — simulate a user going through it"

---

## Step 1: Determine the Interview Mode

Based on what the user asks, pick the right mode:

| Mode | Trigger | Purpose |
|------|---------|---------|
| **Exploratory** | Open-ended question, no specific feature | Understand user segments, generate hypotheses |
| **Feature Feedback** | Specific feature or product change mentioned | Simulate reactions to a proposed change |
| **Design Testing** | Design/screenshot/mockup provided or referenced | Simulate users experiencing a specific flow |

> If unclear, ask: "Are you exploring broadly, testing a specific feature idea, or validating a design?"

---

## Step 2: Gather Real Data

**This is what makes the interviews valuable.** Before simulating ANYTHING, pull real data from every available source.

> ### ⚠️ Cloud Agent? Use APIs Instead of MCP
>
> If you are running as a **cloud agent** (headless environment, no MCP tools available), you **MUST** use REST APIs with credentials from environment variable secrets instead of MCP tools. All required API keys are available via **Cursor Dashboard → Cloud Agents → Secrets** and are injected as environment variables.
>
> | Data Source | MCP Tool (Local) | Cloud Agent Alternative | Secret / Env Var |
> |-------------|-------------------|------------------------|------------------|
> | **Mixpanel** | `run_segmentation_query` etc. | [Mixpanel Query API](https://developer.mixpanel.com/reference/query-api) | `MIXPANEL_API_SECRET` |
> | **MongoDB** | Atlas MCP tools | [MongoDB Atlas Data API](https://www.mongodb.com/docs/atlas/app-services/data-api/) | `MONGODB_ATLAS_API_KEY`, `MONGODB_APP_ID` |
> | **Crisp** | Shell (API) | [Crisp REST API](https://docs.crisp.chat/references/rest-api/v1/) | `CRISP_API_ID`, `CRISP_API_KEY` |
> | **App Store** | Shell (JWT) | [App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi) | `APP_STORE_CONNECT_KEY_ID`, `APP_STORE_CONNECT_ISSUER_ID`, `APP_STORE_CONNECT_PRIVATE_KEY` |
> | **Slack** | Slack MCP | [Slack Web API](https://api.slack.com/web) | `SLACK_BOT_TOKEN` |
>
> **Important:** The local `.env` file at `davidsulitzer.com/api/.env` is **NOT available** in cloud agent environments. Always use secrets. If a secret is missing, ask the user to add it in the Cursor Dashboard.
>
> Example (Mixpanel segmentation in cloud):
> ```bash
> curl -X POST "https://mixpanel.com/api/2.0/segmentation" \
>   -u "$MIXPANEL_API_SECRET:" \
>   -d '{"event": "app_search_initiated", "from_date": "2026-01-01", "to_date": "2026-02-09"}'
> ```
>
> Example (MongoDB Atlas Data API in cloud):
> ```bash
> curl -X POST "https://data.mongodb-api.com/app/$MONGODB_APP_ID/endpoint/data/v1/action/find" \
>   -H "api-key: $MONGODB_ATLAS_API_KEY" \
>   -H "Content-Type: application/json" \
>   -d '{"dataSource": "production", "database": "prod", "collection": "userFeedback", "filter": {}, "limit": 50}'
> ```
>
> **When a data source is inaccessible:** Don't silently skip it. Explicitly note in the report: "Could not access [source] — [reason]. Confidence scores adjusted accordingly."

### 2a. Mixpanel — Behavioral Data (Project ID: <YOUR_MIXPANEL_PROJECT_ID>)

Pull data relevant to the interview topic. Choose from:

**Segmentation** — Understand user behavior patterns:
```
run_segmentation_query with project_id: <YOUR_MIXPANEL_PROJECT_ID>
```
Useful queries:
- Event frequency by user cohort (e.g., how often do trial users search?)
- Feature usage distribution (e.g., what % of users save places?)
- Drop-off points in key flows

**Funnels** — Understand conversion:
```
run_funnels_query with project_id: <YOUR_MIXPANEL_PROJECT_ID>
```
Useful funnels:
- Pricing Screen → Trial Start → Trial Converted
- App Open → Search → Place Profile View → Save
- Trial Start → Session 2 → Session 3 (retention)

**Retention** — Understand stickiness:
```
run_retention_query with project_id: <YOUR_MIXPANEL_PROJECT_ID>
```
Useful queries:
- Day 1 / Day 3 / Day 7 retention by cohort
- Retention by acquisition source
- Feature-correlated retention (users who saved vs didn't)

**Frequency** — Understand usage patterns:
```
run_frequency_query with project_id: <YOUR_MIXPANEL_PROJECT_ID>
```
Useful queries:
- Sessions per week distribution
- Search frequency during trial
- Save frequency by subscription status

**User Properties** — Understand who they are:
```
get_property_values with project_id: <YOUR_MIXPANEL_PROJECT_ID>, resource_type: "User"
```
Key properties to check:
- `$country_code`, `$city` — geography
- `product` — which product they use (filter for davidsulitzer.com by default)
- `abi_onboarding_type` — how they arrived
- `gfe_sensitivity` — GFE sensitivity level (only relevant if interviewing GFE users)

### 2b. MongoDB Atlas — User & Content Data (Database: prod)

Pull data relevant to the interview topic:

**User feedback & reviews:**
```
Collection: userFeedback — Direct user feedback
Collection: reviews — Place reviews (shows what users value)
Collection: userState — Subscription/engagement state
```

**Engagement signals:**
```
Collection: saveListItems — What users save (investment behavior)
Collection: stepLikes — What users like
Collection: mapfollowers — Community engagement
Collection: viewsCount — Browsing patterns
```

**Content quality:**
```
Collection: steps — Places/locations in the app
Collection: maps — Available maps
Collection: details — Place details (what info we show)
```

**Churn signals:**
```
Collection: userFeedback — Look for cancellation feedback
Collection: userSubscriptionBypassesForPremiumMaps — Trial behavior
```

### 2c. App Store Reviews

Pull recent App Store reviews using the App Store Connect API:

```bash
# Generate JWT token for App Store Connect
source .env

# Get recent reviews (requires JWT auth — see App Store Connect API docs)
# Look for: complaints, praise, feature requests, frustrations
```

Alternative: Search the web for recent davidsulitzer.com reviews:
```
Search: "davidsulitzer.com app" review site:apps.apple.com OR site:play.google.com
```

### 2d. Support Conversations — Crisp

Check recent support conversations for common themes:

```bash
# Crisp API — get recent conversations
# Website ID: 51f0b9f1-c96c-452a-8e15-e437101d7d80
# Look for: recurring complaints, feature requests, confusion points
```

### 2e. Slack — Internal Signals

Check bug reports and feedback channels:
```
Channel: #bugs-mobile-apps (CS93RCDSB) — User-reported issues via Julia
```

### 2f. Codebase — Product Context

**Always** read relevant code to understand:
- The actual user flow being discussed (not assumptions!)
- What the user sees, taps, and experiences
- Feature flags and A/B tests currently running
- Paywall/subscription logic
- Onboarding flows and their variations

Key areas:
- `davidsulitzer.com/Steps/AppFlows/` — All user flows
- `davidsulitzer.com/Steps/AppFlows/Paywall/` — Pricing/trial logic
- `davidsulitzer.com/Steps/AppFlows/Onboarding/` — First-time experience
- `davidsulitzer.com/Steps/AppFlows/Retention/` — Churn/cancellation flow
- `davidsulitzer.com/api/businessLogic/` — Backend logic for features

### 2g. Competitor Landscape

**Always** check what alternatives the simulated user has. Personas don't exist in a vacuum — they're comparing davidsulitzer.com to real alternatives.

Search the web for recent competitor features and reviews:
```
Search: "Google Maps" OR "Yelp" OR "TripAdvisor" OR "Foursquare" [topic relevant to interview]
Search: "best restaurant discovery app 2026"
```

Key competitors to benchmark against:
| Competitor | What They Offer | davidsulitzer.com's Differentiation |
|------------|----------------|----------------------|
| **Google Maps** | Universal coverage, reviews at scale, AI summaries | davidsulitzer.com: curated quality > quantity, community maps, smart vibe-based search |
| **Yelp** | Review volume, photos, reservations | davidsulitzer.com: less noise, no sponsored results, real community curation |
| **TripAdvisor** | Travel-focused, hotel + restaurant combo | davidsulitzer.com: local-first (not tourist-first), daily use not just travel |
| **Instagram/TikTok** | Social discovery, viral food content | davidsulitzer.com: searchable + saveable, not ephemeral scroll |
| **Friends/Word of mouth** | Trusted, personal, free | davidsulitzer.com: scales the "friend who knows a spot" feeling |

**Use this in interviews:** When a persona says "I could find this elsewhere," push back with specifics. WHAT would they use? What's the actual experience on that alternative? Make the comparison concrete, not vague.

### 2h. GitHub Projects — Roadmap & Product Context

Check both GitHub Projects for relevant context on what's planned, in progress, or ideated:

**davidsulitzer.com Project** (number: 2, ID: `<YOUR_PROJECT_ID>`) — Active development work:
```bash
# List recent items with status
gh project item-list 2 --owner 8Gaston8 --limit 30
```
Look for: items In Development, Todo, or Done that relate to the interview topic.

**davidsulitzer.com Ideation Lab** (number: 4, ID: `PVT_kwDOBluP0c4BOk4F`) — Ideas and experiments:
```bash
# List ideation items
gh project item-list 4 --owner 8Gaston8 --limit 30
```
Look for: feature ideas, experiments, and hypotheses that relate to the interview topic.

Also search GitHub issues directly for relevant context:
```bash
gh search issues "<topic keywords>" --repo 8Gaston8/davidsulitzer.com --state all
```

---

## Step 3: Build Data-Grounded Personas

Based on the data gathered, build 2-4 personas that represent REAL behavioral segments.

### Persona Template

For each persona, specify:

```markdown
## Persona: "[Name]"
**Segment:** [What real data segment they represent]
**Data basis:** [Specific Mixpanel/MongoDB data that shaped this persona]

| Attribute | Details | Data Source |
|-----------|---------|-------------|
| Demographics | [Age, location, lifestyle] | Mixpanel geo data |
| Behavior pattern | [How they use the app — frequency, features, timing] | Mixpanel events |
| Subscription status | [Trial, converted, churned, never started] | MongoDB userState |
| Key actions | [Searches, saves, visits, reviews] | Mixpanel + MongoDB |
| Pain points | [From reviews, feedback, support tickets] | App Store + Crisp |
| Motivation | [Why they downloaded, what they hope for] | Onboarding data |
```

### Persona Selection by Mode

| Mode | Personas to Build |
|------|-------------------|
| **Exploratory** | Cover 3-4 segments: a converter, a churner, a power user, and an edge case |
| **Feature Feedback** | 2-3 personas most affected by the proposed feature |
| **Design Testing** | 2 personas: one tech-savvy, one less experienced with apps |

---

## Step 4: Run the Simulated Interviews

### Interview Structure

Each interview should follow this format:

1. **Context setting** — Who they are, how they found the app
2. **Experience narrative** — Walk through their actual journey (grounded in real product flow!)
3. **Key moment** — The critical point where they converted/churned/got stuck
4. **Probing questions** — Deep dive into motivations and frustrations
5. **Forward-looking** — What would change their behavior

### Mode-Specific Interview Approaches

#### Exploratory Mode
- Open-ended questions about their experience
- Focus on emotional journey, not just functional
- Probe for unmet needs and surprising behaviors
- Ask: "What would make this indispensable to you?"

#### Feature Feedback Mode
- Describe the proposed feature mid-interview
- Capture initial reaction (excitement, confusion, indifference)
- Probe for edge cases: "What if [scenario]?"
- Ask: "Would this change how often you use the app?"
- Ask: "Would this have changed your decision to [subscribe/cancel]?"

#### Design Testing Mode
- Walk the persona through the design step by step
- Capture first impressions at each screen/state
- Note confusion points: "What do you think this button does?"
- Test comprehension: "What would you do next?"
- Identify emotional reactions: excitement, trust, skepticism, frustration

### Realism Guidelines

- **Use natural speech** — contractions, hesitation, tangents (real people don't speak in bullet points)
- **Include "I don't know" moments** — real users aren't always articulate about their needs
- **Show contradictions** — people say one thing and do another (e.g., "I love discovering places" but saves 0 places)
- **Ground in ACTUAL product behavior** — reference real screens, real flows, real pricing ($12/month)
- **Vary emotional states** — some users are enthusiastic, some are apathetic, some are frustrated
- **Inject real user quotes** — When you pulled App Store reviews, Crisp tickets, or MongoDB feedback in Step 2, weave those ACTUAL words into the simulated persona's dialogue. Mark them clearly:

  > **Example:** The persona says *"I don't use it often enough to justify paying"* — and you note: `[echoes real churn reason: "dont_use_often_enough" — selected by X% of cancelers]`

  This makes the simulation tangibly grounded. If you found a 1-star review saying "I searched for brunch and got 3 results," have the persona express that frustration in their own words. Tag it:
  
  > `[mirrors App Store review, 2 stars, Jan 2026: "searched for brunch spots and barely got any results"]`

  **The goal:** Anyone reading the simulation can immediately see which parts are data-backed and which are AI extrapolation.

---

## Step 5: Synthesize Insights

After running all interviews, produce a structured synthesis:

### Comparison Table

```markdown
| Factor | [Persona 1] | [Persona 2] | [Persona 3] |
|--------|-------------|-------------|-------------|
| First impression | ... | ... | ... |
| Key value moment | ... | ... | ... |
| Biggest friction | ... | ... | ... |
| Would they pay? | ... | ... | ... |
| Usage frequency | ... | ... | ... |
```

### Hypotheses (with Confidence Scoring)

Generate 3-5 testable hypotheses based on the interviews. **Every hypothesis MUST have a confidence level** so the user knows what to trust vs. what to validate first:

| Confidence | Meaning | When to Use |
|------------|---------|-------------|
| 🟢 **High** | Backed by real data (Mixpanel numbers, actual reviews, MongoDB patterns) | Hypothesis directly supported by quantitative evidence |
| 🟡 **Medium** | Supported by qualitative signals (support tickets, a few reviews, codebase patterns) | Some real-world backing but not statistically rigorous |
| 🔴 **Low** | Speculative — AI extrapolation, no direct data found | Plausible reasoning but no evidence yet; validate first |

```markdown
| # | Hypothesis | Confidence | Supporting Evidence | How to Validate |
|---|-----------|------------|-------------------|-----------------|
| 1 | [Statement] | 🟢/🟡/🔴 | [Data source + what it showed] | [Mixpanel query / real interview question / A/B test] |
```

> **Rule:** If more than half your hypotheses are 🔴, explicitly call that out: "Most of these insights are speculative — real user interviews should be the priority before acting on them."

### Impact on Key Metrics

Connect insights back to Q1 2026 goals:

**North Star:** $1M ARR for davidsulitzer.com

| Metric | Current | Insight Impact | Suggested Action |
|--------|---------|---------------|-----------------|
| Pricing → Trial Start (goal: 20-25%) | [Pull from Mixpanel] | [How insights relate] | [Specific change] |
| Trial → Converted (goal: 35-40%) | [Pull from Mixpanel] | [How insights relate] | [Specific change] |
| Activation Rate (goal: 60%) | [Pull from Mixpanel] | [How insights relate] | [Specific change] |
| Early Retention (goal: 40%) | [Pull from Mixpanel] | [How insights relate] | [Specific change] |
| Investment Rate (goal: 10%) | [Pull from Mixpanel] | [How insights relate] | [Specific change] |

---

## Step 6: Generate Actionable Outputs

Based on the mode, produce the right deliverable:

### Exploratory Mode → Interview Guide
Generate a real-user interview question guide:

```markdown
## Interview Guide: [Topic]
**Target segment:** [Who to recruit]
**Session length:** 30 min

### Warm-up (5 min)
1. [Question about their life/context]
2. [Question about how they find places today]

### Core Questions (20 min)
3. [Probing question derived from simulation insight #1]
4. [Probing question derived from simulation insight #2]
...

### Wrap-up (5 min)
8. "If you could change one thing about davidsulitzer.com..."
9. "Would you recommend davidsulitzer.com to a friend? Why/why not?"
```

### Feature Feedback Mode → Decision Brief
```markdown
## Feature Decision Brief: [Feature Name]

### Verdict: 🟢 Build / 🟡 Iterate / 🔴 Rethink

**Summary:** [One paragraph]

### User Reception
| Persona | Reaction | Risk |
|---------|----------|------|
| ... | ... | ... |

### Recommendations
1. [If building: specific implementation suggestions]
2. [If iterating: what to change first]
3. [If rethinking: alternative approaches]

### Questions to Validate with Real Users
1. [Most critical assumption to test]
2. ...
```

### Design Testing Mode → Usability Report
```markdown
## Usability Report: [Design Name]

### Overall Score: X/5

### Screen-by-Screen Findings
| Screen | Comprehension | Emotional Reaction | Issues Found |
|--------|--------------|-------------------|--------------|
| ... | ... | ... | ... |

### Critical Issues (Fix Before Ship)
1. [Issue + which persona hit it + severity]

### Recommendations
1. [Specific design change]
2. ...
```

---

## Step 7: Generate HTML Report

**MANDATORY.** In addition to any markdown output, you MUST generate a self-contained HTML report file that makes the entire interview simulation comfortable to read in a browser. This is the primary deliverable — the thing Gaston will actually read.

### Requirements
- **Single file, zero dependencies** — all CSS must be inline in a `<style>` tag. Load only Google Fonts (`Inter` + `Fraunces`) via `@import`. No JavaScript required.
- **Save to workspace** — name it `user-interview-report-[topic].html` (e.g., `user-interview-report-smart-queries.html`)
- **Responsive** — must read well on both desktop and phone

### Mandatory Sections in the HTML Report

1. **Hero header** — dark gradient background, report title, mode badge (Exploratory / Feature Feedback / Design Testing), date, persona count, hypothesis count, verdict
2. **Table of contents** — clickable anchor links to all sections, 2-column grid layout
3. **Data Sources table** — which sources were accessed vs. which were unavailable (with status indicators)
4. **Feature Deep Dive** (if Feature Feedback or Design Testing mode) — numbered change cards
5. **Persona cards** — each persona as a styled card with colored avatar, demographics table, behavior, pain points, data basis
6. **Full interview transcripts** — this is the heart of the report:
   - Style as alternating chat-style dialogues (interviewer on white, persona on cream/alt background)
   - Speaker labels color-coded (blue for interviewer, orange/accent for persona)
   - Data-grounded annotations as blue callout boxes with left border (linking each insight to its codebase/data source)
   - Italic text for stage directions like *(pauses)*, *(leans forward)*
7. **Synthesis comparison table** — all personas side by side
8. **Hypothesis cards** — each hypothesis as a card with confidence badge (green/yellow/red), evidence summary, and validation method
9. **Metric impact cards** — one per key metric with impact severity tag (Strong/Moderate/Weak/Neutral)
10. **Verdict banner** (if Feature Feedback mode) — green/yellow/red with icon and summary
11. **Recommendations** — grouped by timeline (Ship Now / Quick Wins / Medium-Term / Watch Closely) with colored dot indicators
12. **Interview guide** — numbered question cards for running real interviews
13. **Follow-up suggestions** — action cards for next steps
14. **Footer** — caveat about simulations being hypotheses, generation date

### Design Tokens (Use These)

```css
/* Colors */
--bg: #FAFAF8;            /* Page background */
--surface: #FFFFFF;        /* Cards */
--surface-alt: #F5F3EF;   /* Alternating rows, persona responses */
--accent: #E86C3A;         /* Primary accent (orange) */
--blue: #3B6BCC;           /* Interviewer, annotations */
--green: #2E7D56;          /* High confidence, ship it */
--yellow: #C4930A;         /* Medium confidence */
--red: #C0392B;            /* Low confidence, watch */

/* Typography */
font-family: 'Inter', -apple-system, sans-serif;       /* Body */
font-family: 'Fraunces', Georgia, serif;                /* Headlines */

/* Spacing */
border-radius: 12px (cards), 20px (large cards);
max-width: 820px (content container);
```

### Example Structure (Abbreviated)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Topic] — User Interview Simulation</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&display=swap');
    /* ... all styles inline ... */
  </style>
</head>
<body>
  <header class="hero"><!-- dark gradient, title, badges --></header>
  <nav class="toc"><!-- clickable table of contents --></nav>
  <div class="container">
    <section id="data-sources"><!-- data source table --></section>
    <section id="feature"><!-- feature deep dive cards --></section>
    <section id="personas"><!-- persona cards --></section>
    <section id="interview-1"><!-- full transcript as dialogue --></section>
    <section id="interview-2"><!-- ... --></section>
    <section id="synthesis"><!-- comparison table --></section>
    <section id="hypotheses"><!-- hypothesis cards with badges --></section>
    <section id="metrics"><!-- metric impact cards --></section>
    <section id="verdict"><!-- verdict banner + recommendations --></section>
    <section id="guide"><!-- interview guide --></section>
  </div>
  <footer><!-- caveat + date --></footer>
</body>
</html>
```

> **Quality bar:** The HTML report should feel like a premium product research document — the kind of thing you'd send to a CEO and they'd actually read cover to cover. Not a markdown-to-HTML conversion, but a designed reading experience.

---

## Step 8: Offer Follow-ups

> **Reminder:** Before offering follow-ups, make sure you've committed and pushed the HTML report file if running in a git-enabled environment.

After presenting results, suggest next steps:

- **"Want me to simulate another persona?"** — Different segment, different perspective
- **"Want me to draft a GitHub issue for any of these insights?"** — Using `/new-issue` skill
- **"Want me to add an idea to the davidsulitzer.com Ideation Lab?"** — Track hypotheses as ideation items
- **"Want me to pull more specific data on any of these findings?"** — Deeper Mixpanel/MongoDB dive
- **"Should I run this for GFE too?"** — Same framework, but switches to GFE-specific personas, safety concerns, celiac sensitivity levels, and dietary-focused data

---

## Reference: Available Data Sources

| Source | Tool | What It Provides |
|--------|------|-----------------|
| **Mixpanel** | MCP (project_id: <YOUR_MIXPANEL_PROJECT_ID>) | Events, funnels, retention, segmentation, user properties |
| **MongoDB** | Atlas MCP (database: prod) | Users, reviews, feedback, saves, engagement, subscription state |
| **App Store** | Shell (App Store Connect API) | User reviews, ratings, feature requests |
| **Crisp** | Shell (API) | Support conversations, common complaints |
| **Slack** | Slack MCP | Bug reports (#bugs-mobile-apps), internal discussions |
| **GitHub Projects** | `gh project` CLI | davidsulitzer.com project (dev work), davidsulitzer.com Ideation Lab (ideas/experiments) |
| **GitHub Issues** | `gh search issues` | Feature requests, bugs, past decisions |
| **Codebase** | File tools | Actual product flows, screens, logic |
| **Web** | Web search/fetch | Competitor analysis, market context, davidsulitzer.com public pages |

---

## Reference: Key Metrics (Q1 2026)

**North Star:** $1M ARR for davidsulitzer.com

### Top-Down Metrics (Pricing Funnel)
| Metric | Goal |
|--------|------|
| Pricing Screen → Trial Start | 20-25% |
| Trial Start → Trial Converted | 35-40% |

### Leading Indicators
| Metric | Goal | Definition |
|--------|------|------------|
| Activation Rate | 60% | % of new trial users who view 5+ place profiles from multi-category searches in first 7 days |
| Early Retention | 40% | % of trial users with 3+ sessions in first 3 days |
| Investment Rate | 10% | % of trial users who save at least 1 place in first 7 days |

---

## Reference: davidsulitzer.com Primary Personas

These are the baseline personas. Data should refine and override these:

| Persona | Core Need | Key Behavior |
|---------|-----------|-------------|
| **Decision-Fatigued Foodie** | Just tell me where to go | Searches with specific intent, wants fast answers |
| **Urban Explorer** | Discover hidden gems, feel like a local | Browses and saves, wants to impress friends |
| **Vegan User** | Plant-based focus, not afterthought | Cuisine-specific searches, community-oriented |
| **Date Planner** | Impressive, memorable spots | Plans ahead, cares about ambiance/vibe |
| **Frequent Traveler** | Local expertise in unfamiliar cities | Location-based searches, pre-trip planning |
| **Busy Professional** | Fast, reliable answers | Efficiency over exploration, specific intent |

---

## Reference: Churn Reasons (from Retention Flow)

Real cancellation reasons captured in-app:

| Reason | Code | Frequency Insight |
|--------|------|-------------------|
| Too expensive | `too_expensive` | Check Mixpanel for distribution |
| Didn't find relevant places | `didnt_find_relevant_places` | Check Mixpanel for distribution |
| Don't use often enough | `dont_use_often_enough` | Check Mixpanel for distribution |
| Not enough places | `not_enough_places` | Check Mixpanel for distribution |
| Safety concerns | `safety_concerns` | Check Mixpanel for distribution |
| Technical issues/bugs | `technical_issues_bugs` | Check Mixpanel for distribution |
| Other (free text) | `other` | Check MongoDB userFeedback |

---

## Notes

- **Never fabricate data.** If you can't pull real numbers, say "I couldn't access this — here's my best estimate based on [source]."
- **Always read the actual codebase** before describing product flows. Getting the flow wrong undermines the entire simulation.
- **Simulations are hypotheses, not truths.** Always frame outputs as "worth validating" not "definitely true."
- **Real interviews > simulated interviews.** The goal is to sharpen questions and challenge assumptions, not to replace talking to humans.
- **Adapt tone to Gaston** — Keep it casual, witty, and insightful. This is a thinking tool, not a corporate report.
