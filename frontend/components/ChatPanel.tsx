"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Volume2, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import VoiceInput from "./VoiceInput";

interface ChatMessage {
  type: "user" | "assistant";
  text: string;
  exactQuote?: string;
  source?: {
    page: number;
    section: string;
    node_id: string;
  };
  followUps?: string[];
  audioUrl?: string;
}

interface ChatPanelProps {
  docId: string;
  onQuery: (
    query: string,
    language: string,
    inputMode: string,
    outputMode: string
  ) => Promise<{
    exact_quote: string;
    simple_explanation: string;
    source: { page: number; section: string; node_id: string };
    follow_up_suggestions: string[];
    audio_url?: string;
  }>;
  onSourceClick: (page: number) => void;
  prefillQuery?: string;
}

export default function ChatPanel({
  docId,
  onQuery,
  onSourceClick,
  prefillQuery,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [outputMode, setOutputMode] = useState<"text" | "voice">("text");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (prefillQuery) {
      setInput(prefillQuery);
    }
  }, [prefillQuery]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (queryText?: string) => {
    const query = queryText || input.trim();
    if (!query || isLoading) return;

    const userMessage: ChatMessage = { type: "user", text: query };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const hasHindi = /[\u0900-\u097F]/.test(query);
      const hindiWords = [
        "kya", "hai", "kab", "kaise", "kitna", "dena", "kiraya",
        "batao", "samjhao", "hoga", "mein", "karna",
      ];
      const words = query.toLowerCase().split(/\s+/);
      const isHindi = hasHindi || words.some((w) => hindiWords.includes(w));
      const language = isHindi ? "hi" : "en";

      const response = await onQuery(query, language, "text", outputMode);

      const assistantMessage: ChatMessage = {
        type: "assistant",
        text: response.simple_explanation,
        exactQuote: response.exact_quote,
        source: response.source,
        followUps: response.follow_up_suggestions,
        audioUrl: response.audio_url,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          text: "Sorry, kuch gadbad ho gayi. Please dobara try karo.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceResult = (text: string) => {
    setInput(text);
    handleSend(text);
  };

  const handleFollowUp = (question: string) => {
    setInput(question);
    handleSend(question);
  };

  const playAudio = (audioUrl: string) => {
    const audio = new Audio(audioUrl);
    audio.play();
  };

  return (
    <div className="panel flex flex-col h-full">
      <div className="panel-header flex items-center justify-between">
        <span>Ask Questions</span>
        <button
          onClick={() =>
            setOutputMode((prev) => (prev === "text" ? "voice" : "text"))
          }
          className={`text-xs px-2 py-0.5 border border-white/30 ${
            outputMode === "voice" ? "bg-green-600" : "bg-transparent"
          }`}
          title={outputMode === "voice" ? "Voice output ON" : "Voice output OFF"}
        >
          <Volume2 className="w-3 h-3 inline mr-1" />
          {outputMode === "voice" ? "ON" : "OFF"}
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-text-secondary py-8">
            <p className="font-bold mb-2">Sawaal pucho!</p>
            <p className="text-sm">
              Document ke baare mein kuch bhi pucho — Hindi ya English mein.
            </p>
            <div className="mt-4 space-y-2">
              {[
                "Is document mein kya likha hai?",
                "Kiraya kab dena hai?",
                "Koi hidden charges hai?",
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  className="block w-full text-left text-sm bg-accent border-2 border-primary px-4 py-2 shadow-brutal-sm hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all duration-100"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            message={msg}
            onSourceClick={onSourceClick}
            onFollowUp={handleFollowUp}
            onPlayAudio={playAudio}
          />
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-text-secondary">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm loading-dots">Soch raha hoon</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t-2 border-primary p-3 bg-surface">
        <div className="flex items-center gap-2">
          <VoiceInput onResult={handleVoiceResult} />
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Sawaal pucho..."
            className="input-brutal flex-1 text-sm py-2"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="btn-brutal py-2 px-3 disabled:opacity-30 disabled:pointer-events-none"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({
  message,
  onSourceClick,
  onFollowUp,
  onPlayAudio,
}: {
  message: ChatMessage;
  onSourceClick: (page: number) => void;
  onFollowUp: (q: string) => void;
  onPlayAudio: (url: string) => void;
}) {
  if (message.type === "user") {
    return (
      <div className="flex justify-end">
        <div className="bg-primary text-background px-4 py-2 max-w-[85%] border-2 border-primary shadow-brutal-sm">
          <p className="text-sm">{message.text}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {message.exactQuote && (
        <div className="bg-accent border-2 border-primary px-3 py-2 shadow-brutal-sm">
          <p className="text-xs font-bold text-text-secondary mb-1 uppercase tracking-wider">
            Document mein likha hai:
          </p>
          <p className="text-sm font-mono italic">
            &ldquo;{message.exactQuote}&rdquo;
          </p>
        </div>
      )}

      <div className="bg-surface border-2 border-primary px-4 py-3 shadow-brutal-sm max-w-[95%]">
        <div className="text-sm leading-relaxed prose prose-sm max-w-none">
          <ReactMarkdown>{message.text}</ReactMarkdown>
        </div>

        {message.source && (
          <button
            onClick={() => onSourceClick(message.source!.page)}
            className="mt-2 text-xs text-text-secondary hover:text-primary underline"
          >
            Source: {message.source.section} — Page {message.source.page}
          </button>
        )}

        {message.audioUrl && (
          <button
            onClick={() => onPlayAudio(message.audioUrl!)}
            className="mt-2 ml-3 btn-brutal-outline text-xs py-1 px-2"
          >
            <Volume2 className="w-3 h-3 inline mr-1" />
            Suno
          </button>
        )}
      </div>

      {message.followUps && message.followUps.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-1">
          {message.followUps.map((q, i) => (
            <button
              key={i}
              onClick={() => onFollowUp(q)}
              className="text-xs bg-accent border-2 border-primary px-3 py-1 shadow-brutal-sm hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-none transition-all duration-100"
            >
              {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
