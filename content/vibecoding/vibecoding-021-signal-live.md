---
title: "Vibecoding 021 — SIGNAL/live: A Real-Time Infosec Feed"
date: 2026-04-23
description: "One search box. Two social networks. A live stream of what the infosec community is talking about right now."
tags: ["vibecoding", "security", "cloudflare", "javascript", "mastodon", "bluesky"]
aliases: ["/writing/vibecoding-021-signal-live/"]
---

I have a tab problem. Two social networks — Bluesky and Mastodon — that actually have useful security conversations happening on them, and I kept switching between them to track what was moving. CVE drops, breach coverage, threat intel, people arguing about something Crowdstrike did. Two feeds, two refresh cycles, one set of eyes.

SIGNAL/live is the obvious fix: one search box that watches both at once.

## What it does

Type a keyword — `ransomware`, `CVE-2025`, `#threatintel` — and it pulls matching posts from both networks, merges them by time, and shows you a single feed. It re-checks every 20 seconds without prompting. There's an auto-scroll mode if you want to leave it running on a side monitor, which is how I actually use it.

The design borrows from late-night control room aesthetics — phosphor green on near-black, faint scanlines, JetBrains Mono throughout. It looks like something that should be displaying satellite telemetry.

## The proxy problem

Social APIs are public in spirit but awkward in practice. Both Bluesky and Mastodon serve their data freely, but browsers have rules about fetching from third-party domains — a security feature that turns into a bureaucratic hurdle when you're just trying to read public posts.

The fix is a small Cloudflare Worker that sits between the page and the APIs. It passes your request through and adds the right headers. It's allow-listed to exactly two hosts — the two it's supposed to talk to — so it can't be turned into a general-purpose relay.

One small detour along the way: Bluesky's public API endpoint returns a 403 for Indian IP addresses. The same data is available through a different endpoint, which has no such restriction. It took about ten minutes to find and longer to stop wondering what I'd done wrong.

## Architecture

Two Cloudflare deployments that together cost nothing to run:

- **Worker** — handles the API calls, sits invisibly between the page and the two networks
- **Pages** — the frontend, a single HTML file with no build step and no dependencies

The JavaScript polls both APIs on a timer, deduplicates posts by ID, and re-renders sorted by time. If one source fails, the other keeps running — the status indicator says `partial` rather than going blank.

## What I'd change

The Mastodon side is slightly compromised. infosec.exchange now requires authentication for most of its API endpoints, so keyword searches only work as hashtag lookups there. For plain terms like `malware` you get Bluesky results only, and Mastodon sits out.

A proper fix is a Mastodon API token — free, takes two minutes — but that means the Worker needs to hold a secret, which means configuration, which undermines the "just deploy it" simplicity. Left it as-is for now. It still works, just not symmetrically.

## What it looks like

{{< figure src="/images/vibecoding/signal-live.png" alt="SIGNAL/live showing a live merged feed of infosec posts from Bluesky and Mastodon" >}}

## Source

→ [Try it live](https://signal-feed-8pl.pages.dev/) · [github.com/mr-dinesh/signal-live](https://github.com/mr-dinesh/signal-live)
