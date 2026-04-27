---
title: "Vibecoding 024 — Mindful Check-in: A Personal Practice Tracker"
date: 2026-04-26
description: "A daily mindfulness check-in tool with breath, mind, and shift logging — Cloudflare Workers + D1. Now with anytime check-ins, public stats sharing, and a weekly Verbal Judo practice screen."
tags: ["vibecoding", "javascript", "cloudflare", "d1", "mindfulness", "workers"]
aliases: ["/writing/vibecoding-024-mindful-checkin/"]
weight: -24
---

I wanted a check-in tool that matched how I actually think about a mindfulness practice: not a mood tracker with sliding scales, not a journal app with blank pages, but three specific questions asked at specific times of day.

**Live:** [mindful.mrdinesh.workers.dev](https://mindful.mrdinesh.workers.dev)

## The three dimensions

The check-in captures three things each session:

- **Breath** — a quick body scan. Chip options (deep, shallow, held, irregular, easy) plus a free-text override. The question is "how's your breath right now?" rather than "rate your stress 1–10," because the breath answer is immediate and honest.
- **Mind** — mental state. Chips: calm, focused, busy, scattered, anxious, foggy. Again, overridable. The goal is pattern recognition over time, not journaling.
- **Shift** — one micro-action. A free-text field. What's one small thing you can do right now? Not a goal, not a task — a single concrete shift.

Four time slots (Morning / Midday / Evening / Night) with URL hash shortcuts (`#evening`, etc.) so you can bookmark each one separately and get there in one tap.

## Architecture

Started as a pure localStorage app — single HTML file, no server, deploy to Cloudflare Pages.

Then added persistence and stats. The final stack:

| Layer | Tech |
|---|---|
| Hosting + routing | Cloudflare Workers |
| Database | Cloudflare D1 (SQLite) |
| Auth | PIN stored as a Worker secret |
| Frontend | Vanilla HTML/CSS/JS, no framework |

The Worker serves the full app HTML inline (same pattern as [Argus](/writing/vibecoding-012-argus/) and [JuiceSec](/writing/vibecoding-020-juicesec/)), then handles three API routes:

- `POST /api/pin-check` — verify PIN before first access
- `POST /api/checkin` — upsert an entry into D1
- `GET /api/stats` — return streaks, heatmap, slot frequency, top states

Every save goes to localStorage immediately (so it's always fast and works offline), then syncs to D1 in the background. The confirmation screen shows "✓ synced" or "↯ offline — saved locally" depending on the result.

## D1 schema

```sql
CREATE TABLE checkins (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  date         TEXT NOT NULL,
  slot         TEXT NOT NULL,
  saved_at     TEXT NOT NULL,
  breath_chip  TEXT NOT NULL DEFAULT '',
  breath_custom TEXT NOT NULL DEFAULT '',
  mind_chip    TEXT NOT NULL DEFAULT '',
  mind_custom  TEXT NOT NULL DEFAULT '',
  shift        TEXT NOT NULL DEFAULT '',
  UNIQUE(date, slot) ON CONFLICT REPLACE
);
```

One row per slot per day. `UNIQUE(date, slot) ON CONFLICT REPLACE` handles re-saves cleanly — editing a morning check-in just replaces the row.

## Stats screen

The stats view pulls from D1 and shows:

- **Current streak** and **longest streak** — consecutive days with at least one check-in
- **30-day heatmap** — 10×3 grid of squares, coloured by check-in count (0 to 4+)
- **Slot frequency** — which time of day you check in most, as CSS bar charts
- **Top breath and mind states** — ranked by frequency over all time

Streak calculation happens server-side: fetch all distinct dates, walk them in order, track consecutive runs, compare the last run's end date against today/yesterday.

## One sharp edge: template literal escaping

The Worker inlines the full HTML as a JavaScript template literal. Inside that literal, the app's own JavaScript uses single-quoted strings. Any `\'` written in the template literal becomes just `'` in the rendered HTML — the backslash is dropped as an identity escape.

This means `onclick="enterSlot(\'morning\')"` in the template literal becomes `onclick="enterSlot('morning')"` in the browser — which is valid HTML but **not** valid JavaScript inside a single-quoted string literal like `'<button onclick="enterSlot(\'morning\')">...'`.

The fix: use `data-*` attributes instead of string arguments in inline onclick handlers.

```js
// broken
'<button onclick="enterSlot(\'' + s + '\')">...'

// works
'<button data-slot="' + s + '" onclick="enterSlot(this.dataset.slot)">...'
```

Same fix for `selectChip` (already had `data-group` and `data-value`) and `showScreen` (added `data-screen`). Apostrophes in text content switched to `&apos;` HTML entities.

## Deployment

```bash
wrangler d1 create mindful
# paste database_id into wrangler.toml
wrangler d1 execute mindful --remote --file=schema.sql
wrangler secret put MINDFUL_PIN
wrangler deploy
```

PIN lives as a Worker secret — never in the code, never in the URL. The frontend prompts once, stores in localStorage, and sends as an `X-Pin` header on every API request.

---

## v2 — Four updates

### Anytime check-in

The original four slots (Morning / Midday / Evening / Night) were anchored to parts of the day. That left a gap: a moment of friction or clarity at 2pm on a Tuesday doesn't fit neatly into any of them.

There's now a fifth button — **Now ⏱** — that generates a time-stamped slot (`now_HHMM`) on the spot. The UNIQUE `(date, slot)` constraint in D1 handles dedup naturally: tapping Now twice at the same minute just replaces the earlier entry. In the stats screen, all `now_*` entries aggregate under a single "Anytime" row in the slot frequency chart.

### Public stats — shareable read-only view

The stats screen now has a **share ↗** link for the account owner. It copies a `?public=1` URL to the clipboard. Anyone opening that URL skips the PIN screen entirely and lands on a read-only view of the same stats — streaks, heatmap, patterns.

On the worker side, a new route handles this:

```js
async function handlePublicStats(request, env) {
  if (!env.MINDFUL_PUBLIC_STATS) return json({ error: 'Not enabled' }, 403);
  return json(await fetchStats(env));
}
```

The `MINDFUL_PUBLIC_STATS` env var acts as an opt-in switch — sharing is off by default.

```bash
wrangler secret put MINDFUL_PUBLIC_STATS
# enter: true
```

The public view renders the same stats but replaces the back button with a "mindful check-in" credit and hides the share button.

### Daily Verbal Judo tip

I've been reading *Verbal Judo* by George Thompson and wanted something to nudge me toward applying it day-to-day rather than just reading it. A rotating one-liner now appears below the slot grid on the main screen, labelled "verbal judo."

Twenty tips, one per day across the year (day-of-year mod 20):

> *Paraphrase before you reply — prove you listened.*

> *Power is the ability to not respond when you want to.*

> *Always give people a way out that preserves their dignity.*

Same tip all day. No interaction required — just a prompt.

### Weekly practice screen

Tapping **practice** in the footer opens a dedicated screen for the current week's Verbal Judo chapter. Fifteen chapters, rotating by ISO week number.

Each week shows:
- A single **snippet** — one striking sentence from the chapter, displayed as a blockquote
- A **practice card** — one concrete action to carry into the week

```
Week 17 · Chapter 2 of 15
Words as Your Most Powerful Tools

"Your words can escalate or de-escalate before anyone moves."

┌─────────────────────────────────────────┐
│ this week's practice                    │
│                                         │
│ Spot one moment today where a different │
│ word would have changed the temperature.│
└─────────────────────────────────────────┘

Next chapter in 3 days
```

The goal was low friction: open the app, see the week's focus, close it. No reading required — just the one thing to try.
