---
title: "Vibecoding 022 — PrivyRead: Read Anything, Leave Nothing Behind"
date: 2026-04-23
description: "A privacy-first reader that strips trackers, follows redirects server-side, and hands you clean article text before any of that noise touches your browser."
tags: ["vibecoding", "privacy", "cloudflare", "javascript", "pwa", "readability"]
aliases: ["/writing/vibecoding-022-privyread/"]
weight: -22
---

Every time you click a link in a newsletter, three things happen before you've read a single word: the link redirector logs that you clicked, the UTM parameters tell the destination who sent you, and the tracking pixel in the email confirms you opened it. None of this is secret — it's just how email marketing works. But knowing it happens and having to participate in it are different things.

PrivyRead is the opt-out.

## What it does

Paste a URL — or share one directly from your phone — and PrivyRead hands you the article with none of the overhead. Tracking parameters are stripped before the request goes out. Redirects are followed on the server, not in your browser, so the intermediate link shortener fires against a Cloudflare worker IP instead of yours. The page is fetched and parsed with Mozilla Readability, and what arrives in your browser is clean text: title, byline, body, reading time. Images don't load at all — not because they can't, but because they often contain tracking pixels and I'd rather not.

It's installable as a PWA and registers as a share target on Android. From any app — email, Substack, Twitter — long-press a link, tap Share, and PrivyRead appears in the sheet. The article opens directly. The newsletter never knows you read it.

## The interesting part: Readability in a Worker

Mozilla's Readability library — the same thing that powers Firefox Reader View — expects a real DOM. It was written for browsers. Running it in a Cloudflare Worker means you have JavaScript but no document object.

The fix is [linkedom](https://github.com/WebReflection/linkedom), a server-side DOM implementation. You feed it raw HTML and get back a `document` object that Readability is happy with. It's not perfect — a few edge cases differ from browser DOM behaviour — but for article extraction it works well. The combination is lightweight enough that the Worker cold starts in around 7 ms.

## Tracking params stripped

The list covers the obvious ones — `utm_source`, `utm_medium`, `utm_campaign`, `fbclid`, `gclid` — and a longer tail most people haven't seen: `mkt_tok` (Marketo), `_hsenc` (HubSpot), `twclid`, `li_fat_id`, `epik` (Pinterest), `ttclid` (TikTok), `substack_referral`. Thirty parameters in total. If a URL has them, the pill says **TRACKERS STRIPPED**. If it doesn't, nothing is shown — no noise about noise.

## Architecture

Two Cloudflare deployments, zero cost to run:

- **Worker** — `privyread.mrdinesh.workers.dev` — fetches, redirects, strips, parses. The only thing that ever touches the target site.
- **Pages** — `privyread.pages.dev` — a single HTML file. No framework, no build step, no dependencies loaded at runtime.

The frontend keeps a session counter: articles read and trackers stripped. It resets when you close the tab, which is intentional — I didn't want to store anything.

## What I'd change

Substack paywalls articles properly and Readability can't extract what the server doesn't send. That's expected. What's more annoying is sites that require JavaScript to render their content — server-side fetching gets the raw HTML but misses anything added dynamically. A headless browser would solve it but defeats the point of running in a Worker.

The share target only registers after installing as a PWA, which requires visiting the site in a browser first. Not a hard step, but not zero either.

## What it looks like

{{< figure src="/images/vibecoding/privyread.png" alt="PrivyRead — privacy-first article reader with tracker stripping and server-side redirect following" >}}

## Source

→ [Try it live](https://privyread.pages.dev/)
