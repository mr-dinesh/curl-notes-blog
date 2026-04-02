#!/usr/bin/env python3
"""
Extract books from local eie_full_desc.json (yt-dlp JSONL or JSON array format).

Usage:
    set GEMINI_API_KEY=your_key
    python extract_from_local.py
"""

import json
import csv
import time
import sys
import os
import requests

INPUT_FILE = r"C:\Users\Sushmita\eie_full_desc.json"
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

    for attempt in range(5):
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 429:
            wait = 60 * (attempt + 1)
            print(f"    Rate limited — waiting {wait}s...")
            time.sleep(wait)
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

    # Load episodes — supports both JSONL and JSON array formats
    episodes = []
    with open(INPUT_FILE, encoding="utf-8") as f:
        raw = f.read().strip()

    if raw.startswith("["):
        # JSON array (e.g. from yt-dlp playlist dump)
        outer = json.loads(raw)
        entries = outer.get("entries", outer) if isinstance(outer, dict) else outer
        for ep in entries:
            if isinstance(ep, dict):
                episodes.append(ep)
    else:
        # JSONL — one JSON object per line
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ep = json.loads(line)
                if isinstance(ep, dict):
                    episodes.append(ep)
            except json.JSONDecodeError:
                continue

    print(f"Loaded {len(episodes)} episodes from {INPUT_FILE}")
    with_desc = sum(1 for e in episodes if (e.get("description") or "").strip())
    print(f"Episodes with descriptions: {with_desc}/{len(episodes)}")

    FIELDNAMES = ["Episode Title", "Episode URL", "Book Title", "Author"]

    # Open CSV for progressive writing (write header only if file is new)
    csv_is_new = not os.path.exists(OUTPUT_FILE)
    csv_file = open(OUTPUT_FILE, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
    if csv_is_new:
        writer.writeheader()
        csv_file.flush()

    total = len(episodes)
    total_books = 0
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
                writer.writerow({
                    "Episode Title": title,
                    "Episode URL": url,
                    "Book Title": t,
                    "Author": (book.get("author") or "").strip(),
                })
                total_books += 1
        csv_file.flush()  # save after every episode
        time.sleep(5)

    csv_file.close()

    print(f"\nDone! Found {total_books} book mentions across {total} episodes.")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nImport to Google Sheets: File → Import → Upload → select eid_books.csv")


if __name__ == "__main__":
    main()
