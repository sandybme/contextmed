'use client';

import { useState } from 'react';
import {
  Users,
  Calendar,
  Stethoscope,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { cn, getCountryFlag, getExperienceLevelLabel } from '@/lib/utils';
import { Avatar, Badge } from '@/components/ui';
import type { DoctorSummary } from '@/types';

interface SidebarProps {
  doctors: DoctorSummary[];
  selectedDoctor: DoctorSummary | null;
  onSelectDoctor: (doctor: DoctorSummary) => void;
  isLoading: boolean;
}

export function Sidebar({ doctors, selectedDoctor, onSelectDoctor, isLoading }: SidebarProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  // Group doctors by country
  const doctorsByCountry = doctors.reduce((acc, doctor) => {
    const country = doctor.country;
    if (!acc[country]) {
      acc[country] = [];
    }
    acc[country].push(doctor);
    return acc;
  }, {} as Record<string, DoctorSummary[]>);

  return (
    <aside className="w-72 bg-white border-r border-gray-200 flex flex-col">
      {/* Active Physician */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center gap-2 text-sm font-medium text-gray-500 mb-3">
          <Stethoscope className="h-4 w-4" />
          <span>Active Physician</span>
        </div>
        {selectedDoctor ? (
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
            <Avatar name={selectedDoctor.name} size="md" />
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-900 truncate">{selectedDoctor.name}</p>
              <p className="text-xs text-gray-500 truncate">{selectedDoctor.specialty}</p>
              <div className="flex items-center gap-1 mt-1">
                <span className="text-xs">{getCountryFlag(selectedDoctor.country)}</span>
                <Badge size="sm">{getExperienceLevelLabel(selectedDoctor.experience_level)}</Badge>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 text-center">
            <p className="text-sm text-gray-500">Select a physician below</p>
          </div>
        )}
      </div>

      {/* Physician List */}
      <div className="flex-1 overflow-y-auto">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <Users className="h-4 w-4" />
            <span>Available Physicians</span>
          </div>
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-gray-400" />
          ) : (
            <ChevronRight className="h-4 w-4 text-gray-400" />
          )}
        </button>

        {isExpanded && (
          <div className="px-2 pb-4">
            {isLoading ? (
              <div className="space-y-2 p-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : (
              Object.entries(doctorsByCountry).map(([country, countryDoctors]) => (
                <div key={country} className="mb-3">
                  <div className="flex items-center gap-2 px-2 py-1">
                    <span className="text-sm">{getCountryFlag(country)}</span>
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                      {country}
                    </span>
                  </div>
                  <div className="space-y-1">
                    {countryDoctors.map((doctor) => (
                      <button
                        key={doctor.id}
                        onClick={() => onSelectDoctor(doctor)}
                        className={cn(
                          'w-full flex items-center gap-3 p-2 rounded-lg transition-colors text-left',
                          selectedDoctor?.id === doctor.id
                            ? 'bg-blue-50 border border-blue-200'
                            : 'hover:bg-gray-50'
                        )}
                      >
                        <Avatar name={doctor.name} size="sm" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {doctor.name}
                          </p>
                          <p className="text-xs text-gray-500 truncate">{doctor.specialty}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <Calendar className="h-3 w-3" />
          <span>Demo Mode - MedGemma Challenge</span>
        </div>
      </div>
    </aside>
  );
}
