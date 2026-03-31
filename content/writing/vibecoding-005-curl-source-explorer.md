---
title: "Making a 30-Year-Old Codebase Approachable With AI"
date: 2026-03-19
tags: ["Open Source", "Learning", "Curl", "VibeCoding"]
aliases: ["/writing/vibecoding-005-curl_source_explorer/"]
description: "A browser app that walks you through curl's internals — DNS, TLS, cookies, redirects — with AI explanations tuned to your experience level and progress tracking."
cover:
  image: "/images/writing/vibecoding-005-curl-explorer.png"
  alt: "Curl Source Explorer showing a function with AI explanation"
  relative: false
---

## Curl Source Explorer: Learn a 30-Year-Old Codebase Without Getting Lost

Curl has been running on virtually every computer on the planet since 1998. It's one of the most-used pieces of software ever written — and almost nobody who uses it daily has ever read a line of its source code.

That's partly because diving into a mature C codebase is intimidating. There are no onboarding docs for the internals, no guided tour, no one to ask why a particular function was written the way it was. You're either grepping through 170,000 lines alone, or you're not reading it at all.

I built a small browser app to fix that.

## Curl Source Explorer 
The app lets you pick a module — the DNS resolver, the TLS handshake, the cookie engine, the HTTP redirect logic — and step through its key functions one by one. For each concept, you get the actual source code side-by-side with an AI-generated explanation tuned to your experience level. A complete beginner gets plain-English analogies. An experienced C programmer gets architecture notes, edge cases, and the tradeoffs baked into the implementation.

It also tracks your progress. You mark concepts as understood or flagged for review, jot notes directly on each function, and quiz yourself when you want to test retention. Everything persists locally across sessions.

The whole thing runs in the browser with no installation. Drop two files in a folder, spin up a local server, paste a free Groq API key, and you're reading curl internals with an expert looking over your shoulder.

It won't replace reading the code yourself — and it's honest about that. Every snippet has a direct link to the live GitHub file, with a clear disclaimer that the embedded code is a snapshot and curl commits almost daily. The goal isn't to replace the source. It's to make the source approachable enough that you actually open it.

Built with React, Groq (Llama 3.3 70B), and real curl source from github.com/curl/curl.

### Prompt Used

> *Build a browser-based learning app for the curl source code. The app should let a user select a module — DNS resolver, TLS handshake, cookie engine, HTTP redirect logic — and step through its key functions one by one. For each function, show the actual source code alongside an AI-generated explanation tuned to the user's experience level. Beginners should get plain-English analogies. Experienced C programmers should get architecture notes, edge cases, and implementation tradeoffs. The app should track progress: users mark concepts as understood or flagged for review, add notes, and quiz themselves. Everything should persist across sessions. Use React and the Groq API (Llama 3.3 70B). Every code snippet must link directly to the live file on GitHub, with a disclaimer that the embedded code is a snapshot.*

### GitHub Repo

[github.com/mr-dinesh/Curl-Source-Code-Explorer](https://github.com/mr-dinesh/Curl-Source-Code-Explorer)
