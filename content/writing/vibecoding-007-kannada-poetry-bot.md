---
title: "Putting 945 Verses of Kannada Philosophy on the Internet, One at a Time"
date: 2026-03-21
tags: ["Mastodon", "Kannada", "Poetry", "VibeCoding"]
aliases: ["/writing/vibecoding-007-bot-to-post-kannada-poetry-on-mastodon/"]
description: "Built a Mastodon bot to post DVG's Mankutimmana Kagga — 945 verses of Kannada philosophy — twice daily with transliteration and English explanation."
cover:
  image: "/images/writing/vibecoding-007-kaggabot-mastodon.png"
  alt: "KaggaBot Mastodon post showing a Mankutimmana Kagga verse"
  relative: false
---

### Building a Bot to post Mankutimmana Kagga verses to Mastodon

**D.V. Gundappa's** *Mankutimmana Kagga* — 945 verses of timeless Kannada philosophy — deserves a wider audience. So I built a Mastodon bot to post one verse at a time, twice a day, complete with transliteration and English explanation. Here's how it came together.

### The Prompt

The project started with a simple ask to Claude: *"Create a Mastodon bot to post Kannada Mankutimmana Kagga verses with a short explanation, configurable on how often to post."* From that single sentence, Claude scaffolded a complete Python project — `kagga_bot.py`, `config.py`, `kagga_verses.py`, and a scraper to pull all 945 verses from a public repository.

### Features

- **All 945 verses** with Kannada text, Roman transliteration, and English explanation
- **Configurable schedule** — minutes, hours, or daily at a set time
- **Sequential or random** verse ordering, with persistent state across restarts
- **Smart 500-char handling** — tries full post, falls back to short tags, then posts as a thread if needed
- **Theme filtering** — post verses by theme (Wisdom, Death, Love, etc.)
- **Dry-run mode** for testing without posting

### What Broke

**Literal newlines in the verse data.** The scraper pulled all 945 verses from a public repository and generated `kagga_verses.py` automatically. What it didn't handle was multi-line verse text — the strings had literal newline characters embedded inside them, which Python reads as a syntax error. The file wouldn't even load. Fix: a `sed` pass to replace literal newlines inside strings with `\n` escape sequences before import.

**The 500-character limit is stricter than it looks.** Mastodon's limit is 500 characters, but Kannada Unicode characters consume multiple bytes each. A verse that *looks* short can blow past the limit. The first trimming logic counted characters naively. The fix required counting bytes, not characters, and building a cascade: try the full post → fall back to a shortened version with just the Kannada text and a note → post as a thread if it still won't fit.

**The Kannada hashtag silently broke.** `#ಕಗ್ಗ` uses a virama (the joining character that combines consonants in Kannada script). Mastodon's hashtag parser stripped it, turning the hashtag into something unrecognisable. The workaround was switching to a transliterated hashtag `#Kagga` alongside the Kannada version — less authentic, but actually clickable.

**PythonAnywhere's free tier blocked the Mastodon instance.** The original plan was to host the bot on PythonAnywhere and post to `ioc.exchange` (the infosec Mastodon instance). PythonAnywhere's free tier uses a proxy that blocks outbound connections to many smaller Mastodon instances. The fix was switching to `mastodon.social`, which is large enough to be on PythonAnywhere's allowlist.

### What I Learned

Encountering problems are a part of the process. 
Debugging them is part of the learning process.

The bot is live and posting.
Check it out on [Mastodon](https://mastodon.social/@browncoolie)

### Bot Source code is at Github:
[Repo link here](https://github.com/mr-dinesh/Kagga-Bot)