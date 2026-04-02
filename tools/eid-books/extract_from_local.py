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

GEMINI_MODEL = "gemini-2.0-flash"
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


def gemini_extract(api_key, title, description):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": EXTRACTION_PROMPT.format(
            title=title,
            description=description[:MAX_DESCRIPTION_CHARS],
        )}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 512},
    }

    for attempt in range(3):
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 429:
            print(f"    Rate limited — waiting 20s...")
            time.sleep(20)
            continue
        if not resp.ok:
            print(f"    Gemini error {resp.status_code}: {resp.text[:200]}")
            return []
        data = resp.json()
        break
    else:
        return []

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
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
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("Error: GEMINI_API_KEY not set.")
        print("Get a free key at: aistudio.google.com")
        print("Run:  set GEMINI_API_KEY=your_key_here")
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
        books = gemini_extract(api_key, title, description)
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
