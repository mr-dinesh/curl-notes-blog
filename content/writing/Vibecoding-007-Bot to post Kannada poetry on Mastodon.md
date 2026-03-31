---
title: "Putting 945 Verses of Kannada Philosophy on the Internet, One at a Time"
date: 2026-03-21
tags: ["Mastodon", "Kannada", "Poetry", "VibeCoding"]
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

### Challenges

The biggest debugging headaches were unexpected. The scraped `kagga_verses.py` contained **literal newlines inside string literals** — causing Python `SyntaxError` on load. Several verses needed surgical `sed` fixes. Mastodon's **500 character limit** required multiple iterations of the trimming logic, especially since Kannada Unicode characters count as multiple bytes. The **Kannada hashtag `#ಕಗ್ಗ`** rendered incorrectly on Mastodon — the virama joining character was silently stripped. And PythonAnywhere's **free tier proxy blocked** outbound connections to `ioc.exchange`, requiring to move to 'mastodon.social' instead.

### What I Learned

Encountering problems are a part of the process. 
Debugging them is part of the learning process.

The bot is live and posting.
Check it out on [Mastodon](https://mastodon.social/@browncoolie)

### Bot Source code is at Github:
[Repo link here](https://github.com/mr-dinesh/Kagga-Bot)