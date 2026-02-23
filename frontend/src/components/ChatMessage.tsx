"use client";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  metadata?: {
    doctor?: string;
    tools_used?: string[];
    mode?: string;
  };
}

export default function ChatMessage({
  role,
  content,
  isStreaming,
  metadata,
}: ChatMessageProps) {
  return (
    <div
      className={`flex ${role === "user" ? "justify-end" : "justify-start"} mb-4`}
    >
      <div
        className={`max-w-[85%] ${
          role === "user"
            ? "bg-[var(--accent)] text-white rounded-2xl rounded-br-md px-4 py-3"
            : "bg-[var(--bg-secondary)] border border-[var(--border)] rounded-2xl rounded-bl-md px-5 py-4"
        }`}
      >
        {role === "assistant" && (
          <div className="flex items-center gap-2 mb-2 pb-2 border-b border-[var(--border)]">
            <div className="w-2 h-2 rounded-full bg-[var(--success)]" />
            <span className="text-xs font-medium text-[var(--text-secondary)]">
              ContextMed
            </span>
            {metadata?.mode === "critical" && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--danger)]/20 text-[var(--danger)] font-medium">
                CRITICAL
              </span>
            )}
          </div>
        )}

        <div
          className={`response-content text-sm leading-relaxed whitespace-pre-wrap ${
            isStreaming ? "cursor-blink" : ""
          }`}
        >
          {content || (isStreaming ? "" : "...")}
        </div>

        {role === "assistant" && metadata?.tools_used && metadata.tools_used.length > 0 && !isStreaming && (
          <div className="flex flex-wrap gap-1.5 mt-3 pt-2 border-t border-[var(--border)]">
            {metadata.tools_used.map((tool) => (
              <span
                key={tool}
                className="text-[10px] px-2 py-0.5 rounded-full bg-[var(--bg-tertiary)] text-[var(--text-secondary)]"
              >
                {tool}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
