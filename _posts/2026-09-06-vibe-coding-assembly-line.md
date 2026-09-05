---
layout: post
title: "Vibe Coding as an Assembly Line: Turning Ideas into Products, Brick by Brick"
date: 2026-09-06 00:00:00 +0800
categories: [tech]
tags: [vibe-coding, ai, product-development, mvp, workflow]
description: "A field guide to the full journey from pain point to shipped product with AI — requirement interviews, prioritized backlogs, MVP cutting, and an iteration loop that adds features like Lego bricks. The human–AI division of labor, drawn explicitly."
---

"Vibe coding" gets marketed as a party trick: type a sentence, watch an app appear. That part is real — a capable model will turn a well-formed prompt into a running program. What is not real is the implied workflow: that an idea plus a chat window equals a product. A one-line prompt produces a *demo*. A product is what survives the distance between a vague itch and something a real person reaches for every day. That distance has its own craft, and in the vibe-coding era it is the only craft left that matters.

This essay is a field guide to that distance — an assembly line for turning an idea into a working product, stage by stage. The AI does the mechanical work; a human makes the calls. The product grows like a Lego build: one small, verified, replaceable brick at a time, until the thing standing in front of you is not the picture you started with, but something better — a picture corrected by reality.

## The line in one picture

The pipeline has four phases — and one return loop, because every pass around the loop is one more shipped brick:

![The vibe-coding assembly line: Discover → Define → Build → Harden, with feedback looping back — one loop equals one shipped brick](/assets/images/fig-vibe-assembly-line.svg)

Every stage ends in a **handoff artifact** — a pain statement, a backlog, a one-page brief, a running slice — that the next stage consumes, and every artifact is machine-checkable wherever possible. The AI is both the worker and the inspector of its own work; you are the only honest referee. A stage with no artifact and no referee will drift.

## 1. Start with pain, not ideas

Ideas are cheap and plentiful; pain is the raw material. An idea is a hypothesis that someone, somewhere, hurts often enough and badly enough to change their behavior. Most failed projects die not from bad execution but from building the answer to a question nobody asked. The first job of the pipeline is therefore not to refine the idea but to interrogate it.

You supply the pain, because **the AI does not have your life** — it cannot feel the annoyance that recurs every Tuesday or the workaround that costs you an hour a week. The AI's role in this stage is the interrogator. Hand it your raw idea and let it play devil's advocate on a loop: *Who exactly feels this? How do they cope today, and what does that workaround cost? When did you last feel it — describe the moment. What would make you switch?* Three rounds of this, answered honestly, will separate a real need from a pleasant fantasy.

The test is whether the pain survives contact with specifics. Take a throwaway example that will run through this guide: "I should build a houseplant watering reminder app." Interrogated, the idea cracks open. Calendar reminders already exist — if the problem were *forgetting to water*, it would be solved. What actually hurts is different: you don't know how much water each plant wants, and you only notice when a leaf goes brown. That is a different product about *diagnosis*, not *scheduling* — and it survives the interrogation where the original idea does not.

The stage ends with a one-paragraph pain statement: who feels it, at what moment, and why their current solution falls short. If three rounds of questioning cannot produce that paragraph, the idea does not go on the line. **Killing an idea here is the cheapest decision in the entire pipeline** — cheaper by orders of magnitude than killing it after a month of building.

## 2. Requirements: let the AI interview you

Requirement gathering fails in both directions: people write wish lists ("it should also have dark mode, sharing, and a Mac app") and tools produce feature laundry lists. Neither captures what actually matters. The reliable method is a structured interview — with a role reversal. **The AI interviews you; you are the user, not the product owner.**

The AI's job is to run the interview well: questions in small batches, grouped by theme — the moments when the pain occurs, the frequency, the workarounds you tolerate, the moment you gave up on solving it, adjacent pains that piggyback on the same moment. Answer from your own experience only; do not invent users. You are the seed user, and the honesty of this hour determines the quality of everything downstream.

The AI then converts the raw conversation into **requirement cards**, each carrying four fields: *what* is needed, *who* needs it, *why now* (which concrete moment produces the need), and *how we would know it works* (a verification hint for later). The non-negotiable rule: **every card must trace back to something you actually said.** Models have read thousands of product requirements documents and will happily hallucinate plausible needs — "users want a social sharing feature" — that exist in no real moment of your life. A card that cannot be pointed back to a moment you described is a hallucinated requirement. Delete it. In the plant example, the interview surfaces a card the original idea never contained: *vacation mode* — because your answer to "what happens when you travel for a week?" described the plants dying while you were away. That card exists because you lived the moment.

## 3. Diverge, then prune

The backlog now takes shape through two alternating moves that must never be separated — divergence and pruning:

![The requirement funnel: divergent cards pour in, most die in the funnel, only Musts reach the MVP tray](/assets/images/fig-vibe-funnel.svg)

Divergence is the AI running free — every card decomposed into sub-requirements, edge cases, platform variants, adjacent users, counter-examples. Pruning is where you earn your keep: every card gets a MoSCoW stamp — Must, Should, Could, Won't — and only Musts enter scope. Then write the non-goals down explicitly: *this version will not do X*. **Non-goals matter more than goals** — they are the only thing that stops scope creep when the AI suggests "just one more feature." Pressure test: if more than a third of your cards are Musts, you have not cut yet. Tell the AI it is required to challenge your stamps; a "Should" that keeps arguing is a feature you are attached to, not a need.

Ninety percent casualties is a healthy rate — the corpses are context. They tell you, later, exactly what you gave up and why, which is what makes the backlog a *decision record* rather than a to-do list.

## 4. Argue about the shape, not the spec

The same set of needs can grow into a CLI tool, a web app, a browser extension, a mini program, a background script, an API — or no product at all. The shape determines distribution, discovery, maintenance, and build cost more than any feature decision you will make. So before writing a single task, argue with the AI about form.

Run every candidate shape through three questions. **Where will you remember to use it?** This decides how much friction the product may carry — a watering companion lives in your pocket and must push notifications, because nobody opens a web page to check a plant. A developer tool, by contrast, is fine as a CLI, because the terminal is where the moment happens. **How will anyone else find it?** A browser extension rides on the extension store; a mini program rides on WeChat search; a web app must be marketed. **Who feels it when it breaks?** Every shape is a maintenance contract you are signing with your future self.

The AI prices each shape — build effort, update cadence, distribution channel, failure modes — from its library of similar products; you decide, from your real usage patterns. Then prune once more: the shape discussion will kill or merge requirements that looked essential on paper. A plant app that lives on your phone does not need the multi-user family plan you were half-planning; a CLI does not need onboarding.

The artifact is a **one-page product brief**: the shape, the core loop (the path the user walks from trigger to value, in a few lines), the top Must requirements, and the non-goals. One page. If it takes more, you are still thinking in features instead of in behavior.

## 5. Cut the MVP until it hurts

The MVP is not "the full product with fewer features." It is the smallest complete loop: the shortest path from the moment of pain to the moment of value, with nothing missing in between. Draw that loop before you cut anything — in the plant example: *a plant turns sad → the app tells you, in plain words, what it needs → you act → the plant recovers*. The MVP is whatever makes that loop run end to end, once, for real. Every feature outside the loop goes to the backlog, politely, forever.

The AI's job here is translation: slice the brief into a task list, each task carrying a machine-checkable definition of done — "this command runs and produces this output," "this screen renders with these three states." **A task whose done cannot be checked by running something is not ready to build.** Your job is budgeting: approve the list the way you would approve a purchase order. A good sanity check — if the AI's task list would take you more than a day or two of continuous verifying to accept, the MVP is still too big. Cut again.

The target is not "complete." The target is *ugly but daily*: an MVP you would actually reach for tomorrow, not a polished artifact you would admire. If the finished MVP would not survive contact with your own daily life, you cut the wrong loop — or cut too much of the right one.

## 6. The AI builds; you run the line

Build is the phase where the human's instinct — grab the keyboard — is the biggest hazard. Your job is three verbs: **run it, watch it, say next.** Let the AI implement one task at a time, with the acceptance criteria written before the code. Feed tasks one at a time; never ask for "the whole app." The AI runs its own loop — implement, execute, read the error, fix — which is exactly the loop it is good at and you are bad at, because it never gets bored of error messages.

Insist on a vertical slice first: the first task must not be a landing page but the thinnest cut that pierces the whole stack — one real requirement, from interface to storage. Every later brick snaps onto that spine. This is what turns "the AI wrote a folder of files" into "the AI grew a product."

Two rules keep you honest. First, **never let the AI work more than one task without you running it and looking** — errors are cheapest the moment they appear, and this is also how you keep a true sense of the codebase, the "does this actually feel right" that no test covers. Second, if the AI is stuck on the same error for two rounds, stop it and read the task description yourself — the bug is usually in the spec or the context, not the code. Fix the instruction, not the code. That is the entire skill of being a good line foreman: knowing when the machine is the problem and when the blueprint is.

## 7. Verify every brick, then add the next

Now the product becomes a Lego build in the literal sense:

![Product growth from v1 to v7: solid bricks are features that survived daily use, one added per loop; a failed brick gets pulled, not mourned; the dashed outline is the product imagined on day one](/assets/images/fig-vibe-lego-growth.svg)

Each feature is a brick — self-contained enough to be added, tested, and, when it turns out wrong, removed without collapsing the wall. The rhythm of every loop is fixed: pull the next card from the top of the backlog, let the AI build it against the existing code, run regression (old bricks must not break — non-negotiable, every time), then *you* use the new feature for real. Only then does the brick count as laid.

**Your daily use is the quality department.** Dogfooding stops being a virtue and becomes the process: every day you use the product for its real purpose, every rough edge you hit is a defect report, filed straight into the fix queue by the AI. "The AI says it works" is not an acceptance criterion. You are the acceptance criterion.

The backlog rules keep the line from being hijacked: new ideas go to the *tail* of the backlog and wait their turn; the head is the priority order you set in the pruning stage, not your mood this morning. This one rule — new thoughts do not jump the queue — is what prevents the vibe-coding death spiral, where every impressive demo derails the plan and the product never passes version one. One loop, one brick, verify, repeat. It is deliberately boring. Boring is how assembly lines stay fast.

## 8. Tune and repair like a second job

Software is not finished when it works; it is finished when it stops costing you. The repair flow is a pipeline of its own: you report the symptom (what you did, what happened, what you expected), the AI locates the cause, fixes it, and — the step people skip — **explains the root cause in one paragraph that you actually read**. The explanation is the part that compounds: a bug you understand is a class of bugs you will recognize next time. Ask the AI the same question you would ask a junior engineer: "Where else does this same mistake live?" Fix the class, not the instance.

Tuning also deserves queue treatment. "Make it sharper" is a legitimate recurring task: performance on the slow path, empty states, copy that sounds like a robot, dead code the AI left behind. Schedule a cleanup pass every few loops and let the AI review its own growing codebase with fresh eyes.

Your role collapses to a single question, asked repeatedly: **is this worth fixing?** Treat every proposed repair as a quote — the AI states the change surface and the risk, you approve or defer. Deferring is a decision, not a failure; the backlog exists precisely so that "not now" does not mean "lost." This is the same judgment you exercised in pruning, now applied to maintenance, and it is the whole of your job description from here on.

## 9. Why the line feels fast

The speed is not a trick of faster code generation — model output is the least interesting part of this workflow. It comes from four structural changes, and one picture says more than the four paragraphs ever could:

![Calendar-time comparison, traditional solo build vs the assembly line — the wait is what got compressed](/assets/images/fig-vibe-speed.svg)

- **Decisions arrive early.** In a traditional solo build, decisions are made *while writing*, so every edit re-opens earlier decisions. On the line, every judgment is made in advance and frozen into an artifact — the AI executes against a settled contract and waits on the compiler, not on your thinking.
- **The bottleneck moved.** Solo development used to be bound by typing speed, API recall, and context loading — all mechanical, all now cheap. The remaining bottleneck, judgment, cannot be parallelized, but it *can* be sliced: one small decision per stage, each backed by an artifact and cheap to revisit. The line never waits for you to remember what you were doing.
- **Feedback loops shrank from weeks to hours.** The traditional timeline hides the product from reality until "version one," then discovers the assumptions were wrong — weeks too late. Here, every task is runnable, every brick is used by a real user (you) the day it lands, and first real-user feedback arrives on day four instead of month two.
- **Bricks are reversible.** A small, verified, replaceable unit is cheap to remove, so trying things stops being scary — the wall is never more than a few bricks from a change of plan. There is a fifth, psychological effect too: procrastination is a response to a vague looming target, and an assembly line never presents one. It always shows you the next brick, and the click of each one locking into place carries you to the next.

Underneath the speed sits the division of labor — who owns each move on the line:

![The division of labor: you own judgment, the AI owns volume, and every stage ends in a handoff artifact](/assets/images/fig-vibe-division.svg)

**Table 1.** The same split, compressed into a reference table.

| Stage | You (the human) | The AI | Handoff that moves the line |
|---|---|---|---|
| 1 · Pain discovery | live the pain; answer the interrogation honestly | plays devil's advocate, hunts the real need under the idea | a pain statement worth building for |
| 2 · Requirement interview | supply real experience; veto invented needs | runs the interview, structures answers into requirement cards | raw backlog of traceable cards |
| 3 · Diverge and prune | stamp Must / Should / Won't; write the non-goals | generates variants and edge cases; challenges weak priorities | prioritized backlog + explicit non-goals |
| 4 · Product shape | decides with real usage and discovery in mind | prices each shape: build cost, reach, upkeep | one-page product brief |
| 5 · Cut the MVP | approves scope; keeps it small enough to verify | slices the brief into tasks with checkable definitions of done | task list, machine-checkable |
| 6 · Build | runs it, watches it, says next | implements task by task; reads errors; fixes its own loop | a working vertical slice |
| 7 · Verify and extend | uses the product daily; accepts or rejects each brick | adds the next feature from the queue; runs regression | one working brick per loop |
| 8 · Tune and repair | approves what is worth fixing | diagnoses, fixes, explains root cause, tidies the code | a product that sharpens every week |
| Across the whole line | every judgment call, every veto, every acceptance | all mechanical work, all memory, all volume | an assembly line that never waits for a human to type |

The table is the argument of this essay in miniature: eight stages, and in none of them does the human write the code. What the human supplies — pain, experience, priorities, taste, acceptance — is precisely what the AI cannot supply for itself. **The line inverts the old ratio: you used to spend 80 percent of your time on mechanical work and 20 percent on judgment; now it is the reverse, and the 80 percent that remains is the part that makes the product good.**

## The product you end up with was not in the brief

The final property of the assembly line is that nobody knows, on day one, what the finished product will look like — and this stops being a bug the moment you accept it. The plan is not a prediction of the future; it is a mechanism for letting the future arrive early, one brick at a time, each one corrected by real use before the next is laid. The product that stands at the end was negotiated — between your original picture, the pain you keep discovering as you use the thing, and the thousand small decisions the line forced you to make out loud. It will be different from the idea you started with. That difference is not drift. It is the product having met reality and won.

Vibe coding, done right, is not "the AI writes your app." It is the first time one person can run a whole product line — researcher, product manager, architect, tester, and maintainer at once — because the typing is no longer the bottleneck. You do not program the product anymore. You run the line that builds it: you find the pain, you make the calls, you lay the bricks, and you keep the loop turning. The bricks are cheap, the click is satisfying, and the wall grows while you sleep.
