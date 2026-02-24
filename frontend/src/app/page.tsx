'use client';

import { useState } from 'react';
import { useContextMed } from '@/hooks/useContextMed';
import { AppointmentList, PatientDetail } from '@/components/patient';
import { ChatPanel } from '@/components/chat';
import { Avatar, Badge, Skeleton } from '@/components/ui';
import {
  Activity,
  ChevronDown,
  Users,
  X,
  Wifi,
  WifiOff,
  FileText,
  Stethoscope,
} from 'lucide-react';
import { cn, getCountryFlag, getExperienceLevelLabel } from '@/lib/utils';
import type { DoctorSummary } from '@/types';

export default function Home() {
  const {
    serverStatus,
    doctors,
    patients,
    isLoadingData,
    selectedDoctor,
    selectDoctor,
    selectedPatientId,
    selectedPatientEHR,
    selectPatient,
    deselectPatient,
    isLoadingPatient,
    messages,
    streamingState,
    sendMessage,
    appointmentStatuses,
    isReady,
  } = useContextMed();

  const [isPhysicianDropdownOpen, setIsPhysicianDropdownOpen] = useState(false);
  const [isEHRPanelOpen, setIsEHRPanelOpen] = useState(false);

  // Open EHR panel when patient is selected
  const handleSelectPatient = (patient: { id: string; name: string; chief_complaint: string; age: number; sex: string; country: string }) => {
    selectPatient(patient);
    setIsEHRPanelOpen(true);
  };

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      {/* Header */}
      <header className="h-14 bg-white border-b border-slate-200 px-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 shadow-md">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900">ContextMed</h1>
            <p className="text-[10px] text-slate-500 -mt-0.5">Globally Informed. Locally Accurate.</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {serverStatus === 'connected' ? (
            <div className="flex items-center gap-1.5 text-green-600 bg-green-50 px-2.5 py-1 rounded-full">
              <Wifi className="h-3.5 w-3.5" />
              <span className="text-xs font-medium">Connected</span>
            </div>
          ) : serverStatus === 'checking' ? (
            <div className="flex items-center gap-1.5 text-amber-600 bg-amber-50 px-2.5 py-1 rounded-full">
              <div className="h-3.5 w-3.5 border-2 border-amber-600 border-t-transparent rounded-full animate-spin" />
              <span className="text-xs font-medium">Connecting...</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-red-600 bg-red-50 px-2.5 py-1 rounded-full">
              <WifiOff className="h-3.5 w-3.5" />
              <span className="text-xs font-medium">Disconnected</span>
            </div>
          )}
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Physician & Appointments */}
        <aside className="w-72 bg-white border-r border-slate-200 flex flex-col flex-shrink-0">
          {/* Physician Dropdown */}
          <div className="p-3 border-b border-slate-100">
            <div className="relative">
              <button
                onClick={() => setIsPhysicianDropdownOpen(!isPhysicianDropdownOpen)}
                className="w-full flex items-center justify-between p-2.5 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <Stethoscope className="h-4 w-4 text-slate-500" />
                  {selectedDoctor ? (
                    <div className="text-left">
                      <p className="text-sm font-medium text-slate-900">{selectedDoctor.name}</p>
                      <p className="text-xs text-slate-500">{selectedDoctor.specialty}</p>
                    </div>
                  ) : (
                    <span className="text-sm text-slate-500">Select Physician</span>
                  )}
                </div>
                <ChevronDown className={cn(
                  "h-4 w-4 text-slate-400 transition-transform",
                  isPhysicianDropdownOpen && "rotate-180"
                )} />
              </button>

              {/* Dropdown Menu */}
              {isPhysicianDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
                  {isLoadingData ? (
                    <div className="p-3 space-y-2">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-12 w-full" />
                      ))}
                    </div>
                  ) : (
                    <PhysicianList
                      doctors={doctors}
                      selectedDoctor={selectedDoctor}
                      onSelect={(doctor) => {
                        selectDoctor(doctor);
                        setIsPhysicianDropdownOpen(false);
                      }}
                    />
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Appointments List */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="px-3 py-2.5 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-semibold text-slate-800">Appointments</span>
              </div>
              <Badge size="sm" variant="info">{patients.length}</Badge>
            </div>
            <div className="flex-1 overflow-y-auto">
              <AppointmentList
                patients={patients}
                selectedPatientId={selectedPatientId}
                onSelectPatient={handleSelectPatient}
                isLoading={isLoadingData}
                appointmentStatuses={appointmentStatuses}
              />
            </div>
          </div>
        </aside>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col overflow-hidden p-4">
          <ChatPanel
            messages={messages}
            streamingState={streamingState}
            onSendMessage={sendMessage}
            doctorName={selectedDoctor?.name}
            patientName={selectedPatientEHR?.name}
            isReady={isReady}
            onDeselectPatient={() => {
              deselectPatient();
              setIsEHRPanelOpen(false);
            }}
          />
        </main>

        {/* Right Panel - Patient EHR (Slide-in) */}
        <div
          className={cn(
            "fixed inset-y-0 right-0 w-[420px] bg-white border-l border-slate-200 shadow-2xl transform transition-transform duration-300 ease-in-out z-40",
            isEHRPanelOpen && selectedPatientEHR ? "translate-x-0" : "translate-x-full"
          )}
        >
          {/* EHR Panel Header */}
          <div className="h-14 px-4 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="font-semibold text-slate-900">Patient Record</span>
            </div>
            <button
              onClick={() => setIsEHRPanelOpen(false)}
              className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <X className="h-4 w-4 text-slate-500" />
            </button>
          </div>

          {/* EHR Content */}
          <div className="h-[calc(100vh-3.5rem)] overflow-y-auto">
            {isLoadingPatient ? (
              <div className="p-4 space-y-4">
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-32 w-full" />
              </div>
            ) : selectedPatientEHR ? (
              <PatientDetail patient={selectedPatientEHR} />
            ) : null}
          </div>
        </div>

        {/* Overlay when EHR panel is open */}
        {isEHRPanelOpen && selectedPatientEHR && (
          <div
            className="fixed inset-0 bg-black/20 z-30 lg:hidden"
            onClick={() => setIsEHRPanelOpen(false)}
          />
        )}
      </div>
    </div>
  );
}

// Physician List Component
function PhysicianList({
  doctors,
  selectedDoctor,
  onSelect,
}: {
  doctors: DoctorSummary[];
  selectedDoctor: DoctorSummary | null;
  onSelect: (doctor: DoctorSummary) => void;
}) {
  // Group by country
  const doctorsByCountry = doctors.reduce((acc, doctor) => {
    if (!acc[doctor.country]) {
      acc[doctor.country] = [];
    }
    acc[doctor.country].push(doctor);
    return acc;
  }, {} as Record<string, DoctorSummary[]>);

  return (
    <div className="py-1">
      {Object.entries(doctorsByCountry).map(([country, countryDoctors]) => (
        <div key={country}>
          <div className="px-3 py-1.5 flex items-center gap-1.5">
            <span className="text-sm">{getCountryFlag(country)}</span>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
              {country}
            </span>
          </div>
          {countryDoctors.map((doctor) => (
            <button
              key={doctor.id}
              onClick={() => onSelect(doctor)}
              className={cn(
                "w-full flex items-center gap-2.5 px-3 py-2 hover:bg-slate-50 transition-colors",
                selectedDoctor?.id === doctor.id && "bg-blue-50"
              )}
            >
              <Avatar name={doctor.name} size="sm" />
              <div className="flex-1 text-left">
                <p className="text-sm font-medium text-slate-900">{doctor.name}</p>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-slate-500">{doctor.specialty}</span>
                  <span className="text-slate-300">·</span>
                  <span className="text-[10px] text-slate-400">
                    {getExperienceLevelLabel(doctor.experience_level)}
                  </span>
                </div>
              </div>
              {selectedDoctor?.id === doctor.id && (
                <div className="h-2 w-2 rounded-full bg-blue-500" />
              )}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}
