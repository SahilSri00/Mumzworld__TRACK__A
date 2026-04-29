# Mumzworld Smart Shopping List — AI-Powered Message Parser

> **Track A: AI Engineering Intern**
>
> Turn a busy mom's messy text or voice message — in English or Arabic — into a structured shopping list, calendar events, and Mumzworld search queries. The system expresses uncertainty when information is vague and politely refuses out-of-scope requests.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/mumzworld-smart-list.git
cd mumzworld-smart-list

# 2. Install dependencies
pip install -r requirements.txt

# 3. Get a free API key from https://console.groq.com
cp .env.example .env
# Edit .env and paste your GROK_API_KEY

# 4. Run
python -m uvicorn src.main:app --port 8000

# 5. Open http://localhost:8000 in your browser
```

**Time from clone to first output: ~2 minutes.**

---

## What It Does

Given a mom's informal message like:

> "need diapers for Layla she's size 3 now, her birthday is next month need party stuff, and Noura just had a baby boy wanna send something nice under 150 dirhams"

The system returns structured JSON with:

| Output | Example |
|--------|---------|
| **Shopping items** | Diapers (size 3, diapering), Birthday supplies (party), Baby boy gift (≤150 AED) |
| **Calendar events** | Layla's Birthday (next month) |
| **Search queries** | "diapers size 3", "birthday party supplies kids", "newborn baby boy gift set" |
| **Confidence scores** | 95%, 85%, 90% per item |
| **Uncertainty flags** | "Exact birthday date not specified" |

### Key Features

- 🎙️ **Voice input** via Web Speech API (Chrome/Edge) — speak in English or Arabic
- 🌐 **Bilingual** — native Arabic output, not translated English
- ✅ **Schema validation** — Pydantic v2 enforces strict JSON structure
- ⚠️ **Uncertainty handling** — confidence scores, explicit "I don't know", out-of-scope refusal
- 📊 **16 eval test cases** — including adversarial inputs, gibberish, and prompt injection

---

## Architecture

```
  Mom's Message (text or voice)
          │
          ▼
  ┌─────────────────┐
  │   Web UI         │  Voice input (Web Speech API)
  │   HTML/CSS/JS    │  RTL support for Arabic
  └────────┬────────┘
           │ POST /api/parse
           ▼
  ┌─────────────────┐
  │   FastAPI        │  Language detection
  │   Python         │  Prompt engineering (few-shot)
  │                  │  Pydantic schema validation
  │                  │  Confidence thresholds
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │   Groq API       │  llama-3.3-70b-versatile
  │                  │  Fallback: llama-3.1-8b-instant
  └─────────────────┘
```

---

## Evals

See [EVALS.md](EVALS.md) for detailed results.

### Rubric

Each test case scored on 7 criteria:

| Criterion | What It Measures |
|-----------|-----------------|
| Language Detection | Correct EN/AR identification |
| Item Count | Extracted ≥ expected items |
| Categories | Correct Mumzworld category |
| Calendar Events | Detected birthdays/milestones |
| Out-of-Scope | Refused irrelevant messages |
| Uncertainty | Flagged vague/unknown info |
| Schema Validity | Valid JSON, no empty strings |

### Test Cases (16 total)

- **6 English** — diapers, car seats, maternity, nursery setup, detailed multi-item, budget gifts
- **3 Arabic** — formula + stroller, clothing + toys, bath + safety
- **1 Mixed language** — English with Arabic product names
- **3 Adversarial** — prompt injection, gibberish, single word "hmm"
- **3 Out-of-scope/Uncertain** — recipe question, politics (AR), vague teething request

Run evals: `python -m evals.run_evals`

---

## Tradeoffs

See [TRADEOFFS.md](TRADEOFFS.md) for full details.

**Problem selection**: Chose "Mom's message → shopping list" over return classifier, gift finder, duplicate detection, and symptom triage. This problem combines the most AI techniques (NLP, structured output, multilingual, uncertainty, evals) with the highest Mumzworld-specific business value.

**Model choice**: Llama 3.3 70B (via Groq API) — blazing fast inference (~800 tok/s), free tier, native JSON mode, excellent reasoning.

**What I cut**: Whisper API voice processing (used free browser Speech API instead), product catalog RAG, conversation memory, WhatsApp integration.

**What I'd build next**: Catalog search integration, WhatsApp bot, conversation memory, A/B testing of models with native Arabic speakers.

---

## Tooling

### What I Used

| Tool | Role |
|------|------|
| **Gemini (Antigravity agent)** | Pair-coding: architecture design, code generation, prompt engineering, eval framework, documentation |
| **Llama 3.3 70B (Groq)** | Primary LLM for the shopping list parser |
| **OpenAI SDK** | Client library for communicating with Groq API |
| **VS Code** | Editor |

### How I Used AI

- **Architecture**: Discussed problem selection tradeoffs and settled on the shopping list parser based on grading rubric alignment
- **Code generation**: Generated boilerplate (FastAPI setup, Pydantic models, CSS) via AI, then reviewed and edited for correctness
- **Prompt engineering**: Iterated on the system prompt and few-shot examples manually — the AI suggested the initial structure, but the Arabic examples and uncertainty rules were hand-tuned
- **Eval framework**: AI scaffolded the rubric and runner; I defined the test cases and expected outputs

### What Worked

- AI was excellent at generating the boilerplate (FastAPI routes, Pydantic schemas, CSS styling)
- System prompt iteration was faster with AI suggesting structured JSON schemas

### Where I Overruled

- Arabic few-shot examples: AI-generated Arabic initially read like translated English; rewrote to sound native
- Confidence thresholds: AI suggested 0.5; raised to 0.6 after testing showed too many false positives
- Error handling: Added more graceful degradation paths than the AI initially suggested

---

## Time Log

| Phase | Time |
|-------|------|
| Research & problem selection | ~45 min |
| Architecture & planning | ~30 min |
| Backend (FastAPI, parser, prompts) | ~1.5 hr |
| Frontend (HTML, CSS, JS) | ~1 hr |
| Eval framework & test cases | ~45 min |
| Documentation & polish | ~30 min |
| **Total** | **~5 hours** |
