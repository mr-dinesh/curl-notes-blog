#!/usr/bin/env python3
"""
Fetch descriptions from YouTube using yt-dlp, then extract books using Gemini.

This script reads video IDs from your existing flat JSON file,
fetches the real description for each video, then calls Gemini to extract books.

Usage:
    set GEMINI_API_KEY=your_key
    python fetch_and_extract.py

Requirements: yt-dlp and requests must be installed.
    pip install yt-dlp requests
"""

import json
import csv
import time
import sys
import os
import subprocess
import requests

FLAT_JSON   = r"C:\Users\Sushmita\eie_full.json"      # your existing flat file
OUTPUT_CSV  = r"C:\Users\Sushmita\eid_books.csv"
CACHE_FILE  = r"C:\Users\Sushmita\eie_desc_cache.json" # saves progress

GEMINI_MODEL = "gemini-2.0-flash"
MAX_DESC_CHARS = 4000

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
- Return only valid JSON - no explanation, no markdown fences

Example: [{"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman"}]\
"""


def fetch_description(video_id):
    """Use yt-dlp to fetch the full description for a single video."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        result = subprocess.run(
            ["yt-dlp", "-j", "--no-playlist", url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"    yt-dlp error: {result.stderr[:100]}")
            return None
        data = json.loads(result.stdout)
        return (data.get("description") or "").strip()
    except subprocess.TimeoutExpired:
        print("    yt-dlp timed out")
        return None
    except Exception as e:
        print(f"    fetch error: {e}")
        return None


def gemini_extract(api_key, title, description):
    """Call Gemini API to extract book mentions."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": EXTRACTION_PROMPT.format(
            title=title,
            description=description[:MAX_DESC_CHARS],
        )}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 512},
    }
    for attempt in range(5):
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 429:
            wait = 60 * (attempt + 1)
            print(f"    Rate limited - waiting {wait}s...")
            time.sleep(wait)
            continue
        if not resp.ok:
            print(f"    Gemini error {resp.status_code}: {resp.text[:200]}")
            return []
        data = resp.json()
        break
    else:
        print("    All retries exhausted")
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


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("Error: GEMINI_API_KEY not set.")
        print("Get a free key at: aistudio.google.com")
        print("Run:  set GEMINI_API_KEY=your_key_here")
        sys.exit(1)

    # Load episodes from flat JSON
    episodes = []
    with open(FLAT_JSON, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ep = json.loads(line)
                episodes.append(ep)
            except json.JSONDecodeError:
                continue
    print(f"Loaded {len(episodes)} episodes from {FLAT_JSON}")

    # Load description cache (avoids re-fetching if interrupted)
    desc_cache = load_cache()
    print(f"Description cache has {len(desc_cache)} entries")

    rows = []
    total = len(episodes)

    for i, ep in enumerate(episodes, 1):
        video_id = ep.get("id", "")
        title = ep.get("title", "")
        url = ep.get("webpage_url") or f"https://youtube.com/watch?v={video_id}"

        print(f"[{i}/{total}] {title[:65]}")

        # Get description (from cache or fetch)
        if video_id in desc_cache:
            description = desc_cache[video_id]
            print(f"  (cached, {len(description)} chars)")
        else:
            print(f"  Fetching description via yt-dlp...")
            description = fetch_description(video_id)
            if description is None:
                description = ""
            desc_cache[video_id] = description
            save_cache(desc_cache)  # save after each fetch
            time.sleep(1)  # be polite to YouTube

        if not description:
            print(f"  SKIP - no description")
            continue

        print(f"  Description: {len(description)} chars - extracting books...")
        books = gemini_extract(api_key, title, description)

        if books:
            titles = ', '.join(b.get('title', '?') for b in books[:3])
            print(f"  Found: {titles}")
        else:
            print(f"  No books found")

        for book in books:
            t = (book.get("title") or "").strip()
            if t:
                rows.append({
                    "Episode Title": title,
                    "Episode URL": url,
                    "Book Title": t,
                    "Author": (book.get("author") or "").strip(),
                })

        # Save CSV after every episode (don't lose progress)
        rows_sorted = sorted(rows, key=lambda r: r["Episode Title"])
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Episode Title", "Episode URL", "Book Title", "Author"])
            writer.writeheader()
            writer.writerows(rows_sorted)

        time.sleep(5)  # between episodes

    print(f"\nDone! Found {len(rows)} book mentions across {total} episodes.")
    print(f"Saved to: {OUTPUT_CSV}")
    print("\nImport to Google Sheets: File -> Import -> Upload -> select eid_books.csv")


if __name__ == "__main__":
    main()
