const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Doctor {
  id: string;
  name: string;
  specialty: string;
  experience_level: string;
  country: string;
}

export interface Patient {
  id: string;
  name: string;
  chief_complaint: string;
  age: number;
  sex: string;
  country: string;
}

export interface StreamEvent {
  status?: string;
  chunk?: string;
  done?: boolean;
  error?: string;
  doctor?: string;
  patient?: string;
  tools_used?: string[];
  mode?: string;
}

export async function fetchDoctors(): Promise<Doctor[]> {
  const res = await fetch(`${API_BASE}/doctors`);
  return res.json();
}

export async function fetchPatients(): Promise<Patient[]> {
  const res = await fetch(`${API_BASE}/patients`);
  return res.json();
}

export async function fetchPatientDetails(id: string) {
  const res = await fetch(`${API_BASE}/patient/${id}`);
  return res.json();
}

export async function* streamQuery(
  query: string,
  doctorId: string,
  patientId: string | null,
  mode: string = "regular",
): AsyncGenerator<StreamEvent> {
  const res = await fetch(`${API_BASE}/ask/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      doctor_id: doctorId,
      patient_id: patientId,
      mode,
    }),
  });

  const reader = res.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const event: StreamEvent = JSON.parse(line.slice(6));
          yield event;
          if (event.done || event.error) return;
        } catch {}
      }
    }
  }
}
