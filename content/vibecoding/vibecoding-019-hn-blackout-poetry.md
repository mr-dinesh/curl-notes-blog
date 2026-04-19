---
title: "Vibecoding 019: HN Blackout Poetry"
date: 2026-04-18
description: "Blackout poetry from the Hacker News front page — an LLM picks the surviving words, the rest gets erased."
tags: ["vibecoding", "llm", "poetry", "javascript", "hacker-news"]
---

Austin Kleon takes a newspaper page and a black marker, and turns the news into poetry by erasing most of it. What's left — the surviving words — becomes a found poem. He's been doing this for years. It's a surprisingly moving art form.

I wanted to do the same thing with Hacker News.

## The idea

HN headlines have a particular texture. They're dense with jargon, proper nouns, and compressed meaning. "Smol machines." "PanicLock." "Casus Belli." "Hyperscalers." These aren't ordinary words — they carry whole worlds of context. When you strip away the surrounding noise, you sometimes find something strange and resonant.

The tool fetches the top 20 stories from the HN API, sends the headlines to an LLM with a blackout-poet prompt, and asks it to pick 10–15 words that form a poem. Everything else gets blacked out — animated with a CSS marker-stroke effect, word by word. The survivors appear on the right as a found poem with a title.

## The output

The first real run produced this, titled **"Fevered Machines"**:

> lunar  
> hay  
> fever  
> gunpowder  
> Smol  
> machines  
> PanicLock  
> Slop  
> Hyperscalers  
> Troy  
> acceleration  
> Casus  
> Belli

That's from an actual HN front page. "Hay fever" and "gunpowder" came from a history article. "Smol machines" from an AI piece. "PanicLock" from a security story. "Casus Belli" from geopolitics. Stripped of context and placed next to each other, they become something else entirely.

## How it works

It's a single HTML file — same pattern as [yaraweave](/vibecoding/vibecoding-017-yaraweave) and [argus](/vibecoding/vibecoding-016-argus). No backend, no build step. Open in a browser.

The LLM prompt asks the model to act as a blackout poet in the style of Austin Kleon. It must return exactly the words as they appear in the headlines (preserving capitalisation), output valid JSON, prefer unexpected juxtapositions, and avoid mundane connectives. The JSON comes back as `{ "title": "...", "poem": ["word1", "word2", ...] }`.

Then there's a tokenizer that splits every headline into word tokens. A matcher finds each poem word in the token list — exact match first, then case-insensitive, then strip-punctuation fallback. Non-matching tokens get blacked out with a staggered CSS animation (a `marker-stroke` keyframe that sweeps from transparent to black). The poem words slide in on the right panel one by one, timed to appear partway through the blackout animation.

The whole thing runs against the HN Firebase API (public, no key needed) and either Groq (`llama-3.3-70b-versatile`) or Gemini Flash 2.0. Both have free tiers. Keys are stored in `localStorage`.

## The design

I wanted it to feel like a real newspaper page meeting a dark digital canvas. The left panel — the "newspaper" — uses a cream/newsprint background, IM Fell English (an old-style serif), faint horizontal rules, and thick black marker strokes for the redacted words. The right panel is dark with a faint gold grid, Playfair Display italic for the poem, and words that slide in from the left with a fade.

The masthead reads: *Words found. Meaning made. The rest, erased.*

{{< figure src="/images/vibecoding/hn-blackout.jpg" alt="HN Blackout showing the newspaper panel with blacked-out headlines and the found poem 'Fevered Machines' on the right" >}}

## What surprised me

The LLM is genuinely good at this. I expected it to pick safe, obvious words. Instead it goes for the strange ones — the proper nouns, the tech jargon that sounds almost mythological when isolated. "PanicLock" next to "Slop" next to "Hyperscalers" reads like a dispatch from a dystopia we're already living in.

Each run is different. The headlines change daily, and even with the same headlines, temperature 0.9 produces different selections. Some runs are better than others. The bad ones are forgettable. The good ones feel like they found something real.

## Update — April 2026

Two additions landed in a later session.

**Five HN pages.** The original only pulled Top Stories. The page selector now covers Top, Best, New, Ask HN, and Show HN. Each has its own character — Ask HN leans philosophical, Show HN is full of product names that read like incantations, New is chaotic and raw. The attribution line in the poem panel updates to match.

**Five themes.** The original newsprint-and-dark look is still the default, but there are now four alternatives:

- **Ink** — stark black and white, typewriter font. No compromise.
- **Amber** — retro terminal, monochrome orange-on-black. Feels like 1983.
- **Dusk** — moody purple and indigo. The late-night read.
- **Times** — clean NYT broadsheet: white paper, Playfair Display, NYT blue accents. The one that looks like it belongs in a museum.

Theme choice persists in `localStorage`. The coloured dots in the settings bar switch between them instantly — CSS custom properties handle all the repainting, no JavaScript needed for the actual theme application.

## Update 2 — April 2026

Added client-side throttling to prevent API abuse.

**30-second cooldown.** After each generation the button switches to a live countdown (`Wait 28s…`) and blocks further clicks. The cooldown survives a page refresh — it's stored in `localStorage` against a timestamp, so reopening the tab mid-cooldown picks up where it left off.

**Daily limit of 10 poems per provider.** Groq and Gemini are tracked separately, each with their own counter keyed to the current date. The counter resets automatically at midnight. A usage badge in the settings bar shows the current count (`3 / 10 today`), turns amber above 70%, and red at the limit. The status bar tells you how many poems remain after each successful generation.

All of this is client-side — `localStorage` only, no backend. It won't stop a determined person from opening DevTools and clearing storage, but it stops accidental rapid-fire clicking and keeps casual use within free-tier API limits.

## Source

→ [github.com/mrdee-in/hn-blackout](https://github.com/mrdee-in/hn-blackout)
