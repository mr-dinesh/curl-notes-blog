---
title: "Reading The Wealth of Nations with a Paragraph-Level AI Tutor"
date: 2026-04-09
tags: ["Python", "Flask", "Gemini", "LLM", "Books", "VibeCoding"]
aliases: ["/writing/vibecoding-012-wealth-of-nations-reader/"]
description: "A personal reader app for Adam Smith's Wealth of Nations — click any paragraph, ask Gemini questions about it in the full chapter context. Built in one session with Claude Code."
---

### Building a Personal AI Reader for The Wealth of Nations

*Project #12 of the 100 Vibe Coding Projects challenge*

---

I've been meaning to read Adam Smith's *The Wealth of Nations* for years. It sits in the cultural background of every economics conversation — the invisible hand, the division of labour, the theory of wages — but the full 900-page text is dense and I kept bouncing off it.

Then I saw [Andrej Karpathy's tweet](https://x.com/karpathy/status/1886192184808149383) about building a focused LLM reading tool. The idea clicked: what if I could read the book and ask questions *in context* — not "what does Adam Smith say about wages" as a generic ChatGPT query, but "explain this specific paragraph, in the context of this chapter I'm currently reading"?

That's the whole product. A reader where every paragraph is a prompt waiting to happen.

---

### The Stack

- **Python 3 + Flask** — backend API and page rendering
- **Google Gemini 2.0 Flash** — fast, large-context LLM for Q&A and summarisation
- **Project Gutenberg** — public domain plain text of the book
- **Vanilla HTML/CSS/JS** — three-panel reader UI, no framework
- **Render.com** — free hosting
- **Cloudflare Tunnel** — for future custom domain setup

### How It Works

The backend exposes three API routes:

```
GET  /api/chapter/<id>   # returns chapter text as JSON
POST /api/ask            # paragraph Q&A with chapter context
POST /api/summarize      # full chapter summary
```

The context window for each question is deliberately generous: the full chapter text (up to ~12,000 characters), the specific paragraph selected, and the user's question. Gemini can see *why* a passage says what it says — the full argument around it.

A small parser splits the Project Gutenberg text into 33 chapters and their paragraphs, saved as `book_data.json` at setup time.

### The UI

Three panels: a dark sidebar with chapters grouped by Book, a parchment-toned reading area, and a Q&A panel that slides in from the right when you click a paragraph.

The design leans into the editorial aesthetic — Playfair Display headings, EB Garamond body text, cream backgrounds, amber accents. It should feel like reading a well-designed book, not a SaaS dashboard.

Selected paragraphs get an amber left-border highlight. The Q&A panel shows the paragraph quoted at the top. Ctrl+Enter submits a question.

### What Actually Happened While Reading

Adam Smith is more nuanced than his reputation. The "invisible hand" appears *once* in Book IV, almost in passing. The real substance is in Book I's theory of wages and Book V's surprisingly modern analysis of public expenditure and taxation.

Having Gemini explain the historical context — mercantilism, physiocracy, the Navigation Acts — made chapters readable that would have otherwise needed hours of Wikipedia cross-referencing. I've read further into this book in the past week than in the previous five years of good intentions.

### The Build

The whole thing was built with Claude Code in a single session — from the book parser through the Flask backend, the three-panel UI, auth, GitHub push, and Render deployment. The only manual step was filling in the API key.

**Source:** [github.com/mr-dinesh/Wealth_of_Nations_Reader_App](https://github.com/mr-dinesh/Wealth_of_Nations_Reader_App)
