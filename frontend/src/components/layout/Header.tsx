'use client';

import { Activity, Settings, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui';

interface HeaderProps {
  serverStatus: 'connected' | 'disconnected' | 'checking';
}

export function Header({ serverStatus }: HeaderProps) {
  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center h-10 w-10 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 shadow-lg shadow-blue-500/20">
          <Activity className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">ContextMed</h1>
          <p className="text-xs text-gray-500">Globally Informed. Locally Accurate.</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div
            className={`h-2 w-2 rounded-full ${
              serverStatus === 'connected'
                ? 'bg-green-500'
                : serverStatus === 'checking'
                ? 'bg-amber-500 animate-pulse'
                : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-600">
            {serverStatus === 'connected'
              ? 'API Connected'
              : serverStatus === 'checking'
              ? 'Connecting...'
              : 'Disconnected'}
          </span>
        </div>

        <div className="h-6 w-px bg-gray-200" />

        <Button variant="ghost" size="sm">
          <HelpCircle className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="sm">
          <Settings className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
