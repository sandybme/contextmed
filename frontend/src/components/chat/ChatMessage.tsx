'use client';

import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Sparkles, AlertTriangle, ExternalLink } from 'lucide-react';
import { cn, formatTime } from '@/lib/utils';
import { Badge } from '@/components/ui';
import type { ChatMessage as ChatMessageType } from '@/types';

interface ChatMessageProps {
  message: ChatMessageType;
  doctorName?: string;
}

export function ChatMessage({ message, doctorName }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isStreaming = message.isStreaming;
  const hasContent = message.content.trim().length > 0;

  // Parse sections from content
  const sections = useMemo(() => {
    const content = message.content;
    const hasAllergyAlert = content.includes('## ALLERGY ALERTS');
    return { hasAllergyAlert };
  }, [message.content]);

  // Clean content for display - remove status indicators and metadata
  const cleanedContent = useMemo(() => {
    return message.content
      // Remove status indicators (analyzing, searching, gathering evidence)
      .replace(/🤔 Analyzing query\.\.\.\n?/g, '')
      .replace(/📚 Gathering evidence\.\.\.\n?/g, '')
      .replace(/🔍 Searching [^\n]+\.\.\.\n?/g, '')
      .replace(/🚨 Searching [^\n]+\.\.\.\n?/g, '')
      .replace(/   ✓ [^\n]+\n?/g, '')
      .replace(/\n📋 Evidence gathered from: [^\n]+\n?/g, '')
      .replace(/─{20,}\n?/g, '')
      // Remove allergy alerts section (handled separately)
      .replace(/## ALLERGY ALERTS[\s\S]*?---/g, '')
      // Remove tools footer (handled separately)
      .replace(/\*Tools used:[\s\S]*?\*/g, '')
      .replace(/\n\*Tools: [^\n]+\*$/g, '')
      .trim();
  }, [message.content]);

  return (
    <div
      className={cn(
        'flex gap-4 px-5 py-4',
        isUser ? 'bg-white' : 'bg-slate-50/50'
      )}
    >
      {/* Avatar */}
      <div className="flex-shrink-0 mt-1">
        {isUser ? (
          <div className="h-9 w-9 rounded-lg bg-slate-200 flex items-center justify-center">
            <User className="h-4 w-4 text-slate-600" />
          </div>
        ) : (
          <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-sm">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <span className="font-semibold text-slate-900">
            {isUser ? 'You' : 'ContextMed AI'}
          </span>
          <span className="text-xs text-slate-400">{formatTime(message.timestamp)}</span>
        </div>

        {/* Allergy Alert Box */}
        {sections.hasAllergyAlert && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-center gap-2 text-red-700 font-semibold mb-2">
              <AlertTriangle className="h-4 w-4" />
              <span>Allergy Alerts</span>
            </div>
            <div className="text-sm text-red-600 space-y-1">
              {message.content
                .split('## ALLERGY ALERTS')[1]
                ?.split('---')[0]
                ?.split('\n')
                .filter((line) => line.trim().startsWith('- '))
                .map((line, i) => (
                  <div key={i}>{line}</div>
                ))}
            </div>
          </div>
        )}

        {/* Message Content */}
        <div className="prose prose-sm max-w-none prose-slate prose-headings:text-slate-900 prose-p:text-slate-700 prose-a:text-blue-600 prose-strong:text-slate-900 prose-li:text-slate-700">
          {isUser ? (
            <p className="text-slate-800 m-0">{message.content}</p>
          ) : hasContent ? (
            <ReactMarkdown
              components={{
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline inline-flex items-center gap-0.5"
                  >
                    {children}
                    <ExternalLink className="h-3 w-3" />
                  </a>
                ),
                h1: ({ children }) => (
                  <h1 className="text-lg font-bold mt-4 mb-2 text-slate-900">{children}</h1>
                ),
                h2: ({ children }) => {
                  const text = String(children);
                  if (text === 'ALLERGY ALERTS') return null;
                  return <h2 className="text-base font-semibold mt-4 mb-2 text-slate-900">{children}</h2>;
                },
                h3: ({ children }) => (
                  <h3 className="text-sm font-semibold mt-3 mb-1 text-slate-800">{children}</h3>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-outside ml-4 space-y-1 my-2">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-outside ml-4 space-y-1 my-2">{children}</ol>
                ),
                li: ({ children }) => (
                  <li className="text-slate-700">{children}</li>
                ),
                p: ({ children }) => {
                  const text = String(children);
                  if (text.startsWith('*Tools used:')) return null;
                  return <p className="my-2 text-slate-700 leading-relaxed">{children}</p>;
                },
                strong: ({ children }) => (
                  <strong className="font-semibold text-slate-900">{children}</strong>
                ),
                code: ({ children }) => (
                  <code className="bg-slate-100 px-1.5 py-0.5 rounded text-sm text-slate-800">{children}</code>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-blue-300 pl-4 italic text-slate-600 my-3">{children}</blockquote>
                ),
                hr: () => <hr className="border-slate-200 my-4" />,
              }}
            >
              {cleanedContent}
            </ReactMarkdown>
          ) : isStreaming ? (
            // Show typing indicator only when streaming with no content yet
            <div className="flex items-center gap-2 text-slate-500">
              <span className="inline-flex gap-1">
                <span className="h-2 w-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="h-2 w-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="h-2 w-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '300ms' }} />
              </span>
            </div>
          ) : null}
        </div>

        {/* Streaming cursor at end of content */}
        {isStreaming && hasContent && (
          <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-0.5 align-text-bottom" />
        )}

        {/* Tools Used Footer */}
        {!isUser && message.metadata?.toolsUsed && message.metadata.toolsUsed.length > 0 && !isStreaming && (
          <div className="mt-4 pt-3 border-t border-slate-100">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-slate-400 font-medium">Sources:</span>
              {message.metadata.toolsUsed.map((tool) => (
                <Badge key={tool} size="sm" variant="info">
                  {tool}
                </Badge>
              ))}
              {message.metadata.mode === 'critical' && (
                <Badge size="sm" variant="danger">
                  Critical
                </Badge>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
