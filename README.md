# ContextMed

**Globally Informed. Locally Accurate.**

> Right Guideline. Right Geography. Right Drug. Right Source.

ContextMed is an agentic clinical decision-support system built with [MedGemma](https://huggingface.co/google/medgemma-4b-it) for the [MedGemma Impact Challenge](https://kaggle.com/competitions/med-gemma-impact-challenge).

A physician in **Berlin** gets ESC/AWMF/EMA guidelines. A physician in **Boston** gets ACC/AHA/FDA guidelines. Same patient, same condition — **different regulatory context, different correct answer**.

---

## The Problem

Clinical AI tools today are geography-blind. They return FDA guidelines to a German physician, recommend drugs not approved by EMA, and ignore regional formularies. In a world where 80%+ of physicians practice outside the US, this is a critical gap.

## The Solution

ContextMed adapts every clinical response to:

- **Geography** — FDA vs EMA vs AWMF vs NICE vs CDSCO guidelines
- **Specialty** — Emergency medicine vs family practice vs internal medicine
- **Experience level** — Medical student gets pathophysiology; attending gets action items
- **Patient context** — Allergies, renal function, current medications, lab values
- **Language** — Responds in the physician's working language

## Architecture

```
                    ┌─────────────┐
                    │   Doctor    │ specialty, country,
                    │   Context   │ experience, language
                    └──────┬──────┘
                           │
┌──────────┐    ┌──────────▼──────────┐    ┌──────────────┐
│ Patient  │───▶│     LangGraph       │◀───│  Conversation│
│   EHR    │    │   Agentic Pipeline  │    │    Memory    │
└──────────┘    └──────────┬──────────┘    └──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ PubMed   │ │ OpenFDA  │ │ Tavily   │
        │ Literature│ │ Drug     │ │ Guidelines│
        │          │ │ Safety   │ │ (geo-aware)│
        └──────────┘ └──────────┘ └──────────┘
              │            │            │
              └────────────┼────────────┘
                           ▼
                    ┌─────────────┐
                    │  MedGemma   │ 4B, 4-bit quantized
                    │  Reasoning  │ local GPU inference
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
                    │  Structured │ with safety alerts,
                    │  Response   │ citations, references
                    └─────────────┘
```

### LangGraph Pipeline

| Node | Role |
|------|------|
| **Planner** | MedGemma classifies intent, selects tools, extracts search terms |
| **Retriever** | Runs PubMed, OpenFDA, Tavily, and allergy checks **in parallel** |
| **Reasoner** | Generates evidence-grounded response adapted to doctor context |
| **Formatter** | Adds allergy alerts, citations, and tool metadata |

## Key Features

| Feature | Description |
|---------|-------------|
| Geography-aware guidelines | FDA, EMA, AWMF, NICE, CDSCO — correct source for correct country |
| Experience-adaptive | Student gets pathophysiology; senior gets bullet points |
| Allergy cross-reactivity | Catches penicillin-amoxicillin, sulfa family, NSAID cross-reactions |
| Critical care mode | 4-line emergency format for bedside use |
| Multi-turn memory | Conversation context preserved across interactions |
| Dynamic EHR parsing | Paste clinical notes → structured patient via MedGemma |
| SSE streaming API | Real-time token streaming via FastAPI |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Clinical LLM | MedGemma 4B (4-bit quantized, local GPU) |
| Agentic framework | LangGraph |
| Data models | Pydantic v2 |
| Literature | PubMed E-Utilities (free) |
| Drug safety | OpenFDA (free) |
| Guidelines | Tavily (geography-filtered) |
| API | FastAPI + SSE |
| Deployment | Kaggle GPU + Ngrok |

## Project Structure

```
contextmed/
├── contextmed/
│   ├── __init__.py
│   ├── config.py          # Environment-aware settings
│   ├── models.py          # Pydantic models (Doctor, Patient, etc.)
│   ├── medgemma.py        # MedGemma model loader & inference
│   ├── prompts.py         # Prompt templates (geography, experience-aware)
│   ├── memory.py          # Conversation & clinical notepad memory
│   ├── agent.py           # Main agent orchestrator
│   ├── server.py          # FastAPI server with SSE streaming
│   ├── tools/
│   │   ├── pubmed.py      # PubMed literature search
│   │   ├── openfda.py     # FDA drug safety data
│   │   ├── guidelines.py  # Tavily guideline search (geo-aware)
│   │   └── safety.py      # Allergy checking & dose adjustment
│   ├── agents/
│   │   ├── graph.py       # LangGraph workflow (Planner→Retriever→Reasoner→Formatter)
│   │   └── react.py       # ReAct agent (Think→Act→Observe loop)
│   └── data/
│       └── personas.py    # Sample doctors (USA/Germany) & patients
├── notebook.ipynb         # Self-contained Kaggle notebook
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Quick Start

### On Kaggle (recommended)

1. Upload `notebook.ipynb` to Kaggle
2. Add your secrets in Kaggle Settings:
   - `huggingface` — your HF token
   - `TAVILY_API_KEY` — your Tavily key
   - `ngrok` — your Ngrok token
3. Enable GPU accelerator (T4)
4. Run all cells

### Local Development

```bash
git clone https://github.com/YOUR_USERNAME/contextmed.git
cd contextmed
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
```

## Sample Queries

```python
# USA ER Attending — concise, action-oriented
agent.set_doctor("usa_er_attending")
agent.set_patient("USA_P001")
agent.query("What is the management plan for this heart failure exacerbation?")

# German Internist — ESC guidelines, German language
agent.set_doctor("de_internist")
agent.set_patient("DE_P001")
agent.query("Was ist der Behandlungsplan?")

# Medical Student — educational, detailed pathophysiology
agent.set_doctor("usa_med_student")
agent.set_patient("USA_P002")
agent.query("Explain the pathophysiology of lupus and how to diagnose it")

# Critical Care Mode — 4-line emergency format
agent.set_doctor("usa_er_attending")
agent.set_patient("USA_P001")
agent.query("Patient unresponsive, BP 80/50", mode="critical")
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/doctors` | List available physicians |
| GET | `/patients` | List available patients |
| GET | `/patient/{id}` | Full patient EHR |
| POST | `/ask/stream` | Stream clinical response (SSE) |
| POST | `/doctors/create` | Create custom physician |
| POST | `/patients/create/ehr` | Create patient from clinical notes |
| POST | `/patients/create/form` | Create patient from structured form |

## Competition Tracks

- **Main Track** — Full-featured agentic clinical decision support
- **Agentic Workflow Prize** — LangGraph pipeline with MedGemma-driven planning, parallel tool execution, and multi-turn memory

## License

MIT

---

Built for the [MedGemma Impact Challenge](https://kaggle.com/competitions/med-gemma-impact-challenge) by Google Research.
