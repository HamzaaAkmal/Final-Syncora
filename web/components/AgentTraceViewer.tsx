"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Activity,
  Bot,
  Brain,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock,
  Cpu,
  FileText,
  Loader2,
  MessageSquare,
  Network,
  Play,
  RefreshCw,
  Search,
  Sparkles,
  Target,
  X,
  Zap,
} from "lucide-react";

// Agent types with their icons and colors
const AGENT_CONFIG: Record<string, { icon: React.ReactNode; color: string; label: string; labelUr: string }> = {
  manager: {
    icon: <Brain className="w-4 h-4" />,
    color: "bg-purple-500",
    label: "Manager Agent",
    labelUr: "مینیجر ایجنٹ"
  },
  assessment: {
    icon: <Target className="w-4 h-4" />,
    color: "bg-blue-500",
    label: "Assessment Agent",
    labelUr: "تشخیص ایجنٹ"
  },
  content: {
    icon: <FileText className="w-4 h-4" />,
    color: "bg-green-500",
    label: "Content Agent",
    labelUr: "مواد ایجنٹ"
  },
  tutor: {
    icon: <MessageSquare className="w-4 h-4" />,
    color: "bg-yellow-500",
    label: "Tutor Agent",
    labelUr: "ٹیوٹر ایجنٹ"
  },
  solve: {
    icon: <Zap className="w-4 h-4" />,
    color: "bg-orange-500",
    label: "Solve Agent",
    labelUr: "حل ایجنٹ"
  },
  safety: {
    icon: <CheckCircle2 className="w-4 h-4" />,
    color: "bg-red-500",
    label: "Safety Agent",
    labelUr: "حفاظت ایجنٹ"
  },
  research: {
    icon: <Search className="w-4 h-4" />,
    color: "bg-indigo-500",
    label: "Research Agent",
    labelUr: "تحقیق ایجنٹ"
  },
  response: {
    icon: <Sparkles className="w-4 h-4" />,
    color: "bg-pink-500",
    label: "Response Agent",
    labelUr: "جواب ایجنٹ"
  },
};

interface AgentAction {
  id: string;
  agent: string;
  action: string;
  input?: string;
  output?: string;
  status: "pending" | "running" | "completed" | "error";
  duration_ms?: number;
  timestamp: string;
  children?: AgentAction[];
}

interface AgentTrace {
  trace_id: string;
  session_id: string;
  started_at: string;
  completed_at?: string;
  status: "running" | "completed" | "error";
  total_duration_ms?: number;
  actions: AgentAction[];
  summary?: string;
}

interface AgentTraceViewerProps {
  isUrdu?: boolean;
  sessionId?: string;
  onClose?: () => void;
  embedded?: boolean;
}

// Demo trace data for hackathon
const DEMO_TRACE: AgentTrace = {
  trace_id: "trace_demo_001",
  session_id: "session_demo",
  started_at: new Date().toISOString(),
  status: "completed",
  total_duration_ms: 4250,
  actions: [
    {
      id: "action_1",
      agent: "manager",
      action: "Analyze student query",
      input: "Explain quadratic equations",
      status: "completed",
      duration_ms: 150,
      timestamp: new Date().toISOString(),
    },
    {
      id: "action_2",
      agent: "safety",
      action: "Content safety check",
      input: "Checking query for safety compliance",
      output: "Query is safe and educational",
      status: "completed",
      duration_ms: 80,
      timestamp: new Date().toISOString(),
    },
    {
      id: "action_3",
      agent: "assessment",
      action: "Evaluate student level",
      input: "Check student's current understanding of algebra",
      output: "Student at intermediate level, has prior knowledge of linear equations",
      status: "completed",
      duration_ms: 320,
      timestamp: new Date().toISOString(),
    },
    {
      id: "action_4",
      agent: "content",
      action: "Fetch curriculum content",
      input: "Get PCTB Grade 9 quadratic equations content",
      output: "Retrieved 3 learning objectives and 5 examples",
      status: "completed",
      duration_ms: 450,
      timestamp: new Date().toISOString(),
    },
    {
      id: "action_5",
      agent: "tutor",
      action: "Generate personalized explanation",
      input: "Create step-by-step explanation with examples",
      output: "Generated explanation with 3 solved examples",
      status: "completed",
      duration_ms: 2800,
      timestamp: new Date().toISOString(),
    },
    {
      id: "action_6",
      agent: "response",
      action: "Format final response",
      input: "Combine all content into student-friendly format",
      output: "Response ready with markdown formatting",
      status: "completed",
      duration_ms: 350,
      timestamp: new Date().toISOString(),
    },
    {
      id: "action_7",
      agent: "manager",
      action: "Deliver response to student",
      status: "completed",
      duration_ms: 100,
      timestamp: new Date().toISOString(),
    },
  ],
  summary: "Successfully generated personalized explanation for quadratic equations aligned with PCTB Grade 9 curriculum.",
};

export default function AgentTraceViewer({
  isUrdu = false,
  sessionId,
  onClose,
  embedded = false,
}: AgentTraceViewerProps) {
  const [trace, setTrace] = useState<AgentTrace | null>(null);
  const [loading, setLoading] = useState(false);
  const [expandedActions, setExpandedActions] = useState<Set<string>>(new Set());
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [showDemo, setShowDemo] = useState(true);
  
  const containerRef = useRef<HTMLDivElement>(null);

  // Load trace data
  useEffect(() => {
    if (showDemo) {
      // Show demo trace for hackathon
      setTrace(DEMO_TRACE);
    } else if (sessionId) {
      fetchTrace(sessionId);
    }
  }, [sessionId, showDemo]);

  // Auto-refresh for running traces
  useEffect(() => {
    if (!autoRefresh || !sessionId || trace?.status === "completed") return;
    
    const interval = setInterval(() => {
      fetchTrace(sessionId);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [autoRefresh, sessionId, trace?.status]);

  const fetchTrace = async (sid: string) => {
    setLoading(true);
    try {
      // In production, this would fetch from the API
      // For now, use demo data
      setTrace(DEMO_TRACE);
    } catch (e) {
      console.error("Failed to fetch trace:", e);
    } finally {
      setLoading(false);
    }
  };

  const toggleAction = (actionId: string) => {
    setExpandedActions(prev => {
      const next = new Set(prev);
      if (next.has(actionId)) {
        next.delete(actionId);
      } else {
        next.add(actionId);
      }
      return next;
    });
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return "-";
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case "running":
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case "error":
        return <X className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const renderAction = (action: AgentAction, depth: number = 0) => {
    const config = AGENT_CONFIG[action.agent] || {
      icon: <Bot className="w-4 h-4" />,
      color: "bg-gray-500",
      label: action.agent,
      labelUr: action.agent,
    };
    
    const isExpanded = expandedActions.has(action.id);
    const hasDetails = action.input || action.output;
    
    return (
      <div key={action.id} className="relative">
        {/* Connection line */}
        {depth > 0 && (
          <div 
            className="absolute left-6 top-0 w-0.5 h-full bg-slate-200 dark:bg-slate-600"
            style={{ marginLeft: depth * 24 }}
          />
        )}
        
        <div 
          className={`flex items-start gap-3 p-3 rounded-lg transition-colors cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/50 ${
            isExpanded ? "bg-slate-50 dark:bg-slate-700/50" : ""
          }`}
          style={{ marginLeft: depth * 24 }}
          onClick={() => hasDetails && toggleAction(action.id)}
        >
          {/* Agent icon */}
          <div className={`flex-shrink-0 w-8 h-8 rounded-full ${config.color} flex items-center justify-center text-white`}>
            {config.icon}
          </div>
          
          {/* Action details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium text-slate-900 dark:text-white text-sm">
                {isUrdu ? config.labelUr : config.label}
              </span>
              {getStatusIcon(action.status)}
              {action.duration_ms && (
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  {formatDuration(action.duration_ms)}
                </span>
              )}
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-300 mt-0.5">
              {action.action}
            </p>
            
            {/* Expanded details */}
            {isExpanded && hasDetails && (
              <div className="mt-3 space-y-2 text-sm">
                {action.input && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-2 rounded">
                    <span className="font-medium text-blue-700 dark:text-blue-300">
                      {isUrdu ? "ان پٹ:" : "Input:"}
                    </span>
                    <p className="text-blue-600 dark:text-blue-200 mt-1">{action.input}</p>
                  </div>
                )}
                {action.output && (
                  <div className="bg-green-50 dark:bg-green-900/20 p-2 rounded">
                    <span className="font-medium text-green-700 dark:text-green-300">
                      {isUrdu ? "آؤٹ پٹ:" : "Output:"}
                    </span>
                    <p className="text-green-600 dark:text-green-200 mt-1">{action.output}</p>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Expand indicator */}
          {hasDetails && (
            <div className="flex-shrink-0 text-slate-400">
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </div>
          )}
        </div>
        
        {/* Render children */}
        {action.children?.map(child => renderAction(child, depth + 1))}
      </div>
    );
  };

  const containerClass = embedded
    ? "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden"
    : "fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4";

  const contentClass = embedded
    ? ""
    : "bg-white dark:bg-slate-800 rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-xl";

  return (
    <div className={containerClass} dir={isUrdu ? "rtl" : "ltr"}>
      <div className={contentClass}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
              <Network className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-slate-900 dark:text-white">
                {isUrdu ? "ایجنٹ تعاون لاگز" : "Agent Collaboration Logs"}
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {isUrdu ? "AI ایجنٹس کے درمیان ہم آہنگی" : "Multi-agent coordination trace"}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Demo toggle */}
            <button
              onClick={() => setShowDemo(!showDemo)}
              className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                showDemo 
                  ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
                  : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
              }`}
            >
              {isUrdu ? "ڈیمو" : "Demo"}
            </button>
            
            {/* Refresh */}
            <button
              onClick={() => sessionId && fetchTrace(sessionId)}
              disabled={loading}
              className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            
            {/* Close */}
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
        
        {/* Trace info */}
        {trace && (
          <div className="px-4 py-3 bg-slate-50 dark:bg-slate-700/50 border-b border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1.5">
                  <Activity className="w-4 h-4 text-slate-400" />
                  <span className="text-slate-600 dark:text-slate-300">
                    {trace.actions.length} {isUrdu ? "اقدامات" : "actions"}
                  </span>
                </span>
                <span className="flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-slate-400" />
                  <span className="text-slate-600 dark:text-slate-300">
                    {formatDuration(trace.total_duration_ms)}
                  </span>
                </span>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                trace.status === "completed"
                  ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
                  : trace.status === "running"
                  ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                  : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
              }`}>
                {trace.status === "completed" 
                  ? (isUrdu ? "مکمل" : "Completed")
                  : trace.status === "running"
                  ? (isUrdu ? "جاری" : "Running")
                  : (isUrdu ? "خرابی" : "Error")}
              </span>
            </div>
          </div>
        )}
        
        {/* Actions list */}
        <div 
          ref={containerRef}
          className="overflow-y-auto p-4 space-y-2"
          style={{ maxHeight: embedded ? "400px" : "50vh" }}
        >
          {loading && !trace ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
            </div>
          ) : trace ? (
            <>
              {trace.actions.map(action => renderAction(action))}
              
              {/* Summary */}
              {trace.summary && (
                <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-purple-500" />
                    <span className="font-medium text-purple-700 dark:text-purple-300">
                      {isUrdu ? "خلاصہ" : "Summary"}
                    </span>
                  </div>
                  <p className="text-sm text-purple-600 dark:text-purple-200">
                    {trace.summary}
                  </p>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 text-slate-500 dark:text-slate-400">
              <Network className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>{isUrdu ? "کوئی ٹریس دستیاب نہیں" : "No trace available"}</p>
              <button
                onClick={() => setShowDemo(true)}
                className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                {isUrdu ? "ڈیمو دیکھیں" : "View Demo"}
              </button>
            </div>
          )}
        </div>
        
        {/* Agent legend */}
        <div className="px-4 py-3 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-700/50">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">
            {isUrdu ? "ایجنٹس:" : "Agents:"}
          </p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(AGENT_CONFIG).map(([key, config]) => (
              <div key={key} className="flex items-center gap-1.5 text-xs">
                <div className={`w-3 h-3 rounded-full ${config.color}`} />
                <span className="text-slate-600 dark:text-slate-300">
                  {isUrdu ? config.labelUr : config.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Inline embedded version for dashboard
export function AgentTraceInline({ isUrdu = false }: { isUrdu?: boolean }) {
  return (
    <div className="mt-6">
      <AgentTraceViewer isUrdu={isUrdu} embedded={true} />
    </div>
  );
}
