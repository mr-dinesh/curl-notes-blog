---
title: "One Page, Five Sources, Zero Noise — My Security News Dashboard"
date: 2026-03-20
tags: ["Security", "News", "Groq", "VibeCoding"]
aliases: ["/writing/vibecoding-006-building-a-slashdot-style-cybersecurity-news-dashboard-with-groq/"]
description: "SlashSec is a single HTML file that pulls live RSS from five trusted security sources and uses Groq to generate summaries, severity ratings, and Slashdot-style dept. lines."
cover:
  image: "/images/writing/vibecoding-006-slashsec.png"
  alt: "SlashSec cybersecurity news dashboard with Slashdot-style layout"
  relative: false
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

### What Broke

CORS. RSS feeds don't serve with the headers browsers need for cross-origin fetches. The first version used a single CORS proxy — which worked for about a day before the free tier started rate-limiting requests.

The final implementation uses a three-proxy fallback chain: `allorigins.win` → `corsproxy.io` → a third fallback. If all three fail, the feed degrades gracefully and shows whatever was cached from the last successful fetch. Getting this right took longer than building the entire rest of the dashboard. It's always CORS.

The other problem was JSON reliability. Groq returns JSON most of the time. "Most of the time" is not good enough when your UI depends on parsing it. The fix was wrapping every parse in a try/catch with a fallback to a safe default object — so a malformed response shows a placeholder summary rather than crashing the whole refresh.

### What I Learned

The "dept." line was an afterthought in the prompt — added because Slashdot had it and it seemed fun. It turned out to be the most useful part of the output.

A 3–5 word distillation forces compression that a 3–4 sentence summary doesn't. *supply-chain-never-sleeps dept* tells you the story before you read the headline. *patch-tuesday-forever dept* sets the tone immediately. Good prompt design often comes from constraints you didn't plan for. The lesson: include something playful in your prompt. It surfaces structure you didn't know you needed.

Also: `sessionStorage` for API keys is the right call. `localStorage` persists across tabs and sessions, which is more convenient but widens the exposure window. A key that disappears when the tab closes can't be exfiltrated by a script that runs later. Small decision, correct decision.

### Get The Code

**[github.com/mr-dinesh/SlashSec_style-Infosec-RSS-Dashboard](https://github.com/mr-dinesh/SlashSec_style-Infosec-RSS-Dashboard)**

One `.html` file. Free Groq account at [console.groq.com](https://console.groq.com). Open in browser, paste key, click Fetch Stories.

---

*Built iteratively with Claude Sonnet. The final file is about 1,100 lines of vanilla HTML, CSS, and JavaScript.*
