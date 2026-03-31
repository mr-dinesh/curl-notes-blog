---
title: "The URL Sanitizer That Strips Trackers Before You Click"
date: 2026-03-14
tags: ["Browser Extension", "Privacy", "VibeCoding"]
aliases: ["/writing/vibe_coding_001/"]
description: "Built a browser extension with Gemini that strips tracking parameters from URLs before you open them. Day 1 of the 100 Vibe Coding Projects challenge."
cover:
  image: "/images/writing/vibecoding-001-purelink.png"
  alt: "PureLink browser extension stripping tracking parameters from a URL"
  relative: false
---

### Two big ideas here
- Idea#1: Use an LLM, to create something, anything
- Idea#2: Do it for a 100 days
- A third, meta idea, is to write about what I've done (aside: why is this a meta-idea, will write about it later)

### Today's vibe-coding idea: create a browser extension for a URL sanitizer.

It removes all tracking parameters from the link before rendering it in a new tab.
Tool of choice: Gemini - got this idea from [S Ananand's talk](https://www.youtube.com/watch?v=mCJLNML7FrE)

What struck me as amazing, was the ease of creating and how close the outcome was, to what I'd expected.
And what was also equally amazing, was that it worked. I also got the LLM to create an icon and name it.


### Some Caveats
- I'm not sure, how effective the URL sanitization actually is. 
- Also, there are tons of similar addons, so what makes PureLink any better / different / good ?
- Need to spend some more time validating the results, but I was happy with the initial outcomes and will eventually do a bit more study and analysis of the inner working of the code.

### What Broke

The first version caught the obvious tracking parameters — `utm_source`, `utm_medium`, `utm_campaign` — but missed more obscure ones like `fbclid`, `gclid`, and Microsoft's `ocid` parameter. Gemini generated a solid `rules.json` skeleton but the actual list of parameters to strip needed manual research and validation. The icon it generated was also… let's call it a first draft. Functional, not beautiful.

The deeper issue: Gemini built the extension structure correctly on the first try. The boilerplate — `manifest.json`, `background.js`, `popup.html` — all worked. The weakness was the business logic. The list of tracking params isn't something an LLM can confidently enumerate; it changes as ad platforms update their attribution schemes. That validation has to be done by a human.

### What I Learned

Let the LLM handle structure, be more careful about the specific rules it generates. Browser extension scaffolding is exactly the kind of repetitive, well-documented boilerplate that LLMs do well. The actual logic — which parameters are trackers, which are functional — requires domain knowledge and current sources. [CleanURLs](https://github.com/ClearURLs/Addon) has been maintaining that list for years. PureLink should probably just use it.

### The Security Angle

As someone who thinks about tracking and attribution in a professional context — understanding how attackers pivot between identities, how campaigns are correlated — the tracking parameter problem is more interesting than it first appears. A `utm_source` tag on a phishing link tells a defender which campaign the click came from. Stripping those before you click doesn't just protect your privacy; it also removes attribution data that could matter in an incident investigation.

PureLink strips indiscriminately. That's fine for personal browsing, but worth knowing if you're using it in a work context where link provenance matters.

### Additional Reading
- [CleanURLs](https://github.com/ClearURLs/Addon) — the serious, maintained version of this idea
- [URL Cleaner by Jibin](https://chromewebstore.google.com/detail/url-cleaner/dffbjiomnajbmlhjelpipfldgkijdemn) — Chrome store alternative
- [PureLink source](https://github.com/mr-dinesh/Vibecoding001-PureLink_browser_addon) — the Day 1 version, warts and all




