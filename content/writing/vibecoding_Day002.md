---
title: "I Rebuilt Winamp's Visualizer in a Browser Tab"
date: 2026-03-15
tags: ["Audio", "WebGL", "Browser", "VibeCoding"]
description: "Used Claude to build VIZMIX — a Winamp-inspired 3D audio visualizer in the browser with five visualization modes, live mic input, and trippy WebGL effects."
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


### Interesting Asides
 - Stumbled upon [Pixabay | Royalty free music downloads](https://pixabay.com/music/), some amazing stuff here.
 - Tried [Audio Coffee Background Visualization](https://pixabay.com/music/upbeat-melodic-background-visualization-120919/), and a few more, will add the links here later.
 




