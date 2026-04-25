---
title: "Vibecoding 023 — AFL Masterclass: A Technical Deep Dive"
date: 2026-04-25
description: "A gamified self-paced learning module covering AFL/AFL++ from first principles — edge coverage, the bitmap, mutation stages, adversarial critique, and a 30-day practice roadmap."
tags: ["vibecoding", "security", "fuzzing", "afl", "javascript", "cloudflare"]
aliases: ["/writing/vibecoding-023-afl-masterclass/"]
weight: -23
---

Coverage-guided fuzzing is one of those topics where the gap between "I've heard of AFL" and "I understand what AFL actually does" is larger than it appears. This is an attempt to close that gap in a structured way.

**Live:** [afl-masterclass.pages.dev](https://afl-masterclass.pages.dev)

## What the document covers

Ten sections, built in a deliberate sequence:

The opening section starts with a question that shapes everything else: why did AFL represent a step-change rather than an incremental improvement? The answer is economic rather than algorithmic. Before AFL, the two available approaches — blind random fuzzing and grammar-based generation — forced a choice between scale and domain knowledge. Coverage feedback removes that tradeoff. The fuzzer learns the structure of the target without anyone specifying it.

From there, the document works through the instrumentation (edge coverage, the XOR bitmap, hit count buckets), the mutation pipeline (deterministic stages before havoc, splice as genetic crossover), the systems engineering decisions (why 64KB — it's an L2 cache sizing decision, not arbitrary), and the adversarial critique — the cases where AFL structurally cannot make progress without external help.

The adversarial critique section is probably the most practically useful. Magic bytes, checksums, deep state machines, structured grammars — these are the normal operating environment for anything worth fuzzing. Understanding where AFL breaks is as important as understanding where it works.

The final content section is myth cards — seven common misconceptions with explicit rebuttals. The one that recurs most in practitioner conversations: "AFL found no crashes in 24 hours, so the code is probably clean." That reasoning has five independent failure modes. The section makes each one concrete.

## Structure and intent

The document is designed for someone who wants to build genuine working knowledge, not just familiarity with the terminology. Each section has a time estimate and difficulty rating. There's a 7-day hands-on curriculum with specific daily tasks, and a 30-day roadmap with concrete weekly deliverables.

The key constraint the roadmap tries to enforce: the deliverable at the end of week one is a crash, not notes about crashes. Category-level understanding and working knowledge are different things. The structure is designed to push toward the latter.

## Progress tracking

The document is a single HTML file with no build step and no external dependencies. It has a lightweight progress system built in:

- Sticky progress bar with XP counter
- "Mark Complete" on every section (50 XP)
- "Done" on each of the 7 curriculum days (20 XP)
- "I understand this" on each of the 7 myth cards (10 XP)
- Three themes: Dark / Light / Sepia
- State persists to localStorage

## What the document doesn't cover

Writing a good fuzzing harness is a deep reading skill, not a fuzzer skill. It requires understanding which entry points are callable without the full application stack, what state needs initialising, what needs stubbing, how to avoid the OOM spiral from leaked allocations. That takes practice. The 7-day curriculum is designed to force that practice early, but the document can't substitute for it.

## References

The references section links to the primary sources: Zalewski's `technical_details.txt`, the AFLFast paper (Böhme et al., CCS 2016), the REDQUEEN paper (Aschermann et al., NDSS 2019) that underpins AFL++'s CMPLOG feature, and the AFL++ design paper (Fioraldi et al., WOOT 2020). If you're going to use this as a starting point, those are the natural next things to read.
