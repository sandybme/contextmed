"use client";

import { Patient } from "@/lib/api";

// Simulated appointment times for the patient list
const APPOINTMENT_TIMES = [
  "08:30 AM",
  "09:15 AM",
  "10:00 AM",
  "10:45 AM",
  "11:30 AM",
  "01:00 PM",
  "01:45 PM",
  "02:30 PM",
];

export default function PatientSelector({
  patients,
  selected,
  onSelect,
}: {
  patients: Patient[];
  selected: string | null;
  onSelect: (id: string | null) => void;
}) {
  const today = new Date();
  const dateStr = today.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <label className="block text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">
          Appointments
        </label>
        <span className="text-[10px] text-[var(--text-secondary)]">
          {dateStr}
        </span>
      </div>

      <div className="space-y-1">
        {/* General query - no patient */}
        <button
          onClick={() => onSelect(null)}
          className={`w-full text-left px-3 py-2 rounded-lg border transition-all duration-150 text-sm ${
            selected === null
              ? "border-[var(--accent)] bg-[var(--accent)]/10"
              : "border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--text-secondary)]"
          }`}
        >
          <span className="text-[var(--text-secondary)]">No patient</span>
          <span className="text-[var(--text-secondary)] ml-1">&middot; general query</span>
        </button>

        {/* Appointment list */}
        {patients.map((pat, i) => {
          const time = APPOINTMENT_TIMES[i % APPOINTMENT_TIMES.length];
          const isActive = selected === pat.id;

          return (
            <button
              key={pat.id}
              onClick={() => onSelect(pat.id)}
              className={`w-full text-left rounded-lg border transition-all duration-150 ${
                isActive
                  ? "border-[var(--accent)] bg-[var(--accent)]/10"
                  : "border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--text-secondary)]"
              }`}
            >
              <div className="flex">
                {/* Time column */}
                <div className="flex-shrink-0 w-16 py-2.5 px-2 border-r border-[var(--border)] flex flex-col items-center justify-center">
                  <span className="text-[11px] font-medium text-[var(--text-secondary)]">
                    {time}
                  </span>
                </div>

                {/* Patient info */}
                <div className="flex-1 py-2.5 px-3 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium text-sm truncate">{pat.name}</span>
                    <span className="flex-shrink-0 text-[10px] text-[var(--text-secondary)]">
                      {pat.age}yo {pat.sex}
                    </span>
                  </div>
                  <div className="text-[11px] text-[var(--text-secondary)] mt-0.5 truncate">
                    {pat.chief_complaint}
                  </div>
                  {isActive && (
                    <div className="flex items-center gap-1 mt-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-[var(--success)]" />
                      <span className="text-[10px] text-[var(--success)]">EHR attached</span>
                    </div>
                  )}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
