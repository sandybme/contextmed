import type {
  DoctorSummary,
  PatientSummary,
  PatientEHR,
  QueryRequest,
  ServerInfo,
  CreateDoctorRequest,
  CreateDoctorResponse,
  CreatePatientFromFormRequest,
  CreatePatientResponse,
} from '@/types';

// API base URL - configurable via environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// Fetch Helpers
// ============================================================================

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `HTTP ${response.status}`);
  }

  return response.json();
}

// ============================================================================
// Server Info
// ============================================================================

export async function getServerInfo(): Promise<ServerInfo> {
  return fetchJSON<ServerInfo>('/');
}

// ============================================================================
// Doctors API
// ============================================================================

export async function getDoctors(): Promise<DoctorSummary[]> {
  return fetchJSON<DoctorSummary[]>('/doctors');
}

export async function createDoctor(data: CreateDoctorRequest): Promise<CreateDoctorResponse> {
  return fetchJSON<CreateDoctorResponse>('/doctors/create', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ============================================================================
// Patients API
// ============================================================================

export async function getPatients(): Promise<PatientSummary[]> {
  return fetchJSON<PatientSummary[]>('/patients');
}

export async function getPatient(patientId: string): Promise<PatientEHR> {
  return fetchJSON<PatientEHR>(`/patient/${patientId}`);
}

export async function createPatientFromForm(
  data: CreatePatientFromFormRequest
): Promise<CreatePatientResponse> {
  return fetchJSON<CreatePatientResponse>('/patients/create/form', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ============================================================================
// Streaming Query API
// ============================================================================

export interface StreamCallbacks {
  onStatus?: (status: 'searching' | 'generating') => void;
  onChunk?: (chunk: string, fullText: string) => void;
  onComplete?: (metadata: { doctor: string; patient: string | null; toolsUsed: string[]; mode: string }) => void;
  onError?: (error: string) => void;
}

export async function streamQuery(
  request: QueryRequest,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const url = `${API_BASE_URL}/ask/stream`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
      },
      body: JSON.stringify(request),
      signal,
    });

    if (!response.ok) {
      const error = await response.text();
      callbacks.onError?.(error || `HTTP ${response.status}`);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      callbacks.onError?.('No response body');
      return;
    }

    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        // Process any remaining buffer
        if (buffer.trim()) {
          processSSELine(buffer, fullText, callbacks, (text) => { fullText = text; });
        }
        break;
      }

      // Decode the chunk and add to buffer
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      // Process complete lines (SSE messages end with \n\n or \n)
      let newlineIndex;
      while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
        const line = buffer.substring(0, newlineIndex);
        buffer = buffer.substring(newlineIndex + 1);

        if (line.trim()) {
          const result = processSSELine(line, fullText, callbacks, (text) => { fullText = text; });
          if (result === 'done' || result === 'error') {
            reader.releaseLock();
            return;
          }
        }
      }
    }

    reader.releaseLock();
  } catch (error) {
    if (error instanceof Error && error.name !== 'AbortError') {
      callbacks.onError?.(error.message);
    }
  }
}

function processSSELine(
  line: string,
  fullText: string,
  callbacks: StreamCallbacks,
  setFullText: (text: string) => void
): 'continue' | 'done' | 'error' {
  // Skip empty lines and comments
  if (!line.trim() || line.startsWith(':')) {
    return 'continue';
  }

  // Handle SSE data lines
  if (line.startsWith('data:')) {
    const jsonStr = line.substring(5).trim();
    if (!jsonStr) return 'continue';

    try {
      const data = JSON.parse(jsonStr);

      // Handle status updates
      if (data.status && !data.done) {
        callbacks.onStatus?.(data.status);
        return 'continue';
      }

      // Handle streaming chunks (skip empty chunks to avoid unnecessary re-renders)
      if (data.chunk !== undefined && !data.done) {
        if (data.chunk) {
          const newFullText = fullText + data.chunk;
          setFullText(newFullText);
          callbacks.onChunk?.(data.chunk, newFullText);
        }
        return 'continue';
      }

      // Handle errors
      if (data.error) {
        callbacks.onError?.(data.error);
        return 'error';
      }

      // Handle completion
      if (data.done === true) {
        callbacks.onComplete?.({
          doctor: data.doctor || '',
          patient: data.patient || null,
          toolsUsed: data.tools_used || [],
          mode: data.mode || 'regular',
        });
        return 'done';
      }
    } catch {
      // Skip malformed JSON
      console.warn('Failed to parse SSE data:', jsonStr);
    }
  }

  return 'continue';
}

// ============================================================================
// API Health Check
// ============================================================================

export async function checkApiHealth(): Promise<boolean> {
  try {
    await getServerInfo();
    return true;
  } catch {
    return false;
  }
}
