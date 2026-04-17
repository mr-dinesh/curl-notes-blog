---
title: "Vibecoding 018 — Rescuing 247 Notepad++ Quotes Before They Stay Hidden"
date: 2026-04-17
description: "Notepad++ has a hidden easter egg — type the word 'random', select it, press F1, and a random quote appears. I extracted all 247 of them."
tags: ["vibecoding", "python", "notepad++", "quotes", "tools"]
aliases: ["/writing/vibecoding-018-npp-quotes/"]
---

![Notepad++ Quotes Extraction](/images/writing/vibecoding-018-npp-quotes.png)

## The Itch

Notepad++ has a hidden easter egg most people never find. Type the word `random` anywhere in the editor, select it, and press F1. A small window pops up with a single quote — a random one, drawn from a list of 247 buried in the source code. Sometimes it's a programming aphorism. Sometimes it's dark humour. Sometimes it's completely unhinged.

> *"Always code as if the guy who ends up maintaining your code will be a violent psychopath who knows where you live."*
> — Martin Golding

I stumbled on this years ago and kept triggering it when I wanted a laugh. Then one day I actually wanted to find a specific quote I'd seen — and realised I had no way to. The window appears, shows one quote, and closes. There's no index. No searchable list. The only way to find any given quote is to keep hitting the easter egg and hope.

That felt like a solvable problem.

---

## The Idea

The Notepad++ source code is public. The quotes live in a single file — a long list of attribution + text pairs, with `\n` as literal line breaks inside each entry. The format is consistent enough that a parser could extract every quote cleanly.

The goal: pull all of them out, clean up the escape sequences, and have a proper flat file I could actually use.

---

## The Build

The raw file had 274 lines. Each line follows this pattern:

```
Author: Quote text with \n for line breaks
```

Some entries have numbered variants (e.g. `Don Ho #3:`, `Anonymous #42:`). Some have URLs embedded. Some span what would be multiple paragraphs if the `\n` sequences were rendered.

The parser does two things:
1. Splits on the first `:` to separate attribution from text
2. Replaces `\n` literals with actual newlines

What came out was 247 distinct quotes, spanning:

- **Programming legends** — Kernighan, Stroustrup, Ritchie, Torvalds, Knuth territory
- **Don Ho originals** — the Notepad++ author contributed several of his own, ranging from philosophical to deliberately absurd
- **Anonymous community submissions** — the bulk of the list; these are the ones that made the rounds on forums circa 2006–2015
- **Wildcard entries** — a Space Invaders ASCII art render, a Dennis Ritchie quote rewritten as a Bruce Lee parody, and `Internet #404: Quote not Found`

A few favourites that hold up:

> *"Debugging is twice as hard as writing the code in the first place. Therefore, if you write the code as cleverly as possible, you are, by definition, not smart enough to debug it."*
> — Brian Kernighan

> *"The plural of regex is regrets."*
> — Anonymous #202

> *"int getRandomNumber() { return 4; // chosen by fair dice roll, guaranteed to be random. }"*
> — xkcd.com

> *"Why do programmers always mix up Halloween and Christmas? Because Oct 31 == Dec 25"*
> — Anonymous #195

> *"Artificial Intelligence is no match for natural stupidity."*
> — Terry Pratchett

> **Word of the Day: DEBUGGING** — *The classic mystery game where you are the detective, the victim and the murderer.*

The output is two files: `npp_quotes_raw.txt` (one quote per line, attribution inline, `\n` literals preserved) and `npp_quotes.txt` (same list, `\n` sequences rendered as actual newlines, ready to read or pipe).

---

## What You Can Do With 247 Quotes

The extraction is the easy part. What makes it worthwhile is everything downstream.

### 1. Terminal MOTD

Drop this in your `.bashrc` or `.zshrc`:

```bash
shuf -n 1 ~/npp_quotes.txt
```

Every new terminal session greets you with a random quote. Takes ten seconds to set up.

### 2. Mastodon / Social Bot

The `kagga_bot` skeleton in this same repo was built for exactly this kind of data. Swap in the quotes file, set a posting schedule, and you have a daily Notepad++ quote bot. The quotes are short enough to fit comfortably within character limits, and varied enough that you could post one a day for eight months without repeating.

### 3. Static JSON API

Convert the flat file to a JSON array once:

```python
import json, pathlib

lines = pathlib.Path("npp_quotes.txt").read_text().splitlines()
quotes = []
for line in lines:
    if ": " in line:
        author, text = line.split(": ", 1)
        quotes.append({"author": author.strip(), "quote": text.strip()})

pathlib.Path("quotes.json").write_text(json.dumps(quotes, indent=2, ensure_ascii=False))
```

Host `quotes.json` on any static file server. Any page can fetch a random one with a single `fetch()` call and no backend.

### 4. Hugo Shortcode for This Blog

A `random-quote` shortcode that reads from the JSON at build time — or a small JS snippet that fetches it client-side — would let any Vibecoding post pull in a contextually relevant quote without me having to look one up manually.

### 5. Screensaver / Wallpaper Generator

Feed the quotes into something like [quote-wallpaper](https://github.com/bbbenji/quote-wallpaper) or a simple Pillow script. Rotating desktop wallpaper with a new quote each morning. The ones with ASCII art (Space Invaders, the xkcd snippet) render surprisingly well in monospace.

### 6. Random Quote Widget

All 247 quotes are embedded below. A random one loads each time — hit the button to cycle through them.

<div id="npp-quote-widget" style="border-left:3px solid #888;padding:1rem 1.25rem;margin:1.5rem 0;background:rgba(128,128,128,0.07);border-radius:0 6px 6px 0;">
  <p id="npp-q" style="margin:0 0 0.5rem;font-style:italic;white-space:pre-wrap;line-height:1.6;">Loading...</p>
  <p id="npp-a" style="margin:0;font-size:0.85em;opacity:0.7;"></p>
  <button onclick="nppNext()" style="margin-top:0.75rem;padding:0.3rem 0.8rem;font-size:0.8em;cursor:pointer;border:1px solid #888;background:transparent;border-radius:4px;">another one &rarr;</button>
</div>
<script>
let _Q=[];
fetch('/data/npp-quotes.json').then(r=>r.json()).then(d=>{_Q=d;nppNext();});
function nppNext(){
  if(!_Q.length)return;
  const r=_Q[Math.floor(Math.random()*_Q.length)];
  document.getElementById('npp-q').textContent=r.quote;
  document.getElementById('npp-a').textContent='— '+r.author;
}
</script>

---

## What Vibecoding This Felt Like

This one was tiny by project standards — maybe two hours from "I wonder if these are extractable" to clean output file. No server, no API, no framework. Just a text file, a small parser, and a satisfying flat list at the end.

But there's something worth noting about small extractions like this. The quotes don't live anywhere useful in their original form. They're buried in C++ source, rendered once in a dialog box, and effectively inaccessible. Extracting them doesn't create anything new — it just makes something already real actually findable. A lot of useful work is exactly this shape: not building something from scratch, but rescuing something that exists but can't be reached.

The `kagga_bot` project earlier in this series did the same thing for Kannada poetry. Same instinct. Make the thing findable. Give it a URL or a flat file or a JSON key. The value was always there — you just had to open a door.

---

*Part of the 100 Vibe Coding Projects series.*
