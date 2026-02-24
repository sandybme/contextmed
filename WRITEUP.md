# ContextMed: Globally Informed, Locally Accurate Clinical AI

## Project Name

**ContextMed** — Context Aware Agentic Clinical Decision Support

## Team

Sandhanakrishnan Ravichandran, M.Sc TUM, AI Engineer

---

## Problem Statement

### The Context Problem in Medical AI

Generic Large Language Models lack awareness of the three critical contexts that define clinical practice:

**1. Geographic Context**: A physician in Mumbai asking about emergency protocols receives "Call 911" instead of the correct Indian emergency number (112). Drug approvals differ between FDA (USA), EMA (Europe), and CDSCO (India). Treatment guidelines from ACC/AHA (USA) may contradict ESC (Europe) or AWMF (Germany) recommendations for the same condition. A medication approved in the United States may be unavailable or contraindicated in Germany.

**2. Temporal Context**: Medical knowledge evolves continuously. Guidelines updated in 2024 may contradict recommendations from 2022. LLMs with static training data provide outdated information on:

- Drug safety warnings (new black box warnings added post training)
- Revised clinical thresholds (updated blood pressure targets)
- Withdrawn medications or changed indications
- New evidence from recent clinical trials

**3. Clinical Context**: The same query requires fundamentally different responses based on:

- **Physician Experience**: A medical student needs pathophysiology explanations; an attending needs concise action items
- **Patient Factors**: Allergies, current medications, renal function, and lab values change recommendations
- **Clinical Urgency**: Routine consultations versus emergency situations require different response structures


| Region  | Regulatory Body | Guideline Organizations | Emergency Number |
| ------- | --------------- | ----------------------- | ---------------- |
| USA     | FDA             | ACC, AHA, CDC           | 911              |
| Germany | BfArM, EMA      | AWMF, DGK               | 112              |
| UK      | MHRA            | NICE, BNF               | 999              |
| India   | CDSCO           | ICMR, API               | 112              |


### Why Context Matters

A generic LLM recommending a medication approved by the FDA but not by the EMA creates real clinical risk. Similarly:

- Dosing recommendations differ between American and European guidelines
- First line therapies vary by regulatory jurisdiction
- Drug interactions depend on regionally available formulations
- Clinical workflows differ between healthcare systems

### Impact Potential

Clinical decision support errors directly impact patient safety. ContextMed addresses these gaps by:

1. **Reducing geographic prescribing errors** through region specific guideline retrieval
2. **Ensuring current evidence** via real time literature and guideline search
3. **Improving clinical workflow efficiency** through experience appropriate response formatting
4. **Enhancing patient safety** with automated allergy cross reactivity checking
5. **Supporting emergency care** with dedicated critical care mode

---

## Overall Solution: Context Aware Agentic RAG

### Architecture Overview

ContextMed implements a context aware agentic Retrieval Augmented Generation (RAG) system using MedGemma as the reasoning core. The system maintains awareness of three context layers throughout the clinical reasoning process.

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTEXT LAYER                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │  Geographic  │ │  Physician   │ │   Patient    │        │
│  │  (Country,   │ │  (Experience,│ │  (Allergies, │        │
│  │   Language)  │ │   Specialty) │ │   Labs, Meds)│        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
├─────────────────────────────────────────────────────────────┤
│     LangGraph ReAct Workflow (Think → Act → Observe)        │
│     ┌─────────┐    ┌─────────┐    ┌──────────────┐         │
│     │  Agent  │───▶│  Tools  │───▶│ Final Answer │         │
│     └────┬────┘    └────┬────┘    └──────────────┘         │
│          │              │                                   │
│          └──────────────┘ (loops until ready)              │
├─────────────────────────────────────────────────────────────┤
│  Context Aware Tool Layer                                   │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────┐  │
│  │ PubMed   │ │ OpenFDA  │ │ Guidelines │ │ Safety      │  │
│  │ Search   │ │ Drug     │ │ (Geography │ │ (Allergy/   │  │
│  │          │ │ Labels   │ │  Filtered) │ │  Dose)      │  │
│  └──────────┘ └──────────┘ └────────────┘ └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│        MedGemma 4B (4 bit quantized, local GPU)            │
└─────────────────────────────────────────────────────────────┘
```

### Why MedGemma + Context Aware RAG

MedGemma excels at medical reasoning but faces inherent limitations that context aware RAG addresses:


| Limitation              | How Context Aware RAG Solves It              |
| ----------------------- | -------------------------------------------- |
| Training data cutoff    | Real time guideline and literature retrieval |
| Geographic neutrality   | Country specific domain filtering            |
| Static knowledge        | Dynamic evidence grounding                   |
| Generic responses       | Experience level adaptation                  |
| Missing patient context | EHR integration with safety checks           |


### The Three Context Dimensions

**1. Geographic Context Implementation**

When a German physician queries treatment guidelines:

- System detects `doctor.country = "Germany"`
- Configures Tavily search with German specific domains: `awmf.org`, `escardio.org`, `dgk.org`, `aerzteblatt.de`, `ema.europa.eu`
- Appends query context: "AWMF Leitlinie deutsche guidelines Germany EMA"
- Returns ESC/AWMF guidelines instead of ACC/AHA guidelines

The same query from a USA physician automatically retrieves FDA/ACC/AHA sources.


| Country | Guideline Domains                                              |
| ------- | -------------------------------------------------------------- |
| USA     | acc.org, heart.org, fda.gov, cdc.gov, nih.gov, uptodate.com    |
| Germany | awmf.org, escardio.org, dgk.org, aerzteblatt.de, ema.europa.eu |
| UK      | nice.org.uk, bnf.nice.org.uk, gov.uk                           |
| EU      | escardio.org, ema.europa.eu, easl.eu                           |
| India   | icmr.nic.in, cdsco.gov.in, apiindia.org                        |


**2. Physician Context Implementation**

System prompts adapt based on `doctor.experience_level`:


| Experience Level | Response Style                                                                     |
| ---------------- | ---------------------------------------------------------------------------------- |
| Student          | Detailed pathophysiology, step by step reasoning, learning points, common pitfalls |
| Resident         | Decision frameworks, escalation criteria, evidence synthesis                       |
| Attending        | Concise action items, critical findings, disposition guidance                      |
| Senior           | Only novel information, significant safety alerts, practice changing evidence      |


**3. Patient Context Implementation**

The system ingests structured EHR data including demographics, chief complaint, allergies, current medications, and laboratory values. This enables:

- Allergy cross reactivity checking before any medication recommendation
- Renal dose adjustment based on eGFR
- Drug interaction analysis against current medications
- Personalized recommendations considering comorbidities

---

## Regular Mode vs Critical Mode

ContextMed operates in two distinct modes optimized for different clinical scenarios:

### Regular Mode

Designed for routine clinical consultations, outpatient encounters, and non urgent decision support.

**Characteristics**:

- Comprehensive evidence gathering from PubMed, guidelines, and drug databases
- Detailed explanations appropriate to physician experience level
- Full citation of sources with numbered references
- Educational context for learners
- Thorough consideration of alternatives and contraindications

**Response Structure**:

- Clinical reasoning with supporting evidence
- Specific recommendations with dosing
- Relevant citations and references
- Safety considerations

**Example Use Cases**:

- Outpatient medication adjustment
- Chronic disease management planning
- Differential diagnosis workup
- Treatment guideline clarification

### Critical Mode

Designed for emergency situations, ICU consultations, and time sensitive clinical decisions.

**Characteristics**:

- Rapid, actionable responses prioritizing speed
- Structured four point format for quick scanning
- Additional critical care guideline sources (SCCM, ESICM)
- Enhanced search with emergency medicine context
- Immediate safety alerts prominently displayed

**Response Structure**:

1. **Assessment**: Primary diagnosis with key supporting finding
2. **Immediate Action**: Specific intervention with exact dose or procedure
3. **Monitor**: Parameter to watch, target value, monitoring frequency
4. **Safety Alert**: Critical consideration based on patient specific factors

**Additional Critical Care Domains**:

- sccm.org (Society of Critical Care Medicine)
- esicm.org (European Society of Intensive Care Medicine)
- ccforum.biomedcentral.com (Critical Care Forum)
- pmc.ncbi.nlm.nih.gov (PubMed Central for research)

**Example Use Cases**:

- Hemodynamic instability management
- Acute respiratory failure
- Sepsis protocol initiation
- Cardiac arrest post resuscitation care

### Mode Comparison


| Aspect                 | Regular Mode              | Critical Mode            |
| ---------------------- | ------------------------- | ------------------------ |
| Response time priority | Thoroughness              | Speed                    |
| Evidence depth         | Comprehensive             | Focused                  |
| Response format        | Flexible narrative        | Structured 4 point       |
| Guideline sources      | Regional specialty        | Regional + Critical Care |
| Educational content    | Based on experience level | Minimal, action focused  |
| Safety alerts          | Integrated                | Prominently displayed    |


---

## Technical Details

### Model Configuration

**Base Model**: `google/medgemma-4b-it` (4 billion parameter instruction tuned variant)

**Quantization**: 4 bit NormalFloat (NF4) via BitsAndBytes reduces VRAM from approximately 16GB to approximately 4GB, enabling inference on consumer GPUs (T4, RTX 3080) with minimal quality degradation.

### Allergy Safety System

Before any medication recommendation, the system checks for direct matches and cross reactivity families:

- Penicillin family: amoxicillin, ampicillin, piperacillin, nafcillin
- Sulfa family: sulfamethoxazole, sulfasalazine, TMP SMX
- Cephalosporin family: cephalexin, ceftriaxone, cefazolin, cefepime
- NSAID family: ibuprofen, naproxen, ketorolac, diclofenac

### Real Time Streaming

The FastAPI backend implements Server Sent Events (SSE) for token by token streaming, providing immediate feedback during the 10 to 30 second generation time.

### API Endpoints


| Endpoint               | Method | Purpose                                           |
| ---------------------- | ------ | ------------------------------------------------- |
| `/doctors`             | GET    | List available physician personas                 |
| `/patients`            | GET    | List available patient cases                      |
| `/patient/{id}`        | GET    | Full patient EHR details                          |
| `/ask/stream`          | POST   | Streaming clinical query (mode: regular/critical) |
| `/doctors/create`      | POST   | Create custom physician                           |
| `/patients/create/ehr` | POST   | Parse unstructured clinical notes                 |


### Limitations and Future Work

1. **Language Support**: Currently optimized for English and German; expansion to additional languages planned
2. **Guideline Coverage**: Five regions supported; additional regulatory bodies (Japan PMDA, Australia TGA) in development
3. **Validation**: Clinical validation studies needed before deployment in actual patient care settings

---

## References

1. Singhal K, et al. "Large language models encode clinical knowledge." Nature 2023.
2. Google Health AI. "MedGemma: Open Medical Foundation Models." 2025.
3. ACC/AHA. "2022 Heart Failure Guidelines." Circulation 2022.
4. AWMF. "Nationale VersorgungsLeitlinie Chronische Herzinsuffizienz." 2023.
5. ESC. "2023 Focused Update on Heart Failure Guidelines." European Heart Journal 2023.
6. Yao S, et al. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023.

---

## Links

- **Video Demo**: [3 minute demonstration]
- **Source Code**: [https://github.com/sandybme/contextmed](https://github.com/sandybme/contextmed)

---

*Built for the MedGemma Impact Challenge 2026*