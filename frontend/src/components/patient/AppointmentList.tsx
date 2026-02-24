'use client';

import { Clock, AlertTriangle, CheckCircle, User, ChevronRight } from 'lucide-react';
import { cn, getCountryFlag } from '@/lib/utils';
import { Avatar, Badge, PatientCardSkeleton } from '@/components/ui';
import type { PatientSummary, AppointmentStatus } from '@/types';

interface AppointmentListProps {
  patients: PatientSummary[];
  selectedPatientId: string | null;
  onSelectPatient: (patient: PatientSummary) => void;
  isLoading: boolean;
  appointmentStatuses: Record<string, AppointmentStatus>;
}

const statusConfig: Record<AppointmentStatus, { icon: typeof Clock; label: string; bgColor: string; textColor: string; dotColor: string }> = {
  waiting: {
    icon: Clock,
    label: 'Waiting',
    bgColor: 'bg-amber-50',
    textColor: 'text-amber-700',
    dotColor: 'bg-amber-400',
  },
  'in-progress': {
    icon: User,
    label: 'Active',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-700',
    dotColor: 'bg-blue-500',
  },
  completed: {
    icon: CheckCircle,
    label: 'Done',
    bgColor: 'bg-green-50',
    textColor: 'text-green-700',
    dotColor: 'bg-green-500',
  },
};

export function AppointmentList({
  patients,
  selectedPatientId,
  onSelectPatient,
  isLoading,
  appointmentStatuses,
}: AppointmentListProps) {
  if (isLoading) {
    return (
      <div className="p-2 space-y-2">
        {[1, 2, 3, 4].map((i) => (
          <PatientCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (patients.length === 0) {
    return (
      <div className="p-8 text-center">
        <User className="h-10 w-10 text-slate-300 mx-auto mb-3" />
        <p className="text-sm text-slate-500">No appointments scheduled</p>
      </div>
    );
  }

  return (
    <div className="p-2 space-y-1">
      {patients.map((patient) => {
        const status = appointmentStatuses[patient.id] || 'waiting';
        const statusInfo = statusConfig[status];
        const isSelected = selectedPatientId === patient.id;
        const isPriority =
          patient.chief_complaint.toLowerCase().includes('chest pain') ||
          patient.chief_complaint.toLowerCase().includes('dyspnea') ||
          patient.chief_complaint.toLowerCase().includes('shortness');

        return (
          <button
            key={patient.id}
            onClick={() => onSelectPatient(patient)}
            className={cn(
              'w-full p-3 text-left rounded-lg transition-all group',
              isSelected
                ? 'bg-blue-50 ring-1 ring-blue-200'
                : 'hover:bg-slate-50'
            )}
          >
            <div className="flex items-start gap-3">
              <div className="relative">
                <Avatar name={patient.name} size="md" />
                <div
                  className={cn(
                    'absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white',
                    statusInfo.dotColor
                  )}
                />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-0.5">
                  <p className="font-medium text-slate-900 truncate text-sm">{patient.name}</p>
                  <div className="flex items-center gap-1">
                    {isPriority && (
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
                    )}
                    <ChevronRight className={cn(
                      "h-4 w-4 text-slate-300 transition-transform",
                      isSelected && "text-blue-500 translate-x-0.5"
                    )} />
                  </div>
                </div>

                <p className="text-xs text-slate-500 line-clamp-2 mb-2 leading-relaxed">
                  {patient.chief_complaint}
                </p>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <Badge size="sm" variant="default">
                      {patient.age}y {patient.sex.charAt(0)}
                    </Badge>
                    <span className="text-xs text-slate-400">
                      {getCountryFlag(patient.country)}
                    </span>
                  </div>

                  <span className={cn(
                    'text-[10px] font-medium px-1.5 py-0.5 rounded',
                    statusInfo.bgColor,
                    statusInfo.textColor
                  )}>
                    {statusInfo.label}
                  </span>
                </div>
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}
