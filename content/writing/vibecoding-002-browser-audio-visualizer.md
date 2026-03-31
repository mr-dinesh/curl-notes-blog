---
title: "I Rebuilt Winamp's Visualizer in a Browser Tab"
date: 2026-03-15
tags: ["Audio", "WebGL", "Browser", "VibeCoding"]
aliases: ["/writing/vibecoding_day002/"]
description: "Used Claude to build VIZMIX — a Winamp-inspired 3D audio visualizer in the browser with five visualization modes, live mic input, and trippy WebGL effects."
cover:
  image: "/images/writing/vibecoding-002-vizmix.png"
  alt: "VIZMIX 3D audio visualizer running in the browser"
  relative: false
---

### Create A Browser App - for visualising music
 - Music visualiser app insipired by [Justin's WinAmp]( It really kicks the llama's ass :-)
 - LLM used: Claude. Had used Gemini for Day1 (browser addon).

### Prompt Used
Create an interactive browser app which can visualize music, audio. Use X,Y,Z axis for visualization, of the music, with customizable effects like trippy, colours, waterfall. This was a feature available in Winamp.


### Outcome
 - VIZMIX — your Winamp-inspired 3D audio visualizer.
 - Source code is [here](https://github.com/mr-dinesh/Vibecoding_002_VIZMIX--Winamp-inspired-3D-audio-visualize/tree/main)
 
 
### Visualization Modes 
 - BARS — classic 3D frequency bars along the X axis, height on Y, time on Z
 - WAVE — dual waveform lines with mirror reflection
 - FALL — waterfall cascade where history scrolls back into Z depth
 - SPHERE — 1,800-point particle sphere that deforms to the beat
 - TUNNEL — an infinite zooming tunnel that warps with bass hits

### Audio Sources
 - 🎵 Drop/click any audio file (MP3, WAV, OGG, FLAC…)
 - 🎙 Live microphone input

### Customizable Effects
 - 🌀 TRIPPY — shifting background hues + geometry distortion
 - ✨ BLOOM — amplitude-driven brightness boost
 - 🪞 MIRROR — symmetrical reflection
 - 🔄 SPIN — auto-rotating camera orbit
 - 6 Color Palettes — Cyber, Fire, Ocean, Neon, Mono, Rainbow
 - Controls — sensitivity, height, smoothing, animation speed, volume, seek bar, and drag-to-orbit the 3D camera with your mouse (or touch).

 
### What could be better
- Not all the 5 Visualization Modes work very well.
- Would have liked more granular control of the effects
- Also looping of tracks, full-screen mode, better UX are ideas to work on in Version2.

### What Broke

SPHERE and TUNNEL — the two most ambitious modes — don't render correctly on all hardware. SPHERE loses its bass-deformation response on lower-end GPUs; TUNNEL stutters at high frame rates due to a depth buffer issue. Both are Claude-generated and both have the same root cause: the WebGL implementation assumes consistent `requestAnimationFrame` timing that mobile browsers and integrated graphics don't always deliver. The fix requires delta-time calculations. Version 2 problem.

BARS and WAVE work reliably. FALL is somewhere in between. If you're demoing this, stick to BARS.

### What I Learned

Claude generates functional WebGL code, but it codes to a happy path — a well-spec'd desktop browser on good hardware. Edge cases (mobile Safari, integrated graphics, high-DPI displays) aren't in scope unless you put them in scope explicitly. The lesson: be specific about the target environment in the initial prompt, not after something breaks.

Also: constraints drive creativity. "Use X, Y, Z axes" in the original prompt is what forced the 3D approach instead of the standard flat frequency bars you see everywhere. The best part of the output came directly from the most specific part of the prompt.

### The Security Angle

Building this was a reminder that the browser's permission model is doing real security work, even on something as harmless as a music visualiser. The Web Audio API and WebGL both require a user gesture to initialise — no page can start capturing audio or rendering 3D graphics without the user interacting first. Same reason autoplay video is blocked by default.

It's easy to dismiss these browser restrictions as friction. They're not. They're the same security boundary that stops a malicious page from silently activating your microphone. Worth appreciating.

### Interesting Asides
 - [Pixabay](https://pixabay.com/music/) has a surprisingly good library of royalty-free music for testing.
 - [Audio Coffee Background Visualization](https://pixabay.com/music/upbeat-melodic-background-visualization-120919/) — good test track for the waterfall mode.
 - [Source code](https://github.com/mr-dinesh/Vibecoding_002_VIZMIX--Winamp-inspired-3D-audio-visualize/tree/main)
 




