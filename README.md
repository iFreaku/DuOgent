<div align="center">

# 🤖 DuOgent

### *Two agents. One plans. One executes. Both argue.*

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-SSE-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Pollinations](https://img.shields.io/badge/Powered%20by-Pollinations.ai-e8ff47?style=flat-square)](https://pollinations.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

> *"It's not who I am underneath, but what I do that defines me."*
> — Batman Begins

What DuOgent **does**: it takes your task, splits it into steps, has one AI execute each step, and another AI reject it until it's actually good.

What it **is** underneath: two language models in a loop, yelling at each other on your behalf.

---

## The Idea

Every AI tool gives you one shot. You type, it responds, you get something that's *almost* right but not quite, and now you're copy-pasting it into another prompt to fix it.

DuOgent automates that entire exhausting back-and-forth by making two agents do it instead of you.

**Agent 1 — The Planner/Reviewer**
The uptight one. Breaks your task into the minimum number of steps possible. Then sits there reviewing every piece of output like a senior dev on a Friday afternoon code review.

**Agent 2 — The Executor**
The one that actually does the work. Gets the full picture — original task, full plan, current step, and any critique from the last attempt. No excuses for "I didn't know what you wanted."

The loop runs until Agent 1 approves the work or the retry limit hits. Either way, you get a compiled final answer at the end.

> *"That's not flying. That's falling with style."* — Toy Story

---

## What can it actually do?

### 🖥️ Build web apps
Ask it to build a todo app, a calculator, a landing page. Agent 2 writes the code, Agent 1 reviews it, and if the output is a single-file HTML — it auto-saves to `/static` and renders in a live iframe preview inside the UI. You can preview it, resize it, or download it directly.

### 📝 Long-form writing
Blog posts, technical docs, research articles, product specs. The planner breaks it into sections, the executor writes each one with full memory of what came before.

### 🔬 Multi-step research
*"Explain transformer architecture, its evolution, and current limitations."* Not a one-shot prompt. A plan. DuOgent handles it like one.

### 📧 Content pipelines
Email sequences, onboarding flows, social copy. Each piece reviewed before the next one starts.

### 💻 Code generation
Scripts, components, utilities. Agent 1 actually checks if the code is coherent before you ever see it.

---

## How the loop works

```
Your task
    │
    ▼
Agent 1 makes a plan
    │
    ▼ for each step...
    │
    ├─► Agent 2 executes
    │       (full task + full plan + current step + any critique)
    │
    ├─► Agent 1 reviews
    │       ├── "approved" → next step
    │       └── "fix this specific thing" → Agent 2 tries again
    │
    ▼ all steps done
Agent 1 compiles everything into one final answer
```

Agent 2 always sees the **original task** and the **full plan**. Not just "write the HTML structure" with zero context. It knows what it's building, why, and where this step fits.

---

## Features

- ⬡ **BYOP** — Bring Your Own Pollen. Users connect their own [Pollinations.ai](https://pollinations.ai) account. You host the app, they cover the AI costs. $0 for you.
- 🎛️ **Per-agent model selection** — different model for Agent 1 and Agent 2. Run a smart planner and a fast executor.
- 📡 **Real-time streaming** — watch every step execute live via Server-Sent Events
- 🗂️ **Step tracker** — sidebar shows every step with live status (running / approved / retrying / forced)
- 💾 **HTML auto-save** — generated web apps saved to `/static`, previewed in iframe, downloadable
- 🔒 **localStorage** — your key, models, and all settings survive page refreshes
- ⚙️ **Param toggles** — enable/disable Temperature, Top P, Presence/Frequency Penalty individually (avoids the "can't use both" API error)
- 📱 **Mobile responsive** — hamburger menu, slide-in sidebar, works on phone
- ✕ **Cancel mid-run** — AbortController stops the stream instantly

---

## Powered by Pollinations.ai

DuOgent runs on **[Pollinations.ai](https://pollinations.ai)** — free, open AI inference with access to models from OpenAI, Google Gemini, Mistral, DeepSeek, and more. No separate accounts for each provider. One platform.

### ⬡ BYOP — Bring Your Own Pollen

> *"Why are you trying to hit me? Hit the target!"* — The Last Samurai

The target is: your users pay for their own AI usage. You pay nothing.

BYOP is Pollinations' auth flow that makes this happen. Users click **Connect with Pollinations**, sign in, approve access, and get redirected back to DuOgent with a key in the URL fragment (never hits server logs). The app picks it up, saves it to localStorage, and they're ready to run.

```javascript
// Optional: set your publishable key so the consent screen
// shows "DuOgent" instead of just your hostname
const BYOP_APP_KEY = 'pk_yourkey'; // in templates/index.html
```

Register yours at [enter.pollinations.ai](https://enter.pollinations.ai).

---

## Getting started

```bash
git clone https://github.com/iFreaku/DuOgent.git
cd DuOgent
pip install -r requirements.txt
python server.py
```

Open `http://localhost:5000`. Click **⬡ Connect with Pollinations** or paste a key manually. Pick models for each agent. Write your task. Hit Execute.

> *"Oh yes, it is happening."* — Elf

---

## Project structure

```
DuOgent/
├── dual_agent.py       # The two-agent loop — plan, execute, review, compile
├── server.py           # Flask backend — SSE streaming, /api/run, /api/save
├── requirements.txt
├── templates/
│   └── index.html      # Entire frontend. One file. No build step.
└── static/             # Generated HTML outputs land here (auto-created)
```

No node_modules. No webpack config. No `.env` to figure out. Just Python and one HTML file.

---

## Stack

| | |
|---|---|
| Backend | Python + Flask |
| Streaming | Server-Sent Events |
| Frontend | HTML + CSS + Vanilla JS |
| AI inference | [Pollinations.ai](https://pollinations.ai) |
| Markdown rendering | marked.js |
| Syntax highlighting | highlight.js |
| Fonts | IBM Plex Mono + Syne |

---

## Deployment

Works on Railway, Render, Heroku — anything that runs Python.

The `static/` folder is where HTML outputs get saved. On ephemeral filesystems (like Heroku's free dynos), those files won't persist across restarts. If that matters for your use case, swap the file write in `server.py` with an S3 upload.

---

## License

MIT. Do what you want.

---

<div align="center">

*Built on [Pollinations.ai](https://pollinations.ai) — free AI inference for everyone*

> *"Every passing minute is another chance to turn it all around."* — Vanilla Sky

</div>
