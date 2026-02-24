  'use client';

import { useRef, useEffect } from 'react';
import { MessageSquare, AlertCircle, Sparkles, Search, BookOpen, Pill, Shield, User, Brain } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { cn } from '@/lib/utils';
import type { ChatMessage as ChatMessageType, StreamingState, QueryMode } from '@/types';

interface ChatPanelProps {
  messages: ChatMessageType[];
  streamingState: StreamingState;
  onSendMessage: (query: string, mode: QueryMode) => void;
  doctorName?: string;
  patientName?: string;
  isReady: boolean;
  onDeselectPatient?: () => void;
}

export function ChatPanel({
  messages,
  streamingState,
  onSendMessage,
  doctorName,
  patientName,
  isReady,
  onDeselectPatient,
}: ChatPanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new messages or streaming updates
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages, messages[messages.length - 1]?.content]);

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
        <div className="flex items-center gap-3">
          <div className={cn(
            "h-10 w-10 rounded-xl flex items-center justify-center shadow-sm",
            patientName
              ? "bg-gradient-to-br from-blue-500 to-indigo-600"
              : "bg-gradient-to-br from-slate-400 to-slate-500"
          )}>
            {patientName ? (
              <User className="h-5 w-5 text-white" />
            ) : (
              <Brain className="h-5 w-5 text-white" />
            )}
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">Clinical Assistant</h3>
            <p className="text-xs text-slate-500">
              {patientName ? (
                <span className="flex items-center gap-1.5">
                  <span className="inline-block h-2 w-2 rounded-full bg-blue-500"></span>
                  <span>EHR Context: <span className="font-medium text-slate-700">{patientName}</span></span>
                  {onDeselectPatient && (
                    <button
                      onClick={onDeselectPatient}
                      className="ml-1 text-slate-400 hover:text-slate-600 underline"
                    >
                      (switch to generic)
                    </button>
                  )}
                </span>
              ) : (
                <span className="flex items-center gap-1.5">
                  <span className="inline-block h-2 w-2 rounded-full bg-slate-400"></span>
                  <span>Generic Mode - No patient selected</span>
                </span>
              )}
            </p>
          </div>
        </div>

        {/* Status Indicator */}
        <StreamingStatus status={streamingState.status} />
      </div>

      {/* Messages Area */}
      <div ref={messagesContainerRef} className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <EmptyState isReady={isReady} onSendMessage={onSendMessage} patientName={patientName} />
        ) : (
          <div className="divide-y divide-slate-50">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                doctorName={doctorName}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error Display */}
      {streamingState.error && (
        <div className="px-4 py-3 bg-red-50 border-t border-red-100">
          <div className="flex items-center gap-2 text-red-700">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span className="text-sm">{streamingState.error}</span>
          </div>
        </div>
      )}

      {/* Input */}
      <ChatInput
        onSubmit={onSendMessage}
        isDisabled={!isReady || streamingState.isStreaming}
        isStreaming={streamingState.isStreaming}
        placeholder={
          !isReady
            ? 'Select a physician to start...'
            : patientName
              ? `Ask a clinical question about ${patientName}...`
              : 'Ask a general clinical question...'
        }
      />
    </div>
  );
}

function StreamingStatus({ status }: { status: StreamingState['status'] }) {
  if (status === 'idle' || status === 'complete') {
    return null;
  }

  return (
    <div className={cn(
      "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium",
      status === 'searching' && "bg-blue-50 text-blue-700",
      status === 'generating' && "bg-purple-50 text-purple-700",
      status === 'error' && "bg-red-50 text-red-700"
    )}>
      {status === 'searching' && (
        <>
          <Search className="h-3.5 w-3.5 animate-pulse" />
          <span>Searching databases...</span>
        </>
      )}
      {status === 'generating' && (
        <>
          <Sparkles className="h-3.5 w-3.5 animate-pulse" />
          <span>Generating response...</span>
        </>
      )}
      {status === 'error' && (
        <>
          <AlertCircle className="h-3.5 w-3.5" />
          <span>Error</span>
        </>
      )}
    </div>
  );
}

function EmptyState({
  isReady,
  onSendMessage,
  patientName,
}: {
  isReady: boolean;
  onSendMessage: (query: string, mode: QueryMode) => void;
  patientName?: string;
}) {
  const hasPatient = !!patientName;

  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className={cn(
        "h-20 w-20 rounded-2xl flex items-center justify-center mb-6",
        hasPatient
          ? "bg-gradient-to-br from-blue-100 to-indigo-100"
          : "bg-gradient-to-br from-slate-100 to-slate-200"
      )}>
        {hasPatient ? (
          <User className="h-10 w-10 text-blue-600" />
        ) : (
          <Brain className="h-10 w-10 text-slate-500" />
        )}
      </div>

      <h3 className="text-xl font-semibold text-slate-900 mb-2">
        {hasPatient ? `Consulting for ${patientName}` : 'Clinical Decision Support'}
      </h3>

      <p className="text-sm text-slate-500 max-w-lg mb-8">
        {!isReady
          ? 'Select a physician from the dropdown to begin. You can ask questions with or without a patient selected.'
          : hasPatient
            ? "Ask questions about this patient's condition. I'll use their EHR data (medications, allergies, labs) to provide personalized recommendations."
            : "Ask general clinical questions. Select a patient from the left panel to get patient-specific recommendations using their EHR data."}
      </p>

      {isReady && (
        <>
          {/* Features */}
          <div className="flex items-center justify-center gap-6 mb-8">
            <Feature icon={Search} label="PubMed Search" />
            <Feature icon={BookOpen} label="Guidelines" />
            <Feature icon={Pill} label="Drug Safety" />
            {hasPatient && <Feature icon={Shield} label="Allergy Check" />}
          </div>

          {/* Example Queries - different for patient vs generic mode */}
          <div className="grid grid-cols-2 gap-3 w-full max-w-xl">
            {hasPatient ? (
              <>
                <ExampleQuery
                  text="What's the management plan?"
                  description="Patient-specific treatment"
                  onClick={() => onSendMessage("What's the management plan for this patient?", 'regular')}
                />
                <ExampleQuery
                  text="Check drug interactions"
                  description="Review medication safety"
                  onClick={() => onSendMessage('Are there any drug interactions with current medications?', 'regular')}
                />
                <ExampleQuery
                  text="Differential diagnosis"
                  description="Based on presentation"
                  onClick={() => onSendMessage('What is the differential diagnosis based on the presentation?', 'regular')}
                />
                <ExampleQuery
                  text="Adjust medications"
                  description="Consider allergies & labs"
                  onClick={() => onSendMessage('What medication adjustments should I consider given the labs and allergies?', 'regular')}
                />
              </>
            ) : (
              <>
                <ExampleQuery
                  text="Heart failure guidelines"
                  description="Latest recommendations"
                  onClick={() => onSendMessage('What are the latest heart failure treatment guidelines?', 'regular')}
                />
                <ExampleQuery
                  text="Antibiotic for UTI"
                  description="First-line treatment"
                  onClick={() => onSendMessage('What is the first-line antibiotic for uncomplicated UTI?', 'regular')}
                />
                <ExampleQuery
                  text="Hypertension targets"
                  description="BP goals by condition"
                  onClick={() => onSendMessage('What are the blood pressure targets for diabetic patients?', 'regular')}
                />
                <ExampleQuery
                  text="Drug interactions"
                  description="Warfarin considerations"
                  onClick={() => onSendMessage('What are the common drug interactions with warfarin?', 'regular')}
                />
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function Feature({ icon: Icon, label }: { icon: typeof Search; label: string }) {
  return (
    <div className="flex items-center gap-1.5 text-slate-500">
      <Icon className="h-4 w-4" />
      <span className="text-xs font-medium">{label}</span>
    </div>
  );
}

function ExampleQuery({
  text,
  description,
  onClick,
}: {
  text: string;
  description: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="text-left p-4 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all group"
    >
      <p className="text-sm font-medium text-slate-800 group-hover:text-blue-700">{text}</p>
      <p className="text-xs text-slate-500 mt-0.5">{description}</p>
    </button>
  );
}
