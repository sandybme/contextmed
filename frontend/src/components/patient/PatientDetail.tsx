'use client';

import { useState } from 'react';
import {
  User,
  Heart,
  Pill,
  FileText,
  AlertTriangle,
  Activity,
  Beaker,
  ChevronDown,
  ChevronRight,
  Calendar,
  Scale,
  Ruler,
} from 'lucide-react';
import { cn, getLabFlagColor, formatDate } from '@/lib/utils';
import { Card, Badge } from '@/components/ui';
import type { PatientEHR } from '@/types';

interface PatientDetailProps {
  patient: PatientEHR;
}

interface SectionProps {
  title: string;
  icon: typeof User;
  children: React.ReactNode;
  defaultOpen?: boolean;
  badge?: React.ReactNode;
}

function Section({ title, icon: Icon, children, defaultOpen = false, badge }: SectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-gray-100 last:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-gray-500" />
          <span className="font-medium text-gray-700">{title}</span>
          {badge}
        </div>
        {isOpen ? (
          <ChevronDown className="h-4 w-4 text-gray-400" />
        ) : (
          <ChevronRight className="h-4 w-4 text-gray-400" />
        )}
      </button>
      {isOpen && <div className="px-3 pb-3">{children}</div>}
    </div>
  );
}

export function PatientDetail({ patient }: PatientDetailProps) {
  return (
    <div className="h-full overflow-y-auto">
      {/* Patient Header */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{patient.name}</h2>
            <p className="text-sm text-gray-600">ID: {patient.patient_id}</p>
          </div>
          <Badge variant="info" size="md">
            {patient.insurance}
          </Badge>
        </div>
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gray-400" />
            <span>{patient.age} years</span>
          </div>
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-gray-400" />
            <span>{patient.sex}</span>
          </div>
          <div className="flex items-center gap-2">
            <Scale className="h-4 w-4 text-gray-400" />
            <span>{patient.weight_kg} kg</span>
          </div>
          <div className="flex items-center gap-2">
            <Ruler className="h-4 w-4 text-gray-400" />
            <span>{patient.height_cm} cm</span>
          </div>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          BMI: <span className="font-medium">{patient.bmi.toFixed(1)}</span>
        </div>
      </div>

      {/* Chief Complaint */}
      <div className="p-4 bg-amber-50 border-b border-amber-100">
        <div className="flex items-start gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-amber-800">Chief Complaint</p>
            <p className="text-sm text-amber-700">{patient.chief_complaint}</p>
          </div>
        </div>
      </div>

      {/* Allergies */}
      {patient.allergies.length > 0 && (
        <div className="p-4 bg-red-50 border-b border-red-100">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-800">Allergies</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {patient.allergies.map((allergy, i) => (
                  <Badge key={i} variant="danger" size="sm">
                    {allergy}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Collapsible Sections */}
      <div>
        {/* HPI */}
        <Section title="History of Present Illness" icon={FileText} defaultOpen>
          <p className="text-sm text-gray-600 leading-relaxed">{patient.hpi}</p>
        </Section>

        {/* Vitals */}
        <Section title="Recent Vitals" icon={Activity} defaultOpen>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(patient.recent_vitals).map(([key, value]) => (
              <div key={key} className="p-2 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500 uppercase">{key}</p>
                <p className="font-medium text-gray-900">{value}</p>
              </div>
            ))}
          </div>
        </Section>

        {/* Labs */}
        <Section
          title="Recent Labs"
          icon={Beaker}
          badge={
            <Badge size="sm" variant="info">
              {Object.keys(patient.recent_labs).length}
            </Badge>
          }
        >
          <div className="space-y-2">
            {Object.entries(patient.recent_labs).map(([name, lab]) => (
              <div
                key={name}
                className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900">{name}</p>
                  <p className="text-xs text-gray-500">Ref: {lab.reference}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">
                    {lab.value} {lab.unit}
                  </p>
                  <span
                    className={cn(
                      'text-xs font-medium px-2 py-0.5 rounded',
                      getLabFlagColor(lab.flag)
                    )}
                  >
                    {lab.flag === 'N' ? 'Normal' : lab.flag === 'H' ? 'High' : 'Low'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Section>

        {/* Medications */}
        <Section
          title="Current Medications"
          icon={Pill}
          badge={
            <Badge size="sm" variant="info">
              {patient.current_medications.length}
            </Badge>
          }
        >
          <div className="space-y-2">
            {patient.current_medications.map((med, i) => (
              <div key={i} className="p-2 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <p className="font-medium text-gray-900">{med.name}</p>
                  <Badge size="sm">{med.indication}</Badge>
                </div>
                <p className="text-sm text-gray-600">
                  {med.dose} - {med.frequency}
                </p>
              </div>
            ))}
          </div>
        </Section>

        {/* Medical History */}
        <Section
          title="Medical History"
          icon={Heart}
          badge={
            <Badge size="sm" variant="info">
              {patient.medical_history.length}
            </Badge>
          }
        >
          <div className="space-y-2">
            {patient.medical_history.map((condition, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{condition.condition}</p>
                  {condition.diagnosed_year > 0 && (
                    <p className="text-xs text-gray-500">Diagnosed {condition.diagnosed_year}</p>
                  )}
                </div>
                <Badge
                  size="sm"
                  variant={condition.status === 'active' ? 'warning' : 'success'}
                >
                  {condition.status}
                </Badge>
              </div>
            ))}
          </div>
        </Section>

        {/* Imaging */}
        {patient.recent_imaging.length > 0 && (
          <Section title="Recent Imaging" icon={FileText}>
            <div className="space-y-2">
              {patient.recent_imaging.map((img, i) => (
                <div key={i} className="p-2 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <p className="font-medium text-gray-900">{img.type}</p>
                    <span className="text-xs text-gray-500">{formatDate(img.date)}</span>
                  </div>
                  <p className="text-sm text-gray-600">{img.findings}</p>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Social History */}
        {Object.keys(patient.social_history).length > 0 && (
          <Section title="Social History" icon={User}>
            <div className="space-y-2">
              {Object.entries(patient.social_history).map(([key, value]) => (
                <div key={key} className="p-2 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase">{key}</p>
                  <p className="text-sm text-gray-900">{value}</p>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Family History */}
        {patient.family_history.length > 0 && (
          <Section title="Family History" icon={User}>
            <ul className="space-y-1">
              {patient.family_history.map((item, i) => (
                <li key={i} className="text-sm text-gray-600 flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-gray-400" />
                  {item}
                </li>
              ))}
            </ul>
          </Section>
        )}
      </div>
    </div>
  );
}
