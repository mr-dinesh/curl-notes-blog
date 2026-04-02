#!/usr/bin/env python3
"""
Debug script - run this FIRST to diagnose why extract_from_local.py produces empty CSV.

Usage:
    set GEMINI_API_KEY=your_key
    python debug_extract.py
"""

import json
import os
import sys
import requests

INPUT_FILE = r"C:\Users\Sushmita\eie_full.json"
GEMINI_MODEL = "gemini-2.0-flash"

# ── Step 1: Load file ─────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Loading file")
print("=" * 60)

episodes = []
try:
    with open(INPUT_FILE, encoding="utf-8") as f:
        raw = f.read()

    # Try JSON array first
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            episodes = data
            print(f"File format: JSON array ({len(episodes)} items)")
        elif isinstance(data, dict):
            # Maybe it's a single video or a playlist object
            if "entries" in data:
                episodes = data["entries"]
                print(f"File format: yt-dlp playlist JSON ({len(episodes)} entries)")
            else:
                episodes = [data]
                print(f"File format: single JSON object")
    except json.JSONDecodeError:
        # Try JSONL
        for i, line in enumerate(raw.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                episodes.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  Line {i}: JSON parse error: {e}")
        print(f"File format: JSONL ({len(episodes)} episodes)")
except FileNotFoundError:
    print(f"ERROR: File not found: {INPUT_FILE}")
    sys.exit(1)

print(f"Total episodes loaded: {len(episodes)}")

if not episodes:
    print("\nERROR: No episodes loaded. Check file path and format.")
    sys.exit(1)

# ── Step 2: Inspect description fields ───────────────────────────────────────
print()
print("=" * 60)
print("STEP 2: Checking descriptions")
print("=" * 60)

with_desc = [e for e in episodes if (e.get("description") or "").strip()]
without_desc = [e for e in episodes if not (e.get("description") or "").strip()]

print(f"Episodes WITH description:    {len(with_desc)}")
print(f"Episodes WITHOUT description: {len(without_desc)}")

if with_desc:
    print()
    print("First 3 episodes WITH descriptions:")
    for ep in with_desc[:3]:
        title = ep.get("title", "(no title)")
        desc = (ep.get("description") or "").strip()
        print(f"  Title: {title[:70]}")
        print(f"  Desc ({len(desc)} chars): {desc[:200]}...")
        print()
else:
    print()
    print("NO descriptions found! Checking available fields on first episode:")
    ep = episodes[0]
    print(f"  Keys: {list(ep.keys())}")
    # Check for alternative description field names
    for key in ["description", "fulldescription", "body", "content", "text", "summary"]:
        val = ep.get(key)
        if val:
            print(f"  Found text in field '{key}': {str(val)[:100]}")
    sys.exit(1)

# ── Step 3: Test Gemini on first episode ─────────────────────────────────────
print("=" * 60)
print("STEP 3: Testing Gemini API on first episode with description")
print("=" * 60)

api_key = os.environ.get("GEMINI_API_KEY", "").strip()
if not api_key:
    print("GEMINI_API_KEY not set - skipping API test")
    print("Set it with:  set GEMINI_API_KEY=your_key")
    sys.exit(0)

ep = with_desc[0]
title = ep.get("title", "")
desc = (ep.get("description") or "").strip()[:4000]

prompt = f"""Extract all book titles and their authors mentioned in these podcast show notes.

Episode: {title}

Show Notes:
{desc}

Return a JSON array. Each object must have:
  "title": the book title (string)
  "author": author name (string, or null if not mentioned)

Rules:
- Only include actual books (novels, non-fiction, essays, academic books)
- Exclude: articles, blog posts, papers, podcasts, websites, films, reports, speeches
- If no books are found, return []
- Return only valid JSON - no explanation, no markdown fences

Example: [{{"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman"}}]"""

url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0, "maxOutputTokens": 512},
}

print(f"Calling Gemini for: {title[:60]}")
resp = requests.post(url, json=payload, timeout=30)
print(f"HTTP status: {resp.status_code}")

if resp.ok:
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    print(f"Raw Gemini response:\n{text}")
else:
    print(f"Gemini error: {resp.text[:400]}")

print()
print("=" * 60)
print("Debug complete. Share the output above to diagnose the issue.")
print("=" * 60)
