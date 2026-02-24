'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  getDoctors,
  getPatients,
  getPatient,
  streamQuery,
  checkApiHealth,
} from '@/lib/api';
import { generateId } from '@/lib/utils';
import type {
  DoctorSummary,
  PatientSummary,
  PatientEHR,
  ChatMessage,
  StreamingState,
  ConversationMessage,
  QueryMode,
  AppointmentStatus,
} from '@/types';

export function useContextMed() {
  // Server state
  const [serverStatus, setServerStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  // Data state
  const [doctors, setDoctors] = useState<DoctorSummary[]>([]);
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Selection state
  const [selectedDoctor, setSelectedDoctor] = useState<DoctorSummary | null>(null);
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [selectedPatientEHR, setSelectedPatientEHR] = useState<PatientEHR | null>(null);
  const [isLoadingPatient, setIsLoadingPatient] = useState(false);

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isStreaming: false,
    status: 'idle',
    toolsUsed: [],
  });
  const abortControllerRef = useRef<AbortController | null>(null);

  // Appointment statuses (for demo)
  const [appointmentStatuses, setAppointmentStatuses] = useState<Record<string, AppointmentStatus>>({});

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      setServerStatus('checking');
      const isHealthy = await checkApiHealth();
      setServerStatus(isHealthy ? 'connected' : 'disconnected');
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  // Load doctors and patients (only once when connected)
  useEffect(() => {
    const loadData = async () => {
      if (serverStatus !== 'connected') return;
      // Don't reload if we already have data
      if (doctors.length > 0 && patients.length > 0) return;

      setIsLoadingData(true);
      try {
        const [doctorsData, patientsData] = await Promise.all([
          getDoctors(),
          getPatients(),
        ]);
        setDoctors(doctorsData);
        setPatients(patientsData);

        // Auto-select first doctor if none selected
        if (doctorsData.length > 0 && !selectedDoctor) {
          setSelectedDoctor(doctorsData[0]);
        }

        // Initialize appointment statuses only if not already set
        if (Object.keys(appointmentStatuses).length === 0) {
          const statuses: Record<string, AppointmentStatus> = {};
          patientsData.forEach((p) => {
            statuses[p.id] = 'waiting';
          });
          setAppointmentStatuses(statuses);
        }
      } catch (error) {
        console.error('Failed to load data:', error);
        setServerStatus('disconnected');
      } finally {
        setIsLoadingData(false);
      }
    };

    loadData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serverStatus]);

  // Load patient EHR when selected
  useEffect(() => {
    const loadPatientEHR = async () => {
      if (!selectedPatientId) {
        setSelectedPatientEHR(null);
        return;
      }

      setIsLoadingPatient(true);
      try {
        const ehr = await getPatient(selectedPatientId);
        setSelectedPatientEHR(ehr);
      } catch (error) {
        console.error('Failed to load patient:', error);
        setSelectedPatientEHR(null);
      } finally {
        setIsLoadingPatient(false);
      }
    };

    loadPatientEHR();
  }, [selectedPatientId]);

  // Select a doctor
  const selectDoctor = useCallback((doctor: DoctorSummary) => {
    setSelectedDoctor(doctor);
  }, []);

  // Select or deselect a patient
  const selectPatient = useCallback((patient: PatientSummary) => {
    // If clicking the same patient, deselect
    if (selectedPatientId === patient.id) {
      // Revert status to waiting (unless completed)
      setAppointmentStatuses((prev) => ({
        ...prev,
        [patient.id]: prev[patient.id] === 'completed' ? 'completed' : 'waiting',
      }));
      setSelectedPatientId(null);
      setSelectedPatientEHR(null);
      // Don't clear chat - keep generic conversation
      return;
    }

    // Deselect previous patient (revert to waiting if not completed)
    if (selectedPatientId) {
      setAppointmentStatuses((prev) => ({
        ...prev,
        [selectedPatientId]: prev[selectedPatientId] === 'completed' ? 'completed' : 'waiting',
      }));
    }

    // Select new patient
    setSelectedPatientId(patient.id);
    // Update status to in-progress
    setAppointmentStatuses((prev) => ({
      ...prev,
      [patient.id]: 'in-progress',
    }));
    // Clear chat when switching patients
    setMessages([]);
  }, [selectedPatientId]);

  // Send a message
  const sendMessage = useCallback(
    async (query: string, mode: QueryMode) => {
      if (!selectedDoctor || streamingState.isStreaming) return;

      // Cancel any existing stream
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();

      // Add user message
      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        content: query,
        timestamp: new Date(),
      };

      // Prepare assistant message placeholder
      const assistantMessageId = generateId();
      const assistantMessage: ChatMessage = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setStreamingState({
        isStreaming: true,
        status: 'searching',
        toolsUsed: [],
      });

      // Build conversation history
      const conversationHistory: ConversationMessage[] = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      try {
        await streamQuery(
          {
            query,
            doctor_id: selectedDoctor.id,
            patient_id: selectedPatientId || undefined,
            mode,
            conversation_history: conversationHistory,
          },
          {
            onStatus: (status) => {
              setStreamingState((prev) => ({
                ...prev,
                status: status === 'searching' ? 'searching' : 'generating',
              }));
            },
            onChunk: (chunk, fullText) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMessageId ? { ...m, content: fullText } : m
                )
              );
            },
            onComplete: (metadata) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMessageId
                    ? {
                        ...m,
                        isStreaming: false,
                        metadata: {
                          toolsUsed: metadata.toolsUsed,
                          mode: metadata.mode as QueryMode,
                        },
                      }
                    : m
                )
              );
              setStreamingState({
                isStreaming: false,
                status: 'complete',
                toolsUsed: metadata.toolsUsed,
              });
            },
            onError: (error) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMessageId
                    ? { ...m, content: `Error: ${error}`, isStreaming: false }
                    : m
                )
              );
              setStreamingState({
                isStreaming: false,
                status: 'error',
                toolsUsed: [],
                error,
              });
            },
          },
          abortControllerRef.current.signal
        );
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          setStreamingState({
            isStreaming: false,
            status: 'error',
            toolsUsed: [],
            error: error.message,
          });
        }
      }
    },
    [selectedDoctor, selectedPatientId, messages, streamingState.isStreaming]
  );

  // Clear chat
  const clearChat = useCallback(() => {
    setMessages([]);
    setStreamingState({
      isStreaming: false,
      status: 'idle',
      toolsUsed: [],
    });
  }, []);

  // Deselect patient (go to generic mode)
  const deselectPatient = useCallback(() => {
    if (selectedPatientId) {
      // Revert status to waiting (unless completed)
      setAppointmentStatuses((prev) => ({
        ...prev,
        [selectedPatientId]: prev[selectedPatientId] === 'completed' ? 'completed' : 'waiting',
      }));
    }
    setSelectedPatientId(null);
    setSelectedPatientEHR(null);
  }, [selectedPatientId]);

  // Mark appointment as completed
  const completeAppointment = useCallback((patientId: string) => {
    setAppointmentStatuses((prev) => ({
      ...prev,
      [patientId]: 'completed',
    }));
  }, []);

  // Filter patients by doctor's country
  const filteredPatients = selectedDoctor
    ? patients.filter((p) => p.country === selectedDoctor.country)
    : patients;

  return {
    // Server
    serverStatus,

    // Data
    doctors,
    patients: filteredPatients,
    isLoadingData,

    // Selection
    selectedDoctor,
    selectDoctor,
    selectedPatientId,
    selectedPatientEHR,
    selectPatient,
    deselectPatient,
    isLoadingPatient,

    // Chat
    messages,
    streamingState,
    sendMessage,
    clearChat,

    // Appointments
    appointmentStatuses,
    completeAppointment,

    // Computed
    isReady: !!selectedDoctor && serverStatus === 'connected',
  };
}
