---
title: "I Asked AI to Help Me Build a Home Radio Server on a Sunday Afternoon"
date: 2026-03-22
tags: ["Self-Hosted", "Media", "Docker", "VibeCoding"]
description: "Tried to build a home Icecast radio server to stream MP3s to my phone. What actually happened: four Docker containers, a Mega.nz dead-end, and a surprisingly working result."
---

### I Asked an AI to Help Me Build a Home Radio Server. Here's What Actually Happened.

I have a few hundred MP3s sitting in a folder on my laptop — old Kannada film songs,
some Tamil classics, a few English albums I ripped years ago. I wanted to stream
them to my phone, maybe share the stream with family. Simple enough idea.

I'd heard of Icecast. I knew Liquidsoap existed. I had no intention of reading
their documentation on a Sunday afternoon.

So I opened Claude and said: build me an Icecast server that streams from Mega.nz.

---

### The First Pushback 

The AI didn't just start writing config files. It pointed out something I hadn't
thought through: Mega.nz uses end-to-end encryption. There's no public URL you
can hand to a streaming server. You'd need to decrypt locally first, then re-serve.
That's a pipeline, not a simple mount.

We dropped Mega and moved to Cloudflare R2 instead — S3-compatible, free egress,
works with rclone. Better fit for the use case.

Then I said I wanted to self-host on my home laptop to keep costs at zero.
We talked through the real constraints: dynamic IP from my ISP, possible port
blocking, upload speed as the listener ceiling. Things most tutorials skip.

---

### The Build 

The stack ended up being four Docker containers:

- **Icecast2** — the actual stream server
- **Liquidsoap** — reads playlists, encodes to MP3, pushes to Icecast
- **Node.js** — a small web server for playlist management
- **Navidrome** — added later for on-demand playback

The AI generated a `docker-compose.yml`, an Icecast config, a Liquidsoap script,
and a web UI. The design of the UI is dark and minimal — something between a
broadcast console and a text editor.

---

### What Broke During Deployment

A lot, in sequence.

The Liquidsoap config used `on_metadata` which was renamed to `source.on_metadata`
in v2.2. Then `server.register` had a different call signature than the AI expected.
Then the music paths inside the Docker container didn't match what was written in
the playlist file — `/home/tester/Music` versus `/music`.

Each error had a clear log message. Each fix was a one-liner. None of it was
particularly dramatic, but it took about fifteen iterations to get to a working
stream.

The part that surprised me: the AI remembered the project path across the whole
conversation. When I said "no audio again," it didn't ask me to start over. It
asked for the logs and diagnosed from there.

---

### The Navidrome Addition

Icecast is radio — everyone hears the same thing, you can't click individual
tracks. When I asked for that, the AI explained the distinction clearly and
suggested Navidrome as a second service running alongside Icecast. Same music
folder, different port, different purpose.

Adding it was one block in the docker-compose file. It was running in under
two minutes.

---

### Tailscale

The cleanest part of the whole thing. One install command, one authentication
step, and my home server had a stable private address accessible from my phone
on mobile data. No port forwarding, no DuckDNS, no open ports on the router.

I wish I'd done this years ago for other things.

---

### What Vibecoding Is

People use the word to mean different things. For me, on this project, it meant:
I described what I wanted in plain language, reviewed what came back, corrected
it when it was wrong, and kept going. I didn't write the Liquidsoap config from
scratch. I also didn't blindly paste code without reading it.

The AI was wrong about the Liquidsoap API version. It was right about Mega's
encryption problem. It caught the path mismatch faster than I would have reading
logs alone.

The useful mental model: it's a collaborator that knows a lot and makes mistakes.
Same as most collaborators.

---

### The code, If You Want It

Everything is on GitHub — docker-compose, configs, the web UI, scripts for
generating playlists and fetching cover art automatically. It runs on any Linux
machine with Docker. Total monthly cost: zero.

The stream URL is `http://YOUR_TAILSCALE_IP:8000/stream`. Open it in VLC or
any app that handles HTTP audio streams. Or open the listener page in a browser.

[Github Repo Link](https://github.com/mr-dinesh/home-media-player)
