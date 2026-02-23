"use client";

import { useState } from "react";

interface QueryInputProps {
  onSubmit: (query: string, mode: string) => void;
  disabled: boolean;
  doctorSelected: boolean;
}

export default function QueryInput({
  onSubmit,
  disabled,
  doctorSelected,
}: QueryInputProps) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<"regular" | "critical">("regular");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || disabled || !doctorSelected) return;
    onSubmit(query.trim(), mode);
    setQuery("");
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-[var(--border)] p-4">
      <div className="flex items-center gap-2 mb-3">
        <button
          type="button"
          onClick={() => setMode("regular")}
          className={`text-xs px-3 py-1.5 rounded-full transition-all ${
            mode === "regular"
              ? "bg-[var(--accent)] text-white"
              : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
          }`}
        >
          Regular
        </button>
        <button
          type="button"
          onClick={() => setMode("critical")}
          className={`text-xs px-3 py-1.5 rounded-full transition-all ${
            mode === "critical"
              ? "bg-[var(--danger)] text-white"
              : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
          }`}
        >
          Critical Care
        </button>
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={
            doctorSelected
              ? "Ask a clinical question..."
              : "Select a physician first"
          }
          disabled={disabled || !doctorSelected}
          className="flex-1 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]/50 focus:outline-none focus:border-[var(--accent)] transition-colors disabled:opacity-40"
        />
        <button
          type="submit"
          disabled={disabled || !query.trim() || !doctorSelected}
          className="px-5 py-3 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-sm font-medium rounded-xl transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {disabled ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            </span>
          ) : (
            "Send"
          )}
        </button>
      </div>
    </form>
  );
}
