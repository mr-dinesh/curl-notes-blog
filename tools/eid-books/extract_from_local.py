#!/usr/bin/env python3
"""
Extract books from local eie_full.json (yt-dlp JSONL format).

Usage:
    set GROQ_API_KEY=your_key
    python extract_from_local.py
"""

import json
import csv
import time
import sys
import os
import requests

INPUT_FILE = r"C:\Users\Sushmita\eie_full.json"
OUTPUT_FILE = r"C:\Users\Sushmita\eid_books.csv"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"
MAX_DESCRIPTION_CHARS = 4000

EXTRACTION_PROMPT = """\
Extract all book titles and their authors mentioned in these podcast show notes.

Episode: {title}

Show Notes:
{description}

Return a JSON array. Each object must have:
  "title": the book title (string)
  "author": author name (string, or null if not mentioned)

Rules:
- Only include actual books (novels, non-fiction, essays, academic books)
- Exclude: articles, blog posts, papers, podcasts, websites, films, reports, speeches
- If no books are found, return []
- Return only valid JSON — no explanation, no markdown fences

Example: [{{"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman"}}]\
"""


def groq_extract(api_key, title, description):
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": EXTRACTION_PROMPT.format(
            title=title,
            description=description[:MAX_DESCRIPTION_CHARS],
        )}],
        "temperature": 0,
        "max_tokens": 512,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for attempt in range(3):
        resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code == 429:
            wait = int(resp.headers.get("retry-after", "20"))
            print(f"    Rate limited — waiting {wait}s...")
            time.sleep(wait)
            continue
        if not resp.ok:
            print(f"    Groq error {resp.status_code}: {resp.text[:200]}")
            return []
        data = resp.json()
        break
    else:
        return []

    text = data["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return []


def main():
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print("Error: GROQ_API_KEY not set.")
        print("Run:  set GROQ_API_KEY=your_key_here")
        sys.exit(1)

    # Load episodes from JSONL file
    episodes = []
    with open(INPUT_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ep = json.loads(line)
                episodes.append(ep)
            except json.JSONDecodeError:
                continue

    print(f"Loaded {len(episodes)} episodes from {INPUT_FILE}")

    rows = []
    total = len(episodes)
    for i, ep in enumerate(episodes, 1):
        title = ep.get("title", "")
        description = (ep.get("description") or "").strip()
        url = ep.get("webpage_url") or f"https://youtube.com/watch?v={ep.get('id','')}"

        if not description:
            print(f"  [{i}/{total}] SKIP (no description) — {title[:50]}")
            continue

        print(f"  [{i}/{total}] {title[:60]}")
        books = groq_extract(api_key, title, description)
        if books:
            print(f"         → {', '.join(b.get('title','?') for b in books[:3])}")
        for book in books:
            t = (book.get("title") or "").strip()
            if t:
                rows.append({
                    "Episode Title": title,
                    "Episode URL": url,
                    "Book Title": t,
                    "Author": (book.get("author") or "").strip(),
                })
        time.sleep(2)

    rows.sort(key=lambda r: r["Episode Title"])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Episode Title", "Episode URL", "Book Title", "Author"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone! Found {len(rows)} book mentions across {total} episodes.")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nImport to Google Sheets: File → Import → Upload → select eid_books.csv")


if __name__ == "__main__":
    main()
