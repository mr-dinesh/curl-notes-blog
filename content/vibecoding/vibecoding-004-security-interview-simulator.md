---
title: "Vibecoding 004 — Building My Own Interview Coach for a Security Role"
date: 2026-03-17
tags: ["Security", "Career", "AI", "VibeCoding"]
aliases: ["/writing/vibecoding-004-interview_simulator_webapp/", "/writing/vibecoding-004-security-interview-simulator/"]
description: "A browser-based flashcard simulator with 80+ cards for Director-level cybersecurity interview prep — covering risk, governance, STAR storytelling, and leadership vocabulary."
---
![image](/images/writing/vibecoding-004-interview-simulator.png)


### Prompt Used: 
Build an interview simulator, for an upcoming job interview for a senior cybersecurity role. Generate flashcards which will give me appropriate vocabulary for risk, governance, leader, team building, story-telling in STAR format, context-action-impact frameworks.
The web-based app, should help me practice consistently by keep track of my effort in terms of practice time, weak areas, strengths and allow me to add sources for topics, content, role specific job descriptions if available. 
Example Role: Director SOC

Iteration2: Minor tweaks needed, some cards, the text is overflowing the card dimensions. Also provide a CSV upload capability to add new flashcards in addition to the existing manual mode of adding new cards.

### The Tool: CyberPrep

A self-contained, browser-based flashcard simulator for senior cybersecurity interview preparation. No backend, no login — runs entirely from a single HTML file with persistent local storage. Open it, start practising.

### Why I Built This

Senior security interviews at the Director or Head-of-Security level are different from technical interviews. They're not asking you to whiteboard an algorithm or recite CVEs. They're testing whether you can talk about risk in business terms, lead a team under pressure, justify security investment to a board, and tell a coherent story about your experience using frameworks like STAR or CAR (Context-Action-Result).

The vocabulary matters. "We had an incident" lands differently than "we experienced a material breach that required board notification under our regulatory obligations." Same event. Very different signal about how you think.

I needed a tool that would drill that vocabulary repeatedly until it felt natural. Nothing I found online was specific enough, so I built one.

### What the Cards Look Like

The 80+ cards span 7 categories. A few examples:

#### Risk & Governance
> Q: How do you communicate cyber risk to a non-technical board?
> A: Translate technical risk into business impact — financial exposure, regulatory penalty, reputational cost, operational disruption. Use scenarios, not statistics. "A ransomware event of this type typically costs $X in downtime and $Y in recovery" lands better than "our CVSS score is 9.1."

#### STAR Framework
> Q: Describe a time you had to make a security decision with incomplete information.
> A: Situation — [context]. Task — [your responsibility]. Action — [what you did and why, including what you didn't do]. Result — [outcome, ideally with a number or timeframe]. The interviewer is evaluating your reasoning process, not just the outcome.

#### Leadership
> Q: How do you build a security culture in an organisation that sees security as friction?
> A: You don't mandate it. You make secure behaviour the path of least resistance. Start with wins that remove friction — SSO, password managers, automated patching. Then build on credibility.

### How the Weighted Shuffle Works

Every card starts with equal weight. When you rate a card:
- **Easy** — weight decreases, card appears less frequently
- **Medium** — weight unchanged
- **Hard** — weight increases, card surfaces more in future sessions

After 3-4 sessions, the deck self-organises around your weak spots. The cards you're confident on disappear into the background. The ones you keep stumbling on keep showing up. It's spaced repetition without a complex scheduling algorithm.

### What Broke

The first version had a card overflow problem — longer answers were spilling outside the card boundary on the flip side. Looked terrible. The fix was straightforward (proper overflow handling and dynamic font scaling) but it took a second iteration to get right.

The second ask was CSV upload. Manually entering cards one by one was too slow when you want to add 20 role-specific questions from a job description. The CSV importer accepts `question,answer,category` rows and loads them directly into the deck alongside the pre-loaded cards.

### What I Learned

Flashcard apps are deceptively simple to describe and surprisingly fiddly to build. The 3D flip animation alone required careful CSS — `perspective`, `backface-visibility`, `transform-style: preserve-3d` — and it behaved differently in Safari than Chrome. Claude got it right on the second attempt.

The more useful lesson: the act of *writing the cards* was more valuable than using the app. Forcing yourself to articulate a concise answer to "how do you manage a SOC team under sustained pressure" is the preparation. The app just makes you do it repeatedly.

### Did It Help?

Yes. The vocabulary became more automatic. The STAR format stopped feeling like a template and started feeling like a natural way to structure an answer. Whether the interview goes well is still TBD — but the preparation is better than anything I've done before.

### Github Code Repo
[github.com/mr-dinesh/Vibecoding-004-Interview-Simulator-Webapp](https://github.com/mr-dinesh/Vibecoding-004-Interview-Simulator-Webapp/tree/main)

