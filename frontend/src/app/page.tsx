"use client";

import { useEffect, useRef, useState } from "react";
import {
  Doctor,
  Patient,
  StreamEvent,
  fetchDoctors,
  fetchPatients,
  streamQuery,
} from "@/lib/api";
import DoctorSelector from "@/components/DoctorSelector";
import PatientSelector from "@/components/PatientSelector";
import ChatMessage from "@/components/ChatMessage";
import QueryInput from "@/components/QueryInput";

interface Message {
  role: "user" | "assistant";
  content: string;
  metadata?: {
    doctor?: string;
    tools_used?: string[];
    mode?: string;
  };
}

export default function Home() {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState<string | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [status, setStatus] = useState<string>("");
  const [connected, setConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function load() {
      try {
        const [docs, pats] = await Promise.all([
          fetchDoctors(),
          fetchPatients(),
        ]);
        setDoctors(docs);
        setPatients(pats);
        setConnected(true);
      } catch {
        setConnected(false);
      }
    }
    load();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (query: string, mode: string) => {
    if (!selectedDoctor || isStreaming) return;

    const userMsg: Message = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);
    setStatus("Connecting...");

    const assistantMsg: Message = {
      role: "assistant",
      content: "",
      metadata: { mode },
    };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      for await (const event of streamQuery(
        query,
        selectedDoctor,
        selectedPatient,
        mode,
      )) {
        if (event.status) {
          const labels: Record<string, string> = {
            processing: "Analysing query...",
            searching: "Searching evidence...",
            generating: "Generating response...",
          };
          setStatus(labels[event.status] || event.status);
        }

        if (event.chunk) {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.content += event.chunk;
            }
            return updated;
          });
          setStatus("");
        }

        if (event.done) {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.metadata = {
                doctor: event.doctor,
                tools_used: event.tools_used,
                mode: event.mode,
              };
            }
            return updated;
          });
        }

        if (event.error) {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.content = `Error: ${event.error}`;
            }
            return updated;
          });
        }
      }
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last.role === "assistant") {
          last.content = `Connection error. Is the backend running?`;
        }
        return updated;
      });
    }

    setIsStreaming(false);
    setStatus("");
  };

  const selectedDoctorObj = doctors.find((d) => d.id === selectedDoctor);
  const selectedPatientObj = patients.find((p) => p.id === selectedPatient);

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <aside className="w-80 bg-[var(--bg-secondary)] border-r border-[var(--border)] flex flex-col">
        {/* Logo */}
        <div className="p-5 border-b border-[var(--border)]">
          <h1 className="text-lg font-bold tracking-tight">
            Context<span className="text-[var(--accent)]">Med</span>
          </h1>
          <p className="text-[11px] text-[var(--text-secondary)] mt-0.5">
            Globally informed. Locally accurate.
          </p>
          <div className="flex items-center gap-1.5 mt-2">
            <div
              className={`w-1.5 h-1.5 rounded-full ${
                connected ? "bg-[var(--success)]" : "bg-[var(--danger)]"
              }`}
            />
            <span className="text-[10px] text-[var(--text-secondary)]">
              {connected ? "Backend connected" : "Backend offline"}
            </span>
          </div>
        </div>

        {/* Selectors */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          <DoctorSelector
            doctors={doctors}
            selected={selectedDoctor}
            onSelect={setSelectedDoctor}
          />
          <PatientSelector
            patients={patients}
            selected={selectedPatient}
            onSelect={setSelectedPatient}
          />
        </div>

        {/* Context summary */}
        {selectedDoctorObj && (
          <div className="p-4 border-t border-[var(--border)] bg-[var(--bg-tertiary)]">
            <div className="text-[10px] uppercase tracking-wider text-[var(--text-secondary)] mb-1.5">
              Active Context
            </div>
            <div className="text-xs space-y-0.5">
              <div>
                <span className="text-[var(--text-secondary)]">Physician:</span>{" "}
                {selectedDoctorObj.name}
              </div>
              <div>
                <span className="text-[var(--text-secondary)]">Guidelines:</span>{" "}
                {selectedDoctorObj.country === "USA"
                  ? "FDA / ACC / AHA"
                  : selectedDoctorObj.country === "Germany"
                    ? "EMA / ESC / AWMF"
                    : selectedDoctorObj.country}
              </div>
              {selectedPatientObj && (
                <div>
                  <span className="text-[var(--text-secondary)]">Patient:</span>{" "}
                  {selectedPatientObj.name} ({selectedPatientObj.age}yo)
                </div>
              )}
            </div>
          </div>
        )}
      </aside>

      {/* Main chat area */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-14 border-b border-[var(--border)] flex items-center px-6">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold">Clinical Copilot</h2>
            {status && (
              <div className="flex items-center gap-2">
                <svg
                  className="animate-spin h-3.5 w-3.5 text-[var(--accent)]"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                <span className="text-xs text-[var(--text-secondary)]">
                  {status}
                </span>
              </div>
            )}
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="text-4xl mb-4 opacity-20">+</div>
              <h3 className="text-lg font-semibold mb-1">
                Context<span className="text-[var(--accent)]">Med</span>
              </h3>
              <p className="text-sm text-[var(--text-secondary)] max-w-md">
                Select a physician and patient from the sidebar, then ask a
                clinical question. Responses are tailored to geography,
                specialty, and experience level.
              </p>
              <div className="flex gap-2 mt-6 flex-wrap justify-center">
                {[
                  "What is the management plan?",
                  "Check drug interactions",
                  "Differential diagnosis",
                ].map((q) => (
                  <button
                    key={q}
                    onClick={() => {
                      if (selectedDoctor) handleSubmit(q, "regular");
                    }}
                    className="text-xs px-3 py-1.5 rounded-full border border-[var(--border)] text-[var(--text-secondary)] hover:border-[var(--accent)] hover:text-[var(--accent)] transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage
              key={i}
              role={msg.role}
              content={msg.content}
              isStreaming={
                isStreaming &&
                i === messages.length - 1 &&
                msg.role === "assistant"
              }
              metadata={msg.metadata}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <QueryInput
          onSubmit={handleSubmit}
          disabled={isStreaming}
          doctorSelected={!!selectedDoctor}
        />
      </main>
    </div>
  );
}
