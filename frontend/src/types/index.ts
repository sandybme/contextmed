// ContextMed TypeScript Types - Matching Backend Pydantic Models

// ============================================================================
// Enums
// ============================================================================

export type ExperienceLevel = 'student' | 'resident' | 'attending' | 'senior';
export type QueryMode = 'regular' | 'critical';
export type LabFlag = 'N' | 'H' | 'L';

// ============================================================================
// Doctor Models
// ============================================================================

export interface DoctorContext {
  id: string;
  name: string;
  specialty: string;
  experience_level: ExperienceLevel;
  country: string;
  workplace_type: string;
  workplace_name: string;
  language: string;
  preferences: Record<string, unknown>;
}

export interface DoctorSummary {
  id: string;
  name: string;
  specialty: string;
  experience_level: ExperienceLevel;
  country: string;
}

export interface CreateDoctorRequest {
  name: string;
  specialty: string;
  experience_level: ExperienceLevel;
  country?: string;
  workplace_type?: string;
  workplace_name?: string;
  language?: string;
}

// ============================================================================
// Patient Models
// ============================================================================

export interface LabResult {
  value: number | string;
  unit: string;
  reference: string;
  flag: LabFlag;
}

export interface Medication {
  name: string;
  dose: string;
  frequency: string;
  indication: string;
}

export interface MedicalCondition {
  condition: string;
  diagnosed_year: number;
  status: string;
}

export interface ImagingResult {
  type: string;
  date: string;
  findings: string;
}

export interface PatientEHR {
  patient_id: string;
  name: string;
  age: number;
  sex: string;
  weight_kg: number;
  height_cm: number;
  bmi: number;
  country: string;
  insurance: string;
  allergies: string[];
  current_medications: Medication[];
  medical_history: MedicalCondition[];
  surgical_history: string[];
  family_history: string[];
  social_history: Record<string, string>;
  recent_labs: Record<string, LabResult>;
  recent_vitals: Record<string, string>;
  recent_imaging: ImagingResult[];
  chief_complaint: string;
  hpi: string;
  ros: Record<string, string[]>;
}

export interface PatientSummary {
  id: string;
  name: string;
  chief_complaint: string;
  age: number;
  sex: string;
  country: string;
}

export interface CreatePatientFromEHRRequest {
  ehr_text: string;
  patient_id?: string;
}

export interface CreatePatientFromFormRequest {
  name: string;
  age: number;
  sex: string;
  chief_complaint: string;
  allergies?: string[];
  medications?: Array<Record<string, string>>;
  medical_history?: string[];
  hpi?: string;
  weight_kg?: number;
  height_cm?: number;
  labs?: Record<string, unknown>;
  vitals?: Record<string, string>;
}

// ============================================================================
// Query Models
// ============================================================================

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface QueryRequest {
  query: string;
  doctor_id: string;
  patient_id?: string;
  mode?: QueryMode;
  conversation_history?: ConversationMessage[];
}

// ============================================================================
// SSE Streaming Models
// ============================================================================

export interface SSEStatusMessage {
  status: 'searching' | 'generating';
  done: false;
}

export interface SSEChunkMessage {
  chunk: string;
  done: false;
}

export interface SSEDoneMessage {
  done: true;
  doctor: string;
  patient: string | null;
  tools_used: string[];
  mode: QueryMode;
}

export interface SSEErrorMessage {
  error: string;
  done: true;
}

export type SSEMessage = SSEStatusMessage | SSEChunkMessage | SSEDoneMessage | SSEErrorMessage;

// ============================================================================
// API Response Models
// ============================================================================

export interface ServerInfo {
  name: string;
  tagline: string;
  version: string;
  features: string[];
}

export interface CreateDoctorResponse {
  success: boolean;
  doctor_id: string;
  doctor: DoctorContext;
}

export interface CreatePatientResponse {
  success: boolean;
  patient_id: string;
  patient: PatientEHR;
}

// ============================================================================
// UI State Models
// ============================================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  metadata?: {
    toolsUsed?: string[];
    mode?: QueryMode;
  };
}

export interface StreamingState {
  isStreaming: boolean;
  status: 'idle' | 'searching' | 'generating' | 'complete' | 'error';
  toolsUsed: string[];
  error?: string;
}

export type AppointmentStatus = 'waiting' | 'in-progress' | 'completed';

export interface Appointment {
  patient: PatientSummary;
  status: AppointmentStatus;
  scheduledTime?: string;
}
