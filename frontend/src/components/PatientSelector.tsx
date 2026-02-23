"use client";

import { Patient } from "@/lib/api";

export default function PatientSelector({
  patients,
  selected,
  onSelect,
}: {
  patients: Patient[];
  selected: string | null;
  onSelect: (id: string | null) => void;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider mb-2">
        Patient
      </label>
      <div className="space-y-1.5">
        <button
          onClick={() => onSelect(null)}
          className={`w-full text-left px-3 py-2 rounded-lg border transition-all duration-150 text-sm ${
            selected === null
              ? "border-[var(--accent)] bg-[var(--accent)]/10"
              : "border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--text-secondary)]"
          }`}
        >
          No patient (general query)
        </button>
        {patients.map((pat) => (
          <button
            key={pat.id}
            onClick={() => onSelect(pat.id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg border transition-all duration-150 ${
              selected === pat.id
                ? "border-[var(--accent)] bg-[var(--accent)]/10"
                : "border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--text-secondary)]"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-sm">{pat.name}</span>
              <span className="text-xs text-[var(--text-secondary)]">
                {pat.age}yo {pat.sex} · {pat.country}
              </span>
            </div>
            <div className="text-xs text-[var(--text-secondary)] mt-0.5 truncate">
              {pat.chief_complaint}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
