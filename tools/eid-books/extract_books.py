#!/usr/bin/env python3
"""
Extract books mentioned in "Everything is Everything" podcast show notes.

Workflow:
  1. Fetch all episode descriptions from YouTube via yt-dlp (no API key needed)
  2. Cache them locally so you can re-run without re-fetching
  3. Send all descriptions to Claude in one Batches API call (50% cheaper)
  4. Write results to eid_books.csv — import into Google Sheets

Usage:
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=your_key
    python extract_books.py
"""

import json
import csv
import time
import sys
from pathlib import Path

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLIG8a9wNRHVu-Aw2VgUJacXlpsJMbF5Y_"
CACHE_FILE = "episodes_cache.json"
OUTPUT_FILE = "eid_books.csv"
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


# ---------------------------------------------------------------------------
# Step 1: Fetch episodes via yt-dlp (no API key required)
# ---------------------------------------------------------------------------

def fetch_episodes_from_youtube() -> list[dict]:
    """Fetch all video metadata including descriptions using yt-dlp."""
    try:
        import yt_dlp
    except ImportError:
        print("Error: yt-dlp not installed. Run: pip install yt-dlp")
        sys.exit(1)

    print("Fetching episode data from YouTube (no API key needed)...")
    print("This makes one request per episode — expect 3-5 minutes for 128 episodes.\n")

    episodes = []
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,   # needed to get descriptions
        "ignoreerrors": True,    # skip unavailable videos instead of crashing
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(PLAYLIST_URL, download=False)
        entries = info.get("entries", []) if info else []

        for i, entry in enumerate(entries, 1):
            if not entry:
                continue
            vid_id = entry.get("id", "")
            title = entry.get("title", "")
            print(f"  [{i}/{len(entries)}] {title[:70]}")
            episodes.append({
                "id": vid_id,
                "title": title,
                "url": entry.get("webpage_url") or f"https://youtube.com/watch?v={vid_id}",
                "description": entry.get("description", ""),
            })

    return episodes


def load_or_fetch_episodes() -> list[dict]:
    """Return episodes from local cache, or fetch and cache them."""
    cache = Path(CACHE_FILE)
    if cache.exists():
        print(f"Loading episodes from cache ({CACHE_FILE})...")
        with open(cache, encoding="utf-8") as f:
            episodes = json.load(f)
        print(f"Loaded {len(episodes)} episodes.\n")
        return episodes

    episodes = fetch_episodes_from_youtube()

    with open(cache, "w", encoding="utf-8") as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)
    print(f"\nCached {len(episodes)} episodes to {CACHE_FILE}\n")
    return episodes


# ---------------------------------------------------------------------------
# Step 2: Extract books via Batches API
# ---------------------------------------------------------------------------

def build_batch_requests(episodes: list[dict]) -> list[Request]:
    requests = []
    for ep in episodes:
        description = (ep.get("description") or "").strip()
        if not description:
            continue
        requests.append(Request(
            custom_id=ep["id"],
            params=MessageCreateParamsNonStreaming(
                model="claude-haiku-4-5",
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": EXTRACTION_PROMPT.format(
                        title=ep["title"],
                        description=description[:MAX_DESCRIPTION_CHARS],
                    ),
                }],
            ),
        ))
    return requests


def run_batch(client: anthropic.Anthropic, requests: list[Request]) -> dict:
    """Submit batch, poll until done, return {custom_id: result} mapping."""
    print(f"Submitting batch with {len(requests)} requests...")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch ID: {batch.id}\n")

    while True:
        batch = client.messages.batches.retrieve(batch.id)
        c = batch.request_counts
        total = c.processing + c.succeeded + c.errored + c.canceled + c.expired
        done = c.succeeded + c.errored + c.canceled + c.expired
        print(f"  {batch.processing_status} — {done}/{total} done "
              f"({c.succeeded} ok, {c.errored} errors)")

        if batch.processing_status == "ended":
            break
        time.sleep(15)

    print(f"\nBatch complete: {c.succeeded} succeeded, {c.errored} errored.\n")
    return {r.custom_id: r for r in client.messages.batches.results(batch.id)}


# ---------------------------------------------------------------------------
# Step 3: Parse results
# ---------------------------------------------------------------------------

def parse_books(text: str) -> list[dict]:
    """Parse a JSON book list from Claude's response text."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines and lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    client = anthropic.Anthropic()

    # 1. Episodes
    episodes = load_or_fetch_episodes()
    ep_by_id = {ep["id"]: ep for ep in episodes}
    print(f"Total episodes: {len(episodes)}")

    # 2. Batch extraction
    batch_reqs = build_batch_requests(episodes)
    skipped = len(episodes) - len(batch_reqs)
    if skipped:
        print(f"Skipping {skipped} episode(s) with no description.\n")

    batch_results = run_batch(client, batch_reqs)

    # 3. Compile rows
    rows = []
    for ep_id, result in batch_results.items():
        ep = ep_by_id.get(ep_id, {})
        if result.result.type != "succeeded":
            continue
        text = result.result.message.content[0].text
        books = parse_books(text)
        for book in books:
            title = (book.get("title") or "").strip()
            if not title:
                continue
            rows.append({
                "Episode Title": ep.get("title", ""),
                "Episode URL": ep.get("url", ""),
                "Book Title": title,
                "Author": (book.get("author") or "").strip(),
            })

    rows.sort(key=lambda r: r["Episode Title"])

    # 4. Write CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Episode Title", "Episode URL", "Book Title", "Author"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Found {len(rows)} book mentions across {len(episodes)} episodes.")
    print(f"Saved to: {OUTPUT_FILE}\n")
    print("To import into Google Sheets:")
    print("  File → Import → Upload → select eid_books.csv → Replace spreadsheet")


if __name__ == "__main__":
    main()
