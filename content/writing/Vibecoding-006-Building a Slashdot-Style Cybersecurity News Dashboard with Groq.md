---
title: "One Page, Five Sources, Zero Noise — My Security News Dashboard"
date: 2026-03-20
tags: ["Security", "News", "Groq", "VibeCoding"]
description: "SlashSec is a single HTML file that pulls live RSS from five trusted security sources and uses Groq to generate summaries, severity ratings, and Slashdot-style dept. lines."
---


---

I wanted a single place to read cybersecurity news from the sources I already trust — SANS ISC, Bruce Schneier's blog, Brian Krebs, Bleeping Computer, and Zack Whittaker's This Week in Security. I wanted something purpose-built for security, with AI-generated summaries short enough to scan quickly.

The result is **SlashSec**: a single HTML file, no build step, no server, no dependencies beyond a free Groq API key.

---

### The Prompt

The core instruction to the LLM was deliberately narrow:

> *"You are a cybersecurity editor writing for a Slashdot-style infosec magazine. Given a JSON array of articles, return a JSON array where each element has a 3–4 sentence summary, a severity rating (high / medium / low), 2–4 tags, and a witty Slashdot-style department line."*

That's it. The model receives article titles and excerpts pulled from real RSS feeds. It never generates URLs — all links come directly from the feeds. This keeps the output grounded and avoids hallucinated references.

The "dept." line — borrowed from Slashdot's classic format — turned out to be the most useful prompt element. It forces the model to distil the article's tone into 3–5 words, which ends up being a surprisingly good quick-glance signal. Examples the model produces: *yet-another-breach dept*, *patch-tuesday-forever dept*, *supply-chain-never-sleeps dept*.

---

### The LLM

**Groq** running **llama-3.3-70b-versatile**.

Groq was chosen for speed and its generous free tier. A full refresh — up to 40 articles across 5 feeds. 
The API key is stored in `sessionStorage` only, cleared when the tab closes, and sent exclusively to `api.groq.com`. No proxy or third-party service sees it.

---

### Features

- **5 live RSS feeds** fetched concurrently on every refresh, with a three-proxy fallback chain for CORS handling
- **AI summaries** — 3–4 sentences per article: what happened, who is affected, what to do
- **Severity classification** — High, Medium, or Low per article, with one-click filtering
- **Slashdot layout** — masthead, sticky nav, two-column story feed with sidebar, bylines, and dept. lines
- **Source colour coding** — each of the five sources has a distinct accent colour across all UI elements
- **Dashboard view** — severity distribution, per-source article counts, top tag cloud, all clickable
- **Dark and bright themes** — toggled with a single button, saved between sessions
- **Verified links** — every "Read More" link is sourced directly from the RSS feed, marked with a ✓ badge

The whole thing is one `.html` file. Open it in a browser, paste a Groq API key, click Fetch Stories.

---

### Get The Code

The full source is on GitHub:

**[github.com/mr-dinesh/SlashSec_style-Infosec-RSS-Dashboard](https://github.com/mr-dinesh/SlashSec_style-Infosec-RSS-Dashboard)**

Includes the dashboard, a README, and this write-up. The only requirement is a free Groq account at [console.groq.com](https://console.groq.com).

---

*Built iteratively with Claude Sonnet as a coding assistant. The final file is about 1,100 lines of vanilla HTML, CSS, and JavaScript.*
