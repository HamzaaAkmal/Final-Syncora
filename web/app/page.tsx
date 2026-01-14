"use client";

import { useState, useEffect, useRef } from "react";
import {
  Send,
  Loader2,
  Bot,
  User,
  Database,
  Globe,
  Calculator,
  FileText,
  Microscope,
  Lightbulb,
  Trash2,
  ExternalLink,
  BookOpen,
  Sparkles,
  GraduationCap,
  PenTool,
} from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { useGlobal } from "@/context/GlobalContext";
import { apiUrl } from "@/lib/api";
import { processLatexContent } from "@/lib/latex";
import { getTranslation } from "@/lib/i18n";

interface KnowledgeBase {
  name: string;
  is_default?: boolean;
}

export default function HomePage() {
  const {
    chatState,
    setChatState,
    sendChatMessage,
    clearChatHistory,
    newChatSession,
    uiSettings,
  } = useGlobal();
  const t = (key: string) => getTranslation(uiSettings.language, key);

  const [inputMessage, setInputMessage] = useState("");
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch knowledge bases
  useEffect(() => {
    fetch(apiUrl("/api/v1/knowledge/list"))
      .then((res) => res.json())
      .then((data) => {
        setKbs(data);
        if (!chatState.selectedKb) {
          const defaultKb = data.find((kb: KnowledgeBase) => kb.is_default);
          if (defaultKb) {
            setChatState((prev) => ({ ...prev, selectedKb: defaultKb.name }));
          } else if (data.length > 0) {
            setChatState((prev) => ({ ...prev, selectedKb: data[0].name }));
          }
        }
      })
      .catch((err) => console.error("Failed to fetch KBs:", err));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatState.messages]);

  const handleSend = () => {
    if (!inputMessage.trim() || chatState.isLoading) return;
    sendChatMessage(inputMessage);
    setInputMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    {
      icon: Calculator,
      label: t("Smart Problem Solving"),
      href: "/solver",
      color: "emerald",
      description: "Multi-agent reasoning",
    },
    {
      icon: PenTool,
      label: t("Generate Practice Questions"),
      href: "/question",
      color: "emerald",
      description: "Auto-validated quizzes",
    },
    {
      icon: Microscope,
      label: t("Deep Research Reports"),
      href: "/research",
      color: "emerald",
      description: "Comprehensive analysis",
    },
    {
      icon: Lightbulb,
      label: t("Generate Novel Ideas"),
      href: "/ideagen",
      color: "emerald",
      description: "Brainstorm & synthesize",
    },
    {
      icon: GraduationCap,
      label: t("Guided Learning"),
      href: "/guide",
      color: "emerald",
      description: "Step-by-step tutoring",
    },
    {
      icon: FileText,
      label: t("Notes Assistant"),
      href: "/notes-assistant",
      color: "emerald",
      description: "PDF upload & Q&A",
    },
  ];

  const hasMessages = chatState.messages.length > 0;

  return (
    <div className="h-screen flex flex-col animate-fade-in" style={{ backgroundColor: '#050505' }}>
      {/* Empty State / Welcome Screen */}
      {!hasMessages && (
        <div className="flex-1 flex items-center justify-center px-6 overflow-y-auto">
          <div className="w-full max-w-3xl mx-auto">
            {/* Premium Hero Section - Centered */}
            <div className="text-center mb-8 animate-fade-in">
              {/* Main Heading */}
              <h1 className="text-4xl md:text-5xl mb-8 tracking-tight" style={{ fontFamily: 'Poppins, sans-serif', fontWeight: 700, color: '#F8FAFC' }}>
                What would you like to{' '}
                <span className="bg-gradient-to-r from-emerald-400 via-emerald-500 to-cyan-400 bg-clip-text text-transparent">
                  explore
                </span>
                ?
              </h1>

              {/* Premium Input Box */}
              <div className="mb-10">
                {/* Input Field with Glow Effect */}
                <div className="relative group">
                  {/* Glow Background */}
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 via-cyan-500 to-emerald-500 rounded-[28px] opacity-20 group-hover:opacity-40 blur transition-opacity duration-500" />
                  
                  <div className="relative rounded-[25px] p-1" style={{ backgroundColor: '#0F0F0F' }}>
                    <input
                      ref={inputRef}
                      type="text"
                      className="w-full px-6 py-5 pr-16 rounded-[22px] focus:outline-none transition-all font-medium text-lg"
                      style={{ 
                        backgroundColor: '#161616', 
                        color: '#F8FAFC',
                        border: 'none'
                      }}
                      placeholder={t("Ask anything...")}
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyDown={handleKeyDown}
                      disabled={chatState.isLoading}
                    />
                    <button
                      onClick={handleSend}
                      disabled={chatState.isLoading || !inputMessage.trim()}
                      className="absolute right-3 top-3 bottom-3 aspect-square flex items-center justify-center hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 transition-all"
                      style={{ 
                        background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                        borderRadius: '18px',
                        boxShadow: '0 4px 20px rgba(16, 185, 129, 0.4)'
                      }}
                    >
                      {chatState.isLoading ? (
                        <Loader2 className="w-5 h-5 animate-spin text-black" />
                      ) : (
                        <Send className="w-5 h-5 text-black" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Mode Toggles - Below Input */}
                <div className="flex items-center justify-center gap-3 mt-5 flex-wrap">
                  {/* RAG Toggle */}
                  <button
                onClick={() =>
                  setChatState((prev) => ({
                    ...prev,
                    enableRag: !prev.enableRag,
                  }))
                }
                className="flex items-center gap-2 px-4 py-2.5 rounded-2xl text-sm font-semibold transition-all duration-300"
                style={{
                  backgroundColor: chatState.enableRag ? '#10B981' : '#161616',
                  color: chatState.enableRag ? '#050505' : 'rgba(248, 250, 252, 0.7)',
                  border: chatState.enableRag ? 'none' : '1px solid #1F1F1F',
                  boxShadow: chatState.enableRag ? '0 4px 20px rgba(16, 185, 129, 0.3)' : 'none'
                }}
              >
                <Database className="w-4 h-4" />
                    {t("RAG")}
                  </button>

                  {/* Web Search Toggle */}
                  <button
                    onClick={() =>
                      setChatState((prev) => ({
                        ...prev,
                        enableWebSearch: !prev.enableWebSearch,
                      }))
                    }
                    className="flex items-center gap-2 px-4 py-2.5 rounded-2xl text-sm font-semibold transition-all duration-300"
                    style={{
                      backgroundColor: chatState.enableWebSearch ? '#10B981' : '#161616',
                      color: chatState.enableWebSearch ? '#050505' : 'rgba(248, 250, 252, 0.7)',
                      border: chatState.enableWebSearch ? 'none' : '1px solid #1F1F1F',
                      boxShadow: chatState.enableWebSearch ? '0 4px 20px rgba(16, 185, 129, 0.3)' : 'none'
                    }}
                  >
                    <Globe className="w-4 h-4" />
                    {t("Web Search")}
                  </button>

                  {/* KB Selector */}
                  {chatState.enableRag && (
                    <select
                      value={chatState.selectedKb}
                      onChange={(e) =>
                        setChatState((prev) => ({
                          ...prev,
                          selectedKb: e.target.value,
                        }))
                      }
                      className="text-sm rounded-2xl px-4 py-2.5 outline-none font-semibold transition-all"
                      style={{ 
                        backgroundColor: '#161616', 
                        color: 'rgba(248, 250, 252, 0.7)',
                        border: '1px solid #1F1F1F'
                      }}
                    >
                      {kbs.map((kb) => (
                        <option key={kb.name} value={kb.name}>
                          {kb.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat Interface - When there are messages */}
      {hasMessages && (
        <>
          {/* Header Bar */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card/80 backdrop-blur-xl">
            <div className="flex items-center gap-2 flex-wrap">
              {/* Mode Toggles */}
              <button
                onClick={() =>
                  setChatState((prev) => ({
                    ...prev,
                    enableRag: !prev.enableRag,
                  }))
                }
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-300 ${
                  chatState.enableRag
                    ? "bg-gradient-to-r from-cyan-500 to-cyan-600 text-white shadow-premium scale-105"
                    : "bg-muted text-muted-foreground hover:text-cyan-600 dark:hover:text-cyan-400"
                }`}
              >
                <Database className="w-3.5 h-3.5" />
                {t("RAG")}
              </button>

              <button
                onClick={() =>
                  setChatState((prev) => ({
                    ...prev,
                    enableWebSearch: !prev.enableWebSearch,
                  }))
                }
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-300 ${
                  chatState.enableWebSearch
                    ? "bg-gradient-to-r from-cyan-500 to-cyan-600 text-white shadow-premium scale-105"
                    : "bg-muted text-muted-foreground hover:text-cyan-600 dark:hover:text-cyan-400"
                }`}
              >
                <Globe className="w-3.5 h-3.5" />
                {t("Web Search")}
              </button>

              {chatState.enableRag && (
                <select
                  value={chatState.selectedKb}
                  onChange={(e) =>
                    setChatState((prev) => ({
                      ...prev,
                      selectedKb: e.target.value,
                    }))
                  }
                  className="text-xs bg-muted border-0 rounded-xl px-3 py-2 outline-none dark:text-slate-200 font-semibold"
                >
                  {kbs.map((kb) => (
                    <option key={kb.name} value={kb.name}>
                      {kb.name}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <button
              onClick={newChatSession}
              className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-muted-foreground hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-xl transition-all"
            >
              <Trash2 className="w-4 h-4" />
              {t("New Chat")}
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 bg-gradient-to-br from-background via-background to-midnight-900/5 dark:to-midnight-950/10">
            {chatState.messages.map((msg, idx) => (
              <div
                key={idx}
                className="flex gap-4 w-full max-w-4xl mx-auto animate-fade-in"
              >
                {msg.role === "user" ? (
                  <>
                    <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-800 flex items-center justify-center shrink-0 shadow-md">
                      <User className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                    </div>
                    <div className="flex-1 bg-gradient-to-br from-slate-100 to-slate-50 dark:from-slate-800 dark:to-slate-900 px-5 py-4 rounded-3xl rounded-tl-sm text-foreground font-medium shadow-md border border-slate-200/50 dark:border-slate-700/50">
                      {msg.content}
                    </div>
                  </>
                ) : (
                  <>
                    <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center shrink-0 shadow-premium ring-2 ring-cyan-400/20">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 space-y-3">
                      <div className="bg-card px-6 py-5 rounded-3xl rounded-tl-sm border-2 border-border shadow-premium backdrop-blur-sm">
                        <div className="prose prose-slate dark:prose-invert prose-sm max-w-none">
                          <ReactMarkdown
                            remarkPlugins={[remarkMath]}
                            rehypePlugins={[rehypeKatex]}
                          >
                            {processLatexContent(msg.content)}
                          </ReactMarkdown>
                        </div>

                        {/* Loading indicator */}
                        {msg.isStreaming && (
                          <div className="flex items-center gap-2 mt-4 text-primary text-sm font-semibold">
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>{t("Generating response...")}</span>
                          </div>
                        )}
                      </div>

                      {/* Sources */}
                      {msg.sources &&
                        (msg.sources.rag?.length ?? 0) +
                          (msg.sources.web?.length ?? 0) >
                          0 && (
                          <div className="flex flex-wrap gap-2">
                            {msg.sources.rag?.map((source, i) => (
                              <div
                                key={`rag-${i}`}
                                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs"
                                style={{ backgroundColor: '#0F0F0F', color: '#10B981', border: '1px solid #1F1F1F' }}
                              >
                                <BookOpen className="w-3 h-3" />
                                <span>{source.kb_name}</span>
                              </div>
                            ))}
                            {msg.sources.web?.slice(0, 3).map((source, i) => (
                              <a
                                key={`web-${i}`}
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 rounded-lg text-xs hover:bg-emerald-100 dark:hover:bg-emerald-900/50 transition-colors"
                              >
                                <Globe className="w-3 h-3" />
                                <span className="max-w-[150px] truncate">
                                  {source.title || source.url}
                                </span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            ))}
                          </div>
                        )}
                    </div>
                  </>
                )}
              </div>
            ))}

            {/* Status indicator */}
            {chatState.isLoading && chatState.currentStage && (
              <div className="flex gap-4 w-full max-w-4xl mx-auto">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shrink-0">
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                </div>
                <div className="flex-1 bg-slate-100 dark:bg-slate-800 px-4 py-3 rounded-2xl rounded-tl-none">
                  <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300 text-sm">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                    </span>
                    {chatState.currentStage === "rag" &&
                      t("Searching knowledge base...")}
                    {chatState.currentStage === "web" &&
                      t("Searching the web...")}
                    {chatState.currentStage === "generating" &&
                      t("Generating response...")}
                    {!["rag", "web", "generating"].includes(
                      chatState.currentStage,
                    ) && chatState.currentStage}
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Input Area - Fixed at bottom */}
          <div className="border-t-2 border-border bg-card/80 backdrop-blur-xl px-6 py-5">
            <div className="max-w-4xl mx-auto relative">
              <input
                ref={inputRef}
                type="text"
                className="w-full px-6 py-4 pr-16 bg-background border-2 border-border rounded-[25px] focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all placeholder:text-muted-foreground text-foreground font-medium shadow-inner-premium"
                placeholder={t("Type your message...")}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={chatState.isLoading}
              />
              <button
                onClick={handleSend}
                disabled={chatState.isLoading || !inputMessage.trim()}
                className="absolute right-2 top-2 bottom-2 aspect-square bg-gradient-to-br from-cyan-500 to-cyan-600 text-white rounded-[23px] flex items-center justify-center hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 transition-all shadow-premium"
              >
                {chatState.isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
