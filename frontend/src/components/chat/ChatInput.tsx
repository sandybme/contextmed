'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, AlertTriangle, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { QueryMode } from '@/types';

interface ChatInputProps {
  onSubmit: (query: string, mode: QueryMode) => void;
  isDisabled: boolean;
  isStreaming: boolean;
  placeholder?: string;
}

export function ChatInput({ onSubmit, isDisabled, isStreaming, placeholder }: ChatInputProps) {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<QueryMode>('regular');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, [query]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isDisabled) {
      onSubmit(query.trim(), mode);
      setQuery('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-slate-100 bg-slate-50/50">
      {/* Input Area */}
      <div className="flex gap-3 items-end">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder || "Ask a clinical question..."}
            disabled={isDisabled}
            rows={1}
            className={cn(
              'w-full resize-none rounded-xl border border-slate-200 px-4 py-3',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
              'disabled:bg-slate-100 disabled:text-slate-400 disabled:cursor-not-allowed',
              'placeholder:text-slate-400 text-slate-800',
              'transition-shadow'
            )}
          />
        </div>

        {/* Mode Toggle & Send */}
        <div className="flex items-center gap-2">
          {/* Mode Toggle */}
          <div className="flex rounded-lg border border-slate-200 bg-white overflow-hidden">
            <button
              type="button"
              onClick={() => setMode('regular')}
              className={cn(
                'flex items-center gap-1 px-2.5 py-2 text-xs font-medium transition-colors',
                mode === 'regular'
                  ? 'bg-blue-500 text-white'
                  : 'text-slate-600 hover:bg-slate-50'
              )}
              title="Regular mode - detailed clinical response"
            >
              <Zap className="h-3.5 w-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setMode('critical')}
              className={cn(
                'flex items-center gap-1 px-2.5 py-2 text-xs font-medium transition-colors',
                mode === 'critical'
                  ? 'bg-red-500 text-white'
                  : 'text-slate-600 hover:bg-slate-50'
              )}
              title="Critical mode - emergency 4-line format"
            >
              <AlertTriangle className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={!query.trim() || isDisabled}
            className={cn(
              'h-10 w-10 rounded-xl flex items-center justify-center transition-all',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              query.trim() && !isDisabled
                ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
                : 'bg-slate-200 text-slate-400'
            )}
          >
            {isStreaming ? (
              <div className="flex gap-0.5">
                <div className="h-1.5 w-1.5 rounded-full bg-white animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="h-1.5 w-1.5 rounded-full bg-white animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="h-1.5 w-1.5 rounded-full bg-white animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Helper Text */}
      <div className="flex items-center justify-between mt-2 px-1">
        <p className="text-[10px] text-slate-400">
          Press Enter to send · Shift+Enter for new line
        </p>
        {mode === 'critical' && (
          <p className="text-[10px] text-red-500 font-medium">
            Critical: Emergency 4-line format
          </p>
        )}
      </div>
    </form>
  );
}
