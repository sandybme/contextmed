"""
FastAPI server for ContextMed.

Exposes the agent as a REST API with SSE streaming for real-time responses.
"""

from __future__ import annotations

import asyncio
import json
import queue
import threading
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from contextmed.agent import ContextMedAgent
from contextmed.models import (
    CreateDoctorRequest,
    CreatePatientFromEHRRequest,
    CreatePatientFromFormRequest,
    QueryRequest,
    QueryMode,
)


def create_app(agent: ContextMedAgent) -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="ContextMed API",
        description=(
            "Globally informed, locally accurate clinical AI. "
            "Context-aware agentic RAG powered by MedGemma."
        ),
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store agent on app state for access in endpoints
    app.state.agent = agent

    # ------------------------------------------------------------------
    # Info endpoints
    # ------------------------------------------------------------------

    @app.get("/")
    def root():
        return {
            "name": "ContextMed",
            "tagline": "Globally informed. Locally accurate.",
            "version": "2.0.0",
            "features": [
                "Geography-aware guidelines (FDA, EMA, AWMF, NICE, CDSCO)",
                "Experience-adaptive responses (student -> senior)",
                "LangGraph agentic workflow with ReAct reasoning",
                "Multi-turn conversation memory",
                "Real-time allergy and drug safety checks",
            ],
        }

    @app.get("/doctors")
    def get_doctors():
        return [
            {
                "id": doc_id,
                "name": doc.name,
                "specialty": doc.specialty,
                "experience_level": doc.experience_level.value,
                "country": doc.country,
            }
            for doc_id, doc in agent.doctors.items()
        ]

    @app.get("/patients")
    def get_patients():
        return [
            {
                "id": pat_id,
                "name": pat.name,
                "chief_complaint": pat.chief_complaint,
                "age": pat.age,
                "sex": pat.sex,
                "country": pat.country,
            }
            for pat_id, pat in agent.patients.items()
        ]

    @app.get("/patient/{patient_id}")
    def get_patient_details(patient_id: str):
        if patient_id in agent.patients:
            return agent.patients[patient_id].model_dump()
        return {"error": "Patient not found"}

    # ------------------------------------------------------------------
    # Dynamic creation
    # ------------------------------------------------------------------

    @app.post("/doctors/create")
    def create_doctor(req: CreateDoctorRequest):
        doctor = agent.create_doctor(
            name=req.name,
            specialty=req.specialty,
            experience_level=req.experience_level,
            country=req.country,
            workplace_type=req.workplace_type,
            workplace_name=req.workplace_name,
            language=req.language,
        )
        return {"success": True, "doctor_id": doctor.id, "doctor": doctor.model_dump()}

    @app.post("/patients/create/ehr")
    def create_patient_ehr(req: CreatePatientFromEHRRequest):
        patient = agent.create_patient_from_ehr(req.ehr_text, req.patient_id)
        return {"success": True, "patient_id": patient.patient_id, "patient": patient.model_dump()}

    @app.post("/patients/create/form")
    def create_patient_form(req: CreatePatientFromFormRequest):
        patient = agent.create_patient_from_form(
            name=req.name,
            age=req.age,
            sex=req.sex,
            chief_complaint=req.chief_complaint,
            allergies=req.allergies,
            medications=req.medications,
            medical_history=req.medical_history,
            hpi=req.hpi,
            weight_kg=req.weight_kg,
            height_cm=req.height_cm,
        )
        return {"success": True, "patient_id": patient.patient_id, "patient": patient.model_dump()}

    # ------------------------------------------------------------------
    # Streaming query endpoint
    # ------------------------------------------------------------------

    @app.post("/ask/stream")
    async def ask_stream(req: QueryRequest):
        """
        Stream clinical response with agentic RAG.

        Uses Server-Sent Events (SSE) for real-time token streaming.
        """
        if req.doctor_id not in agent.doctors:
            return {"error": f"Doctor not found: {req.doctor_id}"}

        agent.set_doctor(req.doctor_id)
        if req.patient_id:
            agent.set_patient(req.patient_id)
        else:
            agent._current_patient = None

        token_queue: queue.Queue = queue.Queue()

        def run_agent():
            try:
                token_queue.put(("status", "searching"))

                # Run the LangGraph pipeline in a thread
                from contextmed.agents.graph import AgentState

                patient_id = agent.patient.patient_id if agent.patient else ""
                conv_context = agent.memory.format_for_prompt(
                    agent.doctor.id, patient_id
                )

                # Build state
                state: AgentState = {
                    "query": req.query,
                    "doctor": agent.doctor.model_dump(),
                    "patient": agent.patient.model_dump() if agent.patient else None,
                    "mode": req.mode.value,
                    "conversation_context": conv_context,
                    "needs_drugs": False,
                    "needs_literature": False,
                    "needs_guidelines": False,
                    "search_terms": [],
                    "pubmed_results": [],
                    "openfda_results": [],
                    "guideline_results": [],
                    "allergy_alerts": [],
                    "final_response": "",
                    "citations": [],
                    "tools_used": [],
                    "medgemma": agent.medgemma,
                    "tavily_api_key": agent.settings.tavily_api_key,
                }

                token_queue.put(("status", "generating"))
                result = agent.graph.invoke(state)

                # Stream the response character by character
                for char in result["final_response"]:
                    token_queue.put(("token", char))

                # Store in memory
                agent.memory.add(agent.doctor.id, "user", req.query, patient_id)
                agent.memory.add(
                    agent.doctor.id,
                    "assistant",
                    result["final_response"][:500],
                    patient_id,
                )

                token_queue.put((
                    "done",
                    {
                        "doctor": agent.doctor.name,
                        "patient": agent.patient.name if agent.patient else None,
                        "tools_used": result.get("tools_used", []),
                        "mode": req.mode.value,
                    },
                ))

            except Exception as e:
                token_queue.put(("error", str(e)))

        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()

        async def generate():
            while True:
                try:
                    msg_type, content = token_queue.get(timeout=0.1)
                    if msg_type == "status":
                        yield f"data: {json.dumps({'status': content, 'done': False})}\n\n"
                    elif msg_type == "token":
                        yield f"data: {json.dumps({'chunk': content, 'done': False})}\n\n"
                    elif msg_type == "done":
                        yield f"data: {json.dumps({'done': True, **content})}\n\n"
                        break
                    elif msg_type == "error":
                        yield f"data: {json.dumps({'error': content, 'done': True})}\n\n"
                        break
                except queue.Empty:
                    yield ": keepalive\n\n"
                    await asyncio.sleep(0.05)

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return app
