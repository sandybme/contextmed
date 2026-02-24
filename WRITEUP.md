# ContextMed: Globally Informed, Locally Accurate Clinical AI

## Project Name
**ContextMed** — Geography Aware, Experience Adaptive Clinical Decision Support

## Team
Sandhanakrishnan Ravichandran, M.Sc TUM, AI Engineer

---

## Problem Statement

### The Geography Problem in Medical AI

Large Language Models trained on predominantly Western medical literature exhibit significant geographic bias. A physician in Mumbai asking about emergency protocols might receive "Call 911" instead of the correct Indian emergency number (112). More critically, drug approvals, treatment guidelines, and clinical protocols vary substantially across regulatory bodies:

| Region | Regulatory Body | Guideline Organizations |
|--------|-----------------|------------------------|
| USA | FDA | ACC, AHA, CDC |
| Germany | BfArM, EMA | AWMF, DGK |
| UK | MHRA | NICE, BNF |
| India | CDSCO | ICMR, API |

A generic LLM recommending a medication approved by the FDA but not by the EMA creates real clinical risk. Similarly, dosing recommendations, contraindications, and first line therapies differ between ACC/AHA guidelines (USA) and ESC guidelines (Europe) for the same condition.

### The Temporal Problem

Medical knowledge evolves rapidly. Guidelines updated in 2024 may contradict recommendations from 2022. LLMs with static training data cannot reflect:
- Updated drug safety warnings (e.g., new black box warnings)
- Revised clinical thresholds (e.g., updated blood pressure targets)
- Withdrawn medications or changed indications
- New evidence from recent clinical trials

A model trained on data from 2023 providing heart failure guidance in 2025 may miss critical updates to SGLT2 inhibitor recommendations or updated ejection fraction classifications.

### The Experience Gap

A third year medical student requires fundamentally different guidance than a senior attending physician:
- **Student**: Needs pathophysiology explanations, step by step reasoning, common pitfalls
- **Resident**: Needs decision frameworks, escalation criteria, evidence synthesis
- **Attending**: Needs concise action items, critical findings, disposition guidance
- **Senior Physician**: Needs only novel information, significant safety alerts, practice changing evidence

Generic medical AI treats all physicians identically, creating either information overload for experienced clinicians or insufficient depth for learners.

### Impact Potential

Clinical decision support errors directly impact patient safety. Geographic medication errors, outdated guideline recommendations, and inappropriate response complexity represent preventable harm vectors. ContextMed addresses these gaps by:

1. **Reducing geographic prescribing errors** through region specific guideline retrieval
2. **Ensuring current evidence** via real time literature and guideline search
3. **Improving clinical workflow efficiency** through experience appropriate response formatting
4. **Enhancing patient safety** with automated allergy cross reactivity checking

---

## Overall Solution: MedGemma Powered Agentic RAG

### Architecture Overview

ContextMed implements an agentic Retrieval Augmented Generation (RAG) system using MedGemma as the reasoning core. Rather than relying on MedGemma's parametric knowledge alone, the system augments responses with real time evidence retrieval.

```
┌─────────────────────────────────────────────────────────────┐
│           Next.js Frontend (SSE Streaming)                  │
├─────────────────────────────────────────────────────────────┤
│              FastAPI Server (Real time SSE)                 │
├─────────────────────────────────────────────────────────────┤
│              ContextMedAgent Orchestrator                   │
├─────────────────────────────────────────────────────────────┤
│     LangGraph ReAct Workflow (Think → Act → Observe)        │
│     ┌─────────┐    ┌─────────┐    ┌──────────────┐         │
│     │  Agent  │───▶│  Tools  │───▶│ Final Answer │         │
│     └────┬────┘    └────┬────┘    └──────────────┘         │
│          │              │                                   │
│          └──────────────┘ (loops until ready)              │
├─────────────────────────────────────────────────────────────┤
│  Tool Layer                                                 │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────┐  │
│  │ PubMed   │ │ OpenFDA  │ │ Guidelines │ │ Safety      │  │
│  │ Search   │ │ Drug     │ │ (Tavily)   │ │ (Allergy/   │  │
│  │          │ │ Labels   │ │            │ │  Dose)      │  │
│  └──────────┘ └──────────┘ └────────────┘ └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│        MedGemma 4B (4 bit quantized, local GPU)            │
└─────────────────────────────────────────────────────────────┘
```

### Why MedGemma + RAG Instead of MedGemma Alone

MedGemma excels at medical reasoning but faces inherent limitations:

1. **Training Data Cutoff**: Cannot access post training publications or guideline updates
2. **Geographic Neutrality**: Trained on mixed corpora without explicit regional weighting
3. **Hallucination Risk**: May generate plausible but incorrect drug dosages or interactions

By positioning MedGemma as the reasoning agent that decides which external tools to invoke, we leverage its medical comprehension while grounding responses in verifiable, current evidence.

### ReAct Workflow Implementation

The system implements Reasoning and Acting (ReAct) through LangGraph:

**Agent Node**: MedGemma analyzes the query and physician/patient context, then outputs a structured tool selection:
```json
{"tool": "search_guidelines", "params": {"query": "heart failure diuretic dosing"}}
```

**Tools Node**: Executes the selected tool asynchronously:
- `search_pubmed`: NCBI E Utilities API for recent literature
- `search_openfda`: FDA drug label database for safety information
- `search_guidelines`: Tavily search with geography filtered domains
- `check_allergies`: Cross reactivity analysis against patient allergies
- `calculate_dose`: Renal and weight based dose adjustment

**Final Answer Node**: Synthesizes retrieved evidence with patient context, generating a response calibrated to the physician's experience level.

### Geography Aware Guideline Retrieval

The core differentiator is geography filtered evidence retrieval. When a German physician queries treatment guidelines, the system:

1. Detects `doctor.country = "Germany"`
2. Configures Tavily search with German specific domains:
   - `awmf.org` (German guideline clearinghouse)
   - `escardio.org` (European Society of Cardiology)
   - `dgk.org` (German Cardiac Society)
   - `aerzteblatt.de` (German Medical Journal)
   - `ema.europa.eu` (European Medicines Agency)
3. Appends query context: "AWMF Leitlinie deutsche guidelines Germany EMA"
4. Returns ESC/AWMF guidelines instead of ACC/AHA guidelines

The same query from a USA physician returns FDA/ACC/AHA sources.

**Supported Regions**:
- USA: FDA, ACC, AHA, CDC, NIH, UpToDate
- Germany: AWMF, EMA, DGK, Aerzteblatt
- UK: NICE, BNF, NHS
- EU: ESC, EMA, EASL
- India: ICMR, CDSCO, API

### Experience Adaptive Response Generation

System prompts adapt based on `doctor.experience_level`:

**Student Mode**:
```
Provide detailed explanations with:
- Pathophysiology and mechanisms
- Step by step clinical reasoning
- Key learning points and pearls
- Common mistakes to avoid
```

**Attending Mode**:
```
Be:
- Concise and action oriented
- Focused on critical findings and immediate next steps
- Specific with recommendations
- Including relevant evidence when it changes management
```

This ensures a senior emergency physician receives a three sentence disposition recommendation, while a medical student receives comprehensive educational context.

### Critical Care Mode

For emergency situations, the system activates critical care mode:

1. Adds emergency medicine domains: `sccm.org`, `esicm.org`, `ccforum.biomedcentral.com`
2. Forces structured response format:
   - **Assessment**: Primary diagnosis with key finding
   - **Immediate Action**: Specific intervention with dose
   - **Monitor**: Parameter, target value, frequency
   - **Safety Alert**: Patient specific consideration
3. Prioritizes speed and actionability over comprehensiveness

---

## Technical Details

### Model Configuration

**Base Model**: `google/medgemma-4b-it` (4 billion parameter instruction tuned variant)

**Quantization**: 4 bit NormalFloat (NF4) via BitsAndBytes
- Reduces VRAM from ~16GB to ~4GB
- Enables inference on consumer GPUs (T4, RTX 3080)
- Minimal quality degradation for clinical reasoning tasks

**Inference Configuration**:
```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True
)
```

### Patient Context Integration

The system ingests structured EHR data:

```python
PatientEHR(
    name="Robert Johnson",
    age=67,
    sex="M",
    chief_complaint="Increasing SOB and leg swelling",
    allergies=["Penicillin (rash)", "Sulfa (anaphylaxis)"],
    current_medications=[
        Medication(name="Metformin", dose="1000mg BID"),
        Medication(name="Lisinopril", dose="20mg daily")
    ],
    recent_labs={
        "Creatinine": LabValue(value=1.4, unit="mg/dL", flag="H"),
        "eGFR": LabValue(value=52, unit="mL/min", flag="L"),
        "NT-proBNP": LabValue(value=450, unit="pg/mL", flag="H")
    }
)
```

This context is injected into MedGemma's prompt, enabling patient specific recommendations that account for renal function, current medications, and documented allergies.

### Allergy Safety System

Before any medication recommendation, the system checks for:

1. **Direct Matches**: "Penicillin" allergy blocks penicillin recommendation
2. **Cross Reactivity Families**:
   - Penicillin → amoxicillin, ampicillin, piperacillin
   - Sulfa → sulfamethoxazole, TMP SMX
   - Cephalosporin → cephalexin, ceftriaxone, cefazolin
   - NSAID → ibuprofen, naproxen, ketorolac

Conflicts generate prominent warnings in the response.

### Real Time Streaming

The FastAPI backend implements Server Sent Events (SSE) for token by token streaming:

1. Query arrives at `/ask/stream` endpoint
2. Background thread executes LangGraph workflow
3. ContextVar callback captures each generated token
4. Tokens pushed to async queue, yielded as SSE events
5. Frontend displays progressive response generation

This provides immediate feedback during the 10 to 30 second generation time.

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/doctors` | GET | List available physician personas |
| `/patients` | GET | List available patient cases |
| `/patient/{id}` | GET | Full patient EHR details |
| `/ask/stream` | POST | Streaming clinical query |
| `/doctors/create` | POST | Create custom physician |
| `/patients/create/ehr` | POST | Parse unstructured clinical notes |

### Deployment Considerations

**Kaggle Notebook**: Self contained execution with T4 GPU, Ngrok tunneling for external access

**Local Development**: Requires CUDA compatible GPU with 8GB+ VRAM

**Production**: Containerized deployment with GPU passthrough recommended

### Limitations and Future Work

1. **Language Support**: Currently optimized for English and German; expansion to additional languages planned
2. **Guideline Coverage**: Five regions supported; additional regulatory bodies (Japan PMDA, Australia TGA) in development
3. **Real Time Updates**: Guideline search reflects web indexed content; direct API integration with guideline publishers would improve currency
4. **Validation**: Clinical validation studies needed before deployment in actual patient care settings

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
- **Source Code**: https://github.com/sandybme/contextmed 


---

*Built for the MedGemma Impact Challenge 2026*
