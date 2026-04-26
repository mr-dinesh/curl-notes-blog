---
title: "Vibecoding 024 — Mindful Check-in: A Personal Practice Tracker"
date: 2026-04-26
description: "A daily mindfulness check-in tool with breath, mind, and shift logging — built as a single-file app with Cloudflare Workers, D1 for persistence, and a stats screen showing streaks and 30-day patterns."
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
