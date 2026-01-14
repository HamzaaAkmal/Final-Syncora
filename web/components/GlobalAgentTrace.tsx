"use client";

import React, { useState, useEffect } from "react";
import {
  Activity,
  Brain,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock,
  Cpu,
  FileText,
  Loader2,
  MessageSquare,
  Minimize2,
  Maximize2,
  Network,
  Search,
  Sparkles,
  Target,
  X,
  Zap,
  AlertCircle,
  Wifi,
  WifiOff,
} from "lucide-react";
import { useAgentTrace, AgentAction } from "@/context/AgentTraceContext";

// Agent configuration
const AGENT_CONFIG: Record<string, { 
  icon: React.ReactNode; 
  color: string; 
  bgColor: string;
  label: string; 
  labelUr: string 
}> = {
  manager: {
    icon: <Brain className="w-3.5 h-3.5" />,
    color: "text-purple-600 dark:text-purple-400",
    bgColor: "bg-purple-100 dark:bg-purple-900/30",
    label: "Manager",
    labelUr: "مینیجر"
  },
  assessment: {
    icon: <Target className="w-3.5 h-3.5" />,
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-100 dark:bg-blue-900/30",
    label: "Assessment",
    labelUr: "تشخیص"
  },
  content: {
    icon: <FileText className="w-3.5 h-3.5" />,
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-100 dark:bg-green-900/30",
    label: "Content",
    labelUr: "مواد"
  },
  tutor: {
    icon: <MessageSquare className="w-3.5 h-3.5" />,
    color: "text-yellow-600 dark:text-yellow-400",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/30",
    label: "Tutor",
    labelUr: "ٹیوٹر"
  },
  solve: {
    icon: <Zap className="w-3.5 h-3.5" />,
    color: "text-orange-600 dark:text-orange-400",
    bgColor: "bg-orange-100 dark:bg-orange-900/30",
    label: "Solver",
    labelUr: "حل"
  },
  safety: {
    icon: <CheckCircle2 className="w-3.5 h-3.5" />,
    color: "text-red-600 dark:text-red-400",
    bgColor: "bg-red-100 dark:bg-red-900/30",
    label: "Safety",
    labelUr: "حفاظت"
  },
  research: {
    icon: <Search className="w-3.5 h-3.5" />,
    color: "text-indigo-600 dark:text-indigo-400",
    bgColor: "bg-indigo-100 dark:bg-indigo-900/30",
    label: "Research",
    labelUr: "تحقیق"
  },
  response: {
    icon: <Sparkles className="w-3.5 h-3.5" />,
    color: "text-pink-600 dark:text-pink-400",
    bgColor: "bg-pink-100 dark:bg-pink-900/30",
    label: "Response",
    labelUr: "جواب"
  },
};

interface GlobalAgentTraceProps {
  isUrdu?: boolean;
}

export default function GlobalAgentTrace({ isUrdu = false }: GlobalAgentTraceProps) {
  const {
    currentTrace,
    recentActions,
    isConnected,
    isTraceVisible,
    setTraceVisible,
    isMinimized,
    setMinimized,
  } = useAgentTrace();
  
  const [expandedActions, setExpandedActions] = useState<Set<string>>(new Set());
  
  // Auto-expand latest action
  useEffect(() => {
    if (recentActions.length > 0 && recentActions[0].status === "running") {
      setExpandedActions(prev => new Set([...prev, recentActions[0].id]));
    }
  }, [recentActions]);
  
  const toggleAction = (id: string) => {
    setExpandedActions(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };
  
  const getAgentConfig = (agent: string) => {
    return AGENT_CONFIG[agent] || {
      icon: <Cpu className="w-3.5 h-3.5" />,
      color: "text-gray-600 dark:text-gray-400",
      bgColor: "bg-gray-100 dark:bg-gray-900/30",
      label: agent,
      labelUr: agent,
    };
  };
  
  const getStatusIcon = (status: AgentAction["status"]) => {
    switch (status) {
      case "running":
        return <Loader2 className="w-3 h-3 animate-spin text-blue-500" />;
      case "completed":
        return <CheckCircle2 className="w-3 h-3 text-green-500" />;
      case "error":
        return <AlertCircle className="w-3 h-3 text-red-500" />;
      default:
        return <Clock className="w-3 h-3 text-gray-400" />;
    }
  };
  
  // Don't render if no trace or not visible
  if (!isTraceVisible || (!currentTrace && recentActions.length === 0)) {
    return (
      <button
        onClick={() => setTraceVisible(true)}
        className="fixed bottom-20 right-4 z-40 bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-3 rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-105"
        title={isUrdu ? "ایجنٹ لاگز دیکھیں" : "View Agent Logs"}
      >
        <Network className="w-5 h-5" />
        {currentTrace?.status === "running" && (
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
        )}
      </button>
    );
  }
  
  // Minimized view
  if (isMinimized) {
    return (
      <div className="fixed bottom-20 right-4 z-50 bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 p-3 w-72">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Network className="w-4 h-4 text-purple-500" />
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {isUrdu ? "ایجنٹ لاگز" : "Agent Trace"}
            </span>
            {currentTrace?.status === "running" && (
              <span className="flex items-center gap-1 text-xs text-blue-500">
                <Loader2 className="w-3 h-3 animate-spin" />
                {isUrdu ? "چل رہا ہے" : "Running"}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setMinimized(false)}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              <Maximize2 className="w-4 h-4 text-gray-500" />
            </button>
            <button
              onClick={() => setTraceVisible(false)}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>
        
        {/* Mini progress bar */}
        {currentTrace && (
          <div className="mt-2 flex items-center gap-1">
            {currentTrace.actions.slice(-5).map((action, i) => {
              const config = getAgentConfig(action.agent);
              return (
                <div
                  key={action.id}
                  className={`w-6 h-6 rounded-full flex items-center justify-center ${config.bgColor} ${config.color}`}
                  title={`${config.label}: ${action.action}`}
                >
                  {action.status === "running" ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    config.icon
                  )}
                </div>
              );
            })}
            {currentTrace.actions.length > 5 && (
              <span className="text-xs text-gray-500">
                +{currentTrace.actions.length - 5}
              </span>
            )}
          </div>
        )}
      </div>
    );
  }
  
  // Full view
  return (
    <div className="fixed bottom-20 right-4 z-50 bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 w-96 max-h-[70vh] flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Network className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {isUrdu ? "ایجنٹ تعاون لاگز" : "Agent Collaboration"}
            </h3>
            <span className={`flex items-center gap-1 text-xs ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
              {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
              {isConnected ? (isUrdu ? "منسلک" : "Live") : (isUrdu ? "غیر منسلک" : "Offline")}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setMinimized(true)}
              className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              title={isUrdu ? "چھوٹا کریں" : "Minimize"}
            >
              <Minimize2 className="w-4 h-4 text-gray-500" />
            </button>
            <button
              onClick={() => setTraceVisible(false)}
              className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              title={isUrdu ? "بند کریں" : "Close"}
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>
        
        {/* Trace status */}
        {currentTrace && (
          <div className="mt-2 flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
            <span>
              {currentTrace.status === "running" ? (
                <span className="flex items-center gap-1 text-blue-500">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  {isUrdu ? "عمل جاری ہے..." : "Processing..."}
                </span>
              ) : (
                <span className="flex items-center gap-1 text-green-500">
                  <CheckCircle2 className="w-3 h-3" />
                  {isUrdu ? "مکمل" : "Completed"}
                </span>
              )}
            </span>
            <span>
              {currentTrace.actions.length} {isUrdu ? "ایکشنز" : "actions"}
              {currentTrace.total_duration_ms && ` • ${currentTrace.total_duration_ms}ms`}
            </span>
          </div>
        )}
      </div>
      
      {/* Actions list */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {(currentTrace?.actions || recentActions).slice().reverse().map((action, index) => {
          const config = getAgentConfig(action.agent);
          const isExpanded = expandedActions.has(action.id);
          // Create unique key combining trace id and action id to avoid duplicates
          const uniqueKey = currentTrace?.id ? `${currentTrace.id}-${action.id}` : `recent-${index}-${action.id}`;
          
          return (
            <div
              key={uniqueKey}
              className={`rounded-lg border transition-all ${
                action.status === "running"
                  ? "border-blue-300 dark:border-blue-700 bg-blue-50/50 dark:bg-blue-900/20"
                  : action.status === "error"
                  ? "border-red-300 dark:border-red-700 bg-red-50/50 dark:bg-red-900/20"
                  : "border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/20"
              }`}
            >
              {/* Action header */}
              <button
                onClick={() => toggleAction(action.id)}
                className="w-full p-2 flex items-center gap-2 text-left"
              >
                {/* Agent icon */}
                <div className={`p-1.5 rounded-lg ${config.bgColor} ${config.color}`}>
                  {config.icon}
                </div>
                
                {/* Action info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1">
                    <span className={`text-sm font-medium ${config.color}`}>
                      {isUrdu ? config.labelUr : config.label}
                    </span>
                    {getStatusIcon(action.status)}
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                    {action.action}
                  </p>
                </div>
                
                {/* Duration & expand */}
                <div className="flex items-center gap-2">
                  {action.duration_ms && (
                    <span className="text-xs text-gray-400">
                      {action.duration_ms}ms
                    </span>
                  )}
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              </button>
              
              {/* Expanded details */}
              {isExpanded && (
                <div className="px-2 pb-2 pt-1 border-t border-gray-200 dark:border-gray-700 space-y-2">
                  {action.input && (
                    <div>
                      <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                        {isUrdu ? "ان پٹ:" : "Input:"}
                      </span>
                      <p className="text-xs text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 rounded p-1.5 mt-0.5">
                        {action.input}
                      </p>
                    </div>
                  )}
                  {action.output && (
                    <div>
                      <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                        {isUrdu ? "آؤٹ پٹ:" : "Output:"}
                      </span>
                      <p className="text-xs text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 rounded p-1.5 mt-0.5">
                        {action.output}
                      </p>
                    </div>
                  )}
                  <div className="text-xs text-gray-400">
                    {new Date(action.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              )}
            </div>
          );
        })}
        
        {/* Empty state */}
        {(!currentTrace?.actions || currentTrace.actions.length === 0) && recentActions.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Activity className="w-10 h-10 mx-auto mb-2 opacity-50" />
            <p className="text-sm">
              {isUrdu ? "کوئی ایجنٹ سرگرمی نہیں" : "No agent activity yet"}
            </p>
            <p className="text-xs mt-1">
              {isUrdu ? "سوال پوچھیں یا مواد بنائیں" : "Ask a question or generate content to see agents in action"}
            </p>
          </div>
        )}
      </div>
      
      {/* Footer with summary */}
      {currentTrace?.summary && (
        <div className="p-2 border-t border-gray-200 dark:border-gray-700 bg-green-50 dark:bg-green-900/20">
          <p className="text-xs text-green-700 dark:text-green-400">
            ✨ {currentTrace.summary}
          </p>
        </div>
      )}
    </div>
  );
}
