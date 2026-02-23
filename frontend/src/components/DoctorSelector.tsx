"use client";

import { Doctor } from "@/lib/api";

const FLAG: Record<string, string> = {
  USA: "US",
  Germany: "DE",
  India: "IN",
  UK: "GB",
};

const EXP_LABEL: Record<string, string> = {
  student: "Student",
  resident: "Resident",
  attending: "Attending",
  senior: "Senior",
};

export default function DoctorSelector({
  doctors,
  selected,
  onSelect,
}: {
  doctors: Doctor[];
  selected: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider mb-2">
        Physician
      </label>
      <div className="space-y-1.5">
        {doctors.map((doc) => (
          <button
            key={doc.id}
            onClick={() => onSelect(doc.id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg border transition-all duration-150 ${
              selected === doc.id
                ? "border-[var(--accent)] bg-[var(--accent)]/10"
                : "border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--text-secondary)]"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-sm">{doc.name}</span>
              <span className="text-xs text-[var(--text-secondary)]">
                {FLAG[doc.country] || doc.country}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs text-[var(--text-secondary)]">
                {doc.specialty}
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[var(--bg-tertiary)] text-[var(--text-secondary)]">
                {EXP_LABEL[doc.experience_level] || doc.experience_level}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
