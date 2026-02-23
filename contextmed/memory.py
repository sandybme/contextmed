"""
Conversation memory for ContextMed.

Provides short-term (per-session) memory for multi-turn conversations
and a simple persistent memory store for cross-session context.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from contextmed.models import ConversationMessage


@dataclass
class ConversationMemory:
    """
    Per-session conversation memory.

    Tracks the full conversation history per doctor-patient pair,
    enabling multi-turn reasoning with context.
    """

    # Key: (doctor_id, patient_id) -> List of messages
    _store: Dict[str, List[ConversationMessage]] = field(
        default_factory=lambda: defaultdict(list)
    )
    max_turns: int = 20

    def _key(self, doctor_id: str, patient_id: str = "") -> str:
        return f"{doctor_id}::{patient_id}"

    def add(
        self,
        doctor_id: str,
        role: str,
        content: str,
        patient_id: str = "",
    ) -> None:
        """Add a message to the conversation."""
        key = self._key(doctor_id, patient_id)
        self._store[key].append(ConversationMessage(role=role, content=content))
        # Trim to keep only recent history
        if len(self._store[key]) > self.max_turns * 2:
            self._store[key] = self._store[key][-self.max_turns * 2 :]

    def get_history(
        self,
        doctor_id: str,
        patient_id: str = "",
        last_n: int = 6,
    ) -> List[ConversationMessage]:
        """Retrieve recent conversation history."""
        key = self._key(doctor_id, patient_id)
        return self._store[key][-last_n:]

    def clear(self, doctor_id: str, patient_id: str = "") -> None:
        """Clear conversation history for a doctor-patient pair."""
        key = self._key(doctor_id, patient_id)
        self._store[key] = []

    def format_for_prompt(
        self,
        doctor_id: str,
        patient_id: str = "",
        last_n: int = 6,
    ) -> str:
        """Format conversation history as text for inclusion in prompts."""
        history = self.get_history(doctor_id, patient_id, last_n)
        if not history:
            return ""

        lines = ["PREVIOUS CONVERSATION:"]
        for msg in history:
            role = "Doctor" if msg.role == "user" else "Assistant"
            lines.append(f"{role}: {msg.content[:300]}")
        return "\n".join(lines)


@dataclass
class ClinicalNotepad:
    """
    Persistent memory for clinical reasoning across sessions.

    Stores key clinical decisions, flagged concerns, and reasoning
    checkpoints that the agent can reference in future interactions.
    """

    _notes: Dict[str, List[Dict[str, Any]]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_note(
        self,
        patient_id: str,
        category: str,
        content: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Add a clinical note for a patient."""
        self._notes[patient_id].append({
            "category": category,
            "content": content,
            "metadata": metadata or {},
        })

    def get_notes(
        self,
        patient_id: str,
        category: Optional[str] = None,
    ) -> List[Dict]:
        """Retrieve notes for a patient, optionally filtered by category."""
        notes = self._notes.get(patient_id, [])
        if category:
            return [n for n in notes if n["category"] == category]
        return notes

    def format_for_prompt(self, patient_id: str) -> str:
        """Format patient notes for inclusion in prompts."""
        notes = self.get_notes(patient_id)
        if not notes:
            return ""

        lines = ["CLINICAL NOTEPAD:"]
        for note in notes[-5:]:
            lines.append(f"  [{note['category']}] {note['content'][:200]}")
        return "\n".join(lines)
