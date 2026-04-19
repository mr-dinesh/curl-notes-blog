---
title: "Getting Linux Audio Through VNC to Windows"
date: 2026-04-19
description: "A troubleshooting journey through PulseAudio, RTP, mysterious TCP timeouts, and eventually, music."
tags: ["linux", "vnc", "audio", "pulseaudio", "networking", "notes"]
---

VNC is excellent at showing you your Linux desktop on a Windows machine. It will faithfully deliver every pixel of your screen. What it will not deliver is sound. Your Linux machine could be playing a symphony and your Windows client would sit there in complete, smug silence.

This is the story of fixing that.

---

## The Setup

- Linux machine running Debian, PipeWire/PulseAudio, TigerVNC server
- Windows client watching via VNC
- TigerVNC 1.12 — no built-in audio support (that arrived in 1.13)

The goal: hear Linux audio on Windows speakers without replacing the VNC stack.

---

## Attempt 1: PulseAudio for Windows

The textbook answer is to run a PulseAudio client on Windows that connects to Linux's PulseAudio TCP server. Clean, official, documented.

I downloaded what I thought were the Windows binaries. Turned out to be the entire PulseAudio C source code — complete with 57 language translation files and a Bluetooth stack. Not quite a double-click installer.

Lesson learned: always check if it's a *release* zip or a *source* zip before spending twenty minutes wondering where the `.exe` is.

Moving on.

---

## Attempt 2: Stream Over HTTP

Linux's PulseAudio was already listening on TCP port 4713, restricted to localhost. The plan: open it to the LAN, stream audio as MP3 over HTTP, play it in VLC on Windows.

Simple. Except Windows refused to connect. Not "connection refused" — that would at least be honest. Just silence. A TCP timeout, on the same subnet, with no firewall rules visible on Linux.

Tested port 8888. Timeout. Port 8080. Timeout. The VNC connection on port 5901 worked perfectly, which made this even more baffling. The Windows machine could clearly see Linux — it just didn't want to knock on any door except the VNC one.

Windows Defender was turned off. All three profiles. Still nothing. Some mysteries are left unsolved.

---

## The Fix: Stop Pulling, Start Pushing

The breakthrough came from testing the reverse direction — Linux connecting *to* Windows. That worked immediately.

So instead of Windows pulling a stream from Linux, Linux pushes audio directly to Windows. A simple flip in perspective, embarrassingly obvious in hindsight.

The pipeline:

```bash
parec --format=s16le --rate=44100 --channels=2 \
  -d alsa_output.pci-0000_00_1f.3.iec958-stereo.monitor | \
ffmpeg -f s16le -ar 44100 -ac 2 -i pipe:0 \
  -c:a libmp3lame -b:a 128k \
  -f rtp -payload_type 14 \
  rtp://192.168.0.197:5004
```

`parec` captures whatever Linux is playing via the PulseAudio monitor source. `ffmpeg` encodes it as MP3 at 128kbps and fires it over RTP (UDP) to the Windows machine. On Windows, VLC opens `rtp://@:5004` and plays it.

There was a brief detour through G.711 audio — working, but sounding like a 2003 Skype call — before landing on MP3 stereo, which sounds entirely respectable.

---

## The Result

A desktop shortcut on Linux starts the stream. A one-line `.m3u` playlist on Windows opens it in VLC. Click, click, music.

```
#EXTM3U
#EXTINF:-1,Linux Audio
rtp://@:5004
```

The Linux side auto-starts at login via `~/.config/autostart`, with a five-second delay to let PulseAudio settle. No measurable impact on boot time.

---

## What I'd Do Differently

Check the direction assumptions first. The instinct is always "client connects to server" — but when something mysterious is blocking inbound connections, pushing outbound is often the cleaner path anyway.

Also: always verify you're downloading a binary release, not source code. Especially before a bio break.
