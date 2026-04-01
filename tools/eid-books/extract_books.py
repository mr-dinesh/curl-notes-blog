#!/usr/bin/env python3
"""
Extract books mentioned in "Everything is Everything" podcast show notes.

Workflow:
  1. Fetch episode descriptions via Piped API (no key, works in CI)
     Falls back to yt-dlp if Piped is unavailable
  2. Cache locally — re-runs skip the fetch entirely
  3. Extract books using Groq API (free tier, no payment)
  4. Write eid_books.csv — import into Google Sheets

Usage:
    pip install -r requirements.txt
    export GROQ_API_KEY=your_key   # free at console.groq.com
    python extract_books.py
"""

import json
import csv
import time
import sys
import os
from pathlib import Path
from urllib.request import urlopen, Request as URLRequest
from urllib.parse import quote
from urllib.error import HTTPError, URLError

PLAYLIST_ID = "PLIG8a9wNRHVu-Aw2VgUJacXlpsJMbF5Y_"
CACHE_FILE = "episodes_cache.json"
OUTPUT_FILE = "eid_books.csv"
MAX_DESCRIPTION_CHARS = 4000

# Multiple Piped instances — tried in order until one works
PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.projectsegfau.lt",
    "https://piped-api.garudalinux.org",
    "https://pipedapi.drgns.space",
    "https://api.piped.yt",
    "https://piped.privacydev.net/api",
    "https://api.piped.adminforge.de",
    "https://pipedapi.reallyaweso.me",
]

# Invidious instances — fallback if all Piped instances fail
INVIDIOUS_INSTANCES = [
    "https://inv.nadeko.net",
    "https://invidious.privacydev.net",
    "https://yt.artemislena.eu",
    "https://invidious.fdn.fr",
    "https://invidious.nerdvpn.de",
    "https://iv.melmac.space",
    "https://yewtu.be",
    "https://invidious.lunar.icu",
    "https://invidious.io",
]

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

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
# Step 1a: Fetch via Piped API (preferred — works in CI/GitHub Actions)
# ---------------------------------------------------------------------------

def piped_get(base: str, path: str) -> dict:
    url = f"{base}{path}"
    req = URLRequest(url, headers={"User-Agent": "curl/8.0"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def find_working_piped_instance() -> str | None:
    for base in PIPED_INSTANCES:
        try:
            piped_get(base, f"/playlists/{PLAYLIST_ID}")
            print(f"  Using Piped instance: {base}")
            return base
        except Exception:
            continue
    return None


def fetch_episodes_via_piped(base: str) -> list[dict]:
    print("Fetching playlist from Piped API...")

    videos = []
    data = piped_get(base, f"/playlists/{PLAYLIST_ID}")
    videos.extend(data.get("relatedStreams", []))
    nextpage = data.get("nextpage")

    while nextpage:
        data = piped_get(base, f"/nextpage/playlists/{PLAYLIST_ID}?nextpage={quote(nextpage)}")
        videos.extend(data.get("relatedStreams", []))
        nextpage = data.get("nextpage")

    print(f"Found {len(videos)} videos. Fetching descriptions...")

    episodes = []
    for i, v in enumerate(videos, 1):
        vid_id = v.get("url", "").replace("/watch?v=", "").split("&")[0]
        title = v.get("title", "")
        print(f"  [{i}/{len(videos)}] {title[:70]}")

        description = ""
        try:
            stream = piped_get(base, f"/streams/{vid_id}")
            description = stream.get("description", "")
        except Exception as e:
            print(f"    Warning: could not fetch description — {e}")

        episodes.append({
            "id": vid_id,
            "title": title,
            "url": f"https://youtube.com/watch?v={vid_id}",
            "description": description,
        })
        time.sleep(0.3)

    return episodes


# ---------------------------------------------------------------------------
# Step 1b: Fallback — fetch via Invidious API (different proxy project)
# ---------------------------------------------------------------------------

def invidious_get(base: str, path: str) -> dict:
    url = f"{base}{path}"
    req = URLRequest(url, headers={"User-Agent": "curl/8.0"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def find_working_invidious_instance() -> str | None:
    for base in INVIDIOUS_INSTANCES:
        try:
            invidious_get(base, f"/api/v1/playlists/{PLAYLIST_ID}")
            print(f"  Using Invidious instance: {base}")
            return base
        except Exception:
            continue
    return None


def fetch_episodes_via_invidious(base: str) -> list[dict]:
    print("Fetching playlist from Invidious API...")

    videos = []
    page = 1
    while True:
        data = invidious_get(base, f"/api/v1/playlists/{PLAYLIST_ID}?page={page}")
        page_videos = data.get("videos", [])
        if not page_videos:
            break
        videos.extend(page_videos)
        page += 1

    print(f"Found {len(videos)} videos. Fetching descriptions...")

    episodes = []
    for i, v in enumerate(videos, 1):
        vid_id = v.get("videoId", "")
        title = v.get("title", "")
        print(f"  [{i}/{len(videos)}] {title[:70]}")

        description = ""
        try:
            stream = invidious_get(base, f"/api/v1/videos/{vid_id}")
            description = stream.get("description", "")
        except Exception as e:
            print(f"    Warning: could not fetch description — {e}")

        episodes.append({
            "id": vid_id,
            "title": title,
            "url": f"https://youtube.com/watch?v={vid_id}",
            "description": description,
        })
        time.sleep(0.3)

    return episodes


# ---------------------------------------------------------------------------
# Step 1c: Fallback — fetch via yt-dlp (works locally, may be blocked in CI)
# ---------------------------------------------------------------------------

def fetch_episodes_via_ytdlp() -> list[dict]:
    try:
        import yt_dlp
    except ImportError:
        print("Error: yt-dlp not installed. Run: pip install yt-dlp")
        sys.exit(1)

    playlist_url = f"https://www.youtube.com/playlist?list={PLAYLIST_ID}"
    print("Fetching via yt-dlp (fallback)...")

    episodes = []
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "ignoreerrors": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
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


# ---------------------------------------------------------------------------
# Fetch dispatcher + cache
# ---------------------------------------------------------------------------

def fetch_episodes_from_youtube() -> list[dict]:
    in_ci = os.environ.get("CI", "") == "true"

    print("Looking for a working Piped instance...")
    base = find_working_piped_instance()
    if base:
        return _finish_fetch(fetch_episodes_via_piped(base))

    print("All Piped instances unavailable. Trying Invidious...")
    base = find_working_invidious_instance()
    if base:
        return _finish_fetch(fetch_episodes_via_invidious(base))

    if in_ci:
        print("\nError: all Piped and Invidious instances are unavailable.")
        print("Re-run the workflow — instances are sometimes temporarily down.")
        sys.exit(1)

    print("All proxy instances unavailable — falling back to yt-dlp (local only)...")
    return _finish_fetch(fetch_episodes_via_ytdlp())


def _finish_fetch(episodes: list[dict]) -> list[dict]:
    if not episodes:
        print("\nError: fetched 0 episodes. Try re-running.")
        sys.exit(1)

    return episodes


def load_or_fetch_episodes() -> list[dict]:
    cache = Path(CACHE_FILE)
    if cache.exists():
        with open(cache, encoding="utf-8") as f:
            episodes = json.load(f)
        if episodes:
            print(f"Loaded {len(episodes)} episodes from cache.\n")
            return episodes
        print("Cache is empty — re-fetching...\n")

    episodes = fetch_episodes_from_youtube()

    with open(cache, "w", encoding="utf-8") as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)
    print(f"\nCached {len(episodes)} episodes.\n")
    return episodes


# ---------------------------------------------------------------------------
# Step 2: Extract books via Groq API
# ---------------------------------------------------------------------------

def groq_extract(api_key: str, title: str, description: str) -> list[dict]:
    payload = json.dumps({
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": EXTRACTION_PROMPT.format(
            title=title,
            description=description[:MAX_DESCRIPTION_CHARS],
        )}],
        "temperature": 0,
        "max_tokens": 512,
    }).encode()

    req = URLRequest(
        GROQ_API_URL,
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except HTTPError as e:
        if e.code == 429:
            retry_after = int(e.headers.get("retry-after", "15"))
            print(f"    Rate limited — waiting {retry_after}s...")
            time.sleep(retry_after)
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        else:
            print(f"    Groq error {e.code}: {e.read().decode()[:200]}")
            return []

    text = data["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return []


def extract_all_books(api_key: str, episodes: list[dict]) -> list[dict]:
    rows = []
    total = len(episodes)
    for i, ep in enumerate(episodes, 1):
        description = (ep.get("description") or "").strip()
        if not description:
            print(f"  [{i}/{total}] SKIP — {ep['title'][:50]}")
            continue

        print(f"  [{i}/{total}] {ep['title'][:60]}")
        books = groq_extract(api_key, ep["title"], description)
        if books:
            print(f"          → {', '.join(b.get('title', '?') for b in books[:3])}")
        for book in books:
            title = (book.get("title") or "").strip()
            if not title:
                continue
            rows.append({
                "Episode Title": ep["title"],
                "Episode URL": ep["url"],
                "Book Title": title,
                "Author": (book.get("author") or "").strip(),
            })
        time.sleep(2)

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print("Error: GROQ_API_KEY not set. Get a free key at console.groq.com")
        sys.exit(1)

    episodes = load_or_fetch_episodes()
    print(f"Processing {len(episodes)} episodes...\n")

    rows = extract_all_books(api_key, episodes)
    rows.sort(key=lambda r: r["Episode Title"])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Episode Title", "Episode URL", "Book Title", "Author"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone! Found {len(rows)} book mentions across {len(episodes)} episodes.")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nImport to Google Sheets: File → Import → Upload → select eid_books.csv")


if __name__ == "__main__":
    main()
