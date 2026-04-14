---
title: "Vibecoding 016 — Argus"
date: 2026-04-14
description: "A single-file Cloudflare Workers app that stress-tests any claim, URL, or article from every angle — steelman, strawman, synthesis."
tags: ["vibecoding", "cloudflare", "workers-ai", "llm", "tools", "reasoning"]
aliases: ["/writing/vibecoding-016-argus/"]
---

I read a lot. Substacks, security advisories, policy papers, op-eds. And I noticed a pattern in myself — I'd read something that confirmed my existing view and move on, or dismiss something that challenged it without really engaging with it. Neither is rigorous thinking.

Argus was built to fix that. The premise: before you commit to a position, stress-test it. Force yourself to see the strongest version of the argument you disagree with, and the weakest version of the one you're inclined to accept.

The name is from Greek mythology. Argus was the hundred-eyed giant who saw everything from every angle.

→ **[github.com/mr-dinesh/argus](https://github.com/mr-dinesh/argus)**

![Argus](/images/writing/vibecoding-016-argus.jpg)

---

## What It Does

Paste a claim, a URL, or an article. Argus auto-detects the input type and produces three panels.

**Steelman** — The strongest possible version of the argument. Assumes the most informed, serious defender. If it would embarrass a real expert, the model rewrites it.

**Strawman** — The weakest, most attackable version. What a hostile critic actually dismantles. What gets left out, exaggerated, or silently assumed.

**Synthesis** — What a rigorous, disinterested thinker concludes. Includes the real crux — the single question that separates believers from sceptics — what evidence would flip the conclusion, and one actionable implication.

---

## Architecture

Everything runs on Cloudflare. No external API keys. No backend server. No database.

```
Browser
  +-- Cloudflare Worker (argus-proxy.mrdinesh.workers.dev)
        +-- GET /         → serves the HTML app
        +-- POST /fetch   → proxies URL fetch (solves CORS)
        +-- POST /analyse → calls Workers AI (llama-3.1-8b-instruct)
```

Single Worker, three routes. The HTML is embedded directly in the Worker — no separate hosting, no Pages project, no CDN configuration. One deployment, one URL.

Workers AI handles inference on Cloudflare's free tier — 10,000 requests/day, no credit card required. The model returns structured JSON which gets parsed and rendered into the three panels client-side.

The `/fetch` route is what enables URL mode. Browsers block cross-origin fetches. The Worker fetches server-side and returns the HTML, which the client strips to plain text before sending to the AI.

---

## The Prompt Is the Product

The UI took an afternoon. The model is someone else's. The prompt is the only thing that makes Argus different from a generic pros-and-cons generator.

Four constraints that matter:

**Structured JSON only.** No prose, no preamble, exact schema enforced by instruction. If the model returns anything else, the parser catches it.

**No validation.** "Do NOT validate or agree with the input." Without this, LLMs reliably flatter the user. This one instruction changes the output character entirely.

**Steelman quality check.** "If your steelman would embarrass a serious defender, rewrite it." Dramatically improves output on the first try.

**Specific crux.** "The single resolvable question separating believers from sceptics. Not 'it depends'." The crux field is the most intellectually honest output in the whole tool. In a client meeting, naming the crux ends 40-minute debates in 4 minutes.

---

## What Vibecoding This Felt Like

The API roulette problem is real. Anthropic (no free tier), OpenRouter (free models deprecated), Gemini (free tier blocked in India) — before landing on Cloudflare Workers AI. The lesson: when building a free personal tool, your API choice is a constraint, not a preference.

CORS is always the first wall. Every URL-fetching tool hits this. The right fix is always a server-side proxy — not allorigins.win, not corsproxy.io. Own your proxy.

Single-file deployments are underrated. Embedding the HTML in the Worker means zero infrastructure to maintain, zero cold starts, zero separate deployments to keep in sync.

Prompt engineering compounds. Each of the four prompt constraints above was added after seeing a failure mode in the output. You can't design these constraints upfront — you discover them by running real inputs and noticing where the model flinches.

---

**[github.com/mr-dinesh/argus](https://github.com/mr-dinesh/argus)**  
*Part of the [100 Vibe Coding Projects](https://mrdee.in/vibecoding/) series.*
