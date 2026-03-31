
---
title: "KaggaBot: Automating Daily Verse Posts With GitHub Actions"
date: 2026-03-25
tags: ["GitHub Actions", "Mastodon", "Automation", "VibeCoding"]
description: "KaggaBot uses GitHub Actions as a free scheduler to post two Mankutimmana Kagga verses to Mastodon every day — no server, no cost, no babysitting."
---


### What's Mankuthimmana Kagga

Mankuthimmana Kagga — often called the Kannada Gita — is a collection of 945 philosophical verses by D.V. Gundappa (DVG). Written in the 1940s, it wrestles with life's biggest questions with a rare combination of humility and depth. It deserves a wider audience.

### KaggaBot

It's a small automation that does one simple thing: post two verses from the Kagga every day to Mastodon (an ad-free social media platform), automatically, without anyone pressing a button.

### What's in the code

The core of the bot is a Python file containing all the verses of the Kagga, individually scraped and stored as structured data. 

A script picks from this collection and formats each verse for posting. GitHub Actions handles the scheduling — no server required, no ongoing cost.

Verses in .py file  →  bot script  →  GitHub Actions cron  →  Mastodon post

### The scheduling magic

A GitHub Actions workflow file defines two daily triggers — morning and evening. When the schedule fires, GitHub spins up a clean environment, checks out the code, and runs the bot. That's the entire pipeline.

### Two posts a day, every day
on:
  schedule:
    - cron: '0 6 * * *'   # morning
    - cron: '0 18 * * *'  # evening
No cloud bill. No server to maintain. No babysitting.

### Why Mastodon?
Mastodon is open, ad-free, and has a clean API — ideal for a bot that exists purely to share literature, not to game an algorithm. The posts are public and readable by anyone, no account needed.

### Why this matters
At two posts a day, it takes over a year to work through all 945 verses of Mankuthimmana Kagga.

That's the right pace for philosophy — slow enough to sit with, regular enough to build a habit. KaggaBot transforms reading a classic Kannada text into a daily practice, entirely on autopilot.

The whole project is open source. If you want to adapt it — for a different text, a different language, a different platform — the bones are all there.

### Links
🐘 [Read the posts](https://mastodon.social/@browncoolie)
⎇ [View source code](https://github.com/mr-dinesh/KaggaBot_Automated)


