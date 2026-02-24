'use client';

import { cn } from '@/lib/utils';
import { Loader2, Search, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

type Status = 'idle' | 'searching' | 'generating' | 'complete' | 'error';

interface StatusIndicatorProps {
  status: Status;
  className?: string;
  showLabel?: boolean;
}

const statusConfig: Record<Status, { icon: typeof Loader2; label: string; color: string }> = {
  idle: {
    icon: CheckCircle2,
    label: 'Ready',
    color: 'text-gray-400',
  },
  searching: {
    icon: Search,
    label: 'Searching medical databases...',
    color: 'text-blue-500',
  },
  generating: {
    icon: Sparkles,
    label: 'Generating clinical response...',
    color: 'text-purple-500',
  },
  complete: {
    icon: CheckCircle2,
    label: 'Complete',
    color: 'text-green-500',
  },
  error: {
    icon: AlertCircle,
    label: 'Error occurred',
    color: 'text-red-500',
  },
};

export function StatusIndicator({ status, className, showLabel = true }: StatusIndicatorProps) {
  const config = statusConfig[status];
  const Icon = config.icon;
  const isAnimating = status === 'searching' || status === 'generating';

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Icon
        className={cn(
          'h-4 w-4',
          config.color,
          isAnimating && 'animate-pulse'
        )}
      />
      {showLabel && (
        <span className={cn('text-sm', config.color)}>{config.label}</span>
      )}
    </div>
  );
}

export function StreamingDots({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center gap-1', className)}>
      <div className="h-2 w-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="h-2 w-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="h-2 w-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
  );
}
