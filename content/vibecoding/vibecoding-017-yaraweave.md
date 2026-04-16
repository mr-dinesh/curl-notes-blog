---
title: "Vibecoding 017 — YaraWeave: From Threat Intel to YARA in One Click"
date: 2026-04-16
description: "A single-file browser tool that queries MalwareBazaar, VirusTotal, OTX and more — then uses Gemini to generate a production-quality YARA rule with a condition-by-condition explanation."
tags: ["vibecoding", "security", "yara", "threat-intelligence", "gemini", "soc"]
aliases: ["/writing/vibecoding-017-yaraweave/"]
---

![YaraWeave — Threat Intel to YARA Rule Generator](/images/writing/vibecoding-017-yaraweave.jpg)

## The Itch

Every SOC I've ever worked with has the same gap.

They have threat intelligence. Feeds, platforms, subscriptions — often more than they know what to do with. And they have YARA. Most mature detection teams have some rules, usually inherited, rarely updated, authorship long forgotten.

What they almost never have is the middle part: someone who can look at a MalwareBazaar entry for a new Emotet variant and turn it into a deployable detection rule within the same morning. That skill — translating raw intel into working YARA — sits at the intersection of malware analysis, detection engineering, and threat intelligence. It's genuinely rare. And it's exactly the kind of operational gap that a language model is well-suited to bridge.

That's what YaraWeave is. A tool for closing that gap, fast.

→ **[github.com/mr-dinesh/yaraweave](https://github.com/mr-dinesh/yaraweave)**

---

## The Idea

The brief was simple: accept a SHA256 hash or a malware family name, hit multiple open-source threat intel sources in parallel, and use Gemini to synthesise a YARA rule from everything that came back.

Not a toy rule with `$str1 = "malware"`. A real one — with meaningful hex patterns, wide string variants, weighted conditions, and a metadata block that tells you when it was generated, what severity it carries, and what TLP applies.

And then explain it. Section by section. Condition by condition. So a tier-1 analyst who didn't write the rule can still understand it, tune it, and deploy it with confidence.

Up to five intel sources, one LLM call to generate, one to explain. That's the entire pipeline.

---

## The Build

### Sources

The tool queries up to five sources in parallel using `Promise.all`:

| Source | What it adds | Key required |
|---|---|---|
| MalwareBazaar | Family name, file type, first seen, reporter tags | None |
| URLhaus | Distribution URLs, payload context | None |
| OTX AlienVault | Threat pulse count, community intelligence | Free |
| VirusTotal | Detection rate across 70+ AV engines | Free |
| ThreatFox | IOC context, additional tags | None |

MalwareBazaar, URLhaus, and OTX are enabled by default; ThreatFox is available but unchecked. The three abuse.ch sources (MalwareBazaar, URLhaus, ThreatFox) support browser-direct requests with open CORS policies — no proxy needed. That's what made a single-file deployment viable.

### The Gemini Prompt

The YARA generation prompt is doing more work than it looks like. It doesn't just say "write a YARA rule for Emotet." It sends the full raw JSON from every source that returned data, plus an enriched summary with family, file type, first-seen, tags, detection rate, and OTX pulse count. Gemini then generates against that full context.

The rule requirements are explicit in the prompt:
- `detect_` prefix, snake_case name
- Metadata with description, author, date, hash (if available), severity, TLP
- At least 3–5 meaningful string patterns — hex patterns, ASCII, wide variants
- A weighted condition: `(2 of ($str*)) and (1 of ($hex*))` — not `all of them`

The second call — the explanation — parses the generated rule and produces five structured sections: `THREAT_CONTEXT`, `RULE_LOGIC`, `STRING_RATIONALE`, `DEPLOYMENT_NOTES`, and `CONFIDENCE`. That last one is important. A generated rule with `CONFIDENCE: LOW` should be treated very differently from one with `CONFIDENCE: HIGH` — and both are more useful than a rule with no confidence signal at all.

### API Config

All keys — Gemini, VirusTotal, OTX — are configured through a modal and stored in `localStorage`. Nothing is hardcoded. Nothing is sent to a backend. The browser talks directly to each API. This was a deliberate choice: the tool needed to be deployable as a static file without a server, and it needed to be trustworthy enough that I'd hand the URL to a security professional without them wondering where their API keys were going.

The Gemini model is also configurable (`gemini-1.5-flash` by default, but you can switch to `gemini-2.0-flash-exp` or `gemini-1.5-pro` without touching the code).

---

## What Vibecoding This Felt Like

This one was a different kind of build. Most vibe coding sessions involve a lot of UI iteration — getting the layout right, fixing the interactions, making it feel like a real tool rather than a prototype. YaraWeave had all of that, but the interesting work was in the prompts.

Getting a language model to produce a *good* YARA rule — not a plausible-looking one, but one that a detection engineer would actually deploy — required being very specific about what "good" meant. The first few iterations produced rules that were syntactically correct but operationally useless: generic strings, trivially bypassable conditions, metadata with placeholder values.

The fix was to treat the prompt like a spec doc. Every requirement was explicit. The model stopped guessing what I wanted and started delivering what I asked for.

The explanation pipeline was the part I hadn't planned for at the start. But once the YARA output was solid, the natural question was: *who deploys this?* The analyst who generated it might understand it. The one on shift at 2am inheriting it needs the explanation too. That second Gemini call is cheap and it's the thing that makes the tool useful beyond a single session.

---

## Try It

- **Claude Artifact:** [Run YaraWeave in your browser](https://claude.ai/public/artifacts/8c198f5f-e4db-4765-9ee2-b88ee0b35a1f)
- **GitHub:** [github.com/mr-dinesh/yaraweave](https://github.com/mr-dinesh/yaraweave)
- Open `yaraweave.html` in any browser
- Click **⚙ Configure**, add your Gemini key (free at [aistudio.google.com](https://aistudio.google.com))
- Try `Emotet` in family mode — no other keys needed

VirusTotal and OTX keys are optional but add detection rate and pulse count context that meaningfully improves the generated rule.

---

**[github.com/mr-dinesh/yaraweave](https://github.com/mr-dinesh/yaraweave)**  
*Part of the [100 Vibe Coding Projects](https://mrdee.in/vibecoding/) series — building security tools to translate 25 years of practitioner experience into demonstrable artifacts.*
