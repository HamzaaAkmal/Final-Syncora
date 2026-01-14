"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";
import { wsUrl } from "@/lib/api";

// ============================================================================
// Types
// ============================================================================

export interface AgentAction {
  id: string;
  agent: string;
  action: string;
  input?: string;
  output?: string;
  status: "pending" | "running" | "completed" | "error";
  duration_ms?: number;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface AgentTrace {
  trace_id: string;
  session_id: string;
  started_at: string;
  completed_at?: string;
  status: "running" | "completed" | "error";
  total_duration_ms?: number;
  actions: AgentAction[];
  current_agent?: string;
  summary?: string;
}

interface AgentTraceContextType {
  // Current trace data
  currentTrace: AgentTrace | null;
  allTraces: AgentTrace[];
  isConnected: boolean;
  
  // Real-time actions stream
  recentActions: AgentAction[];
  
  // Methods
  startNewTrace: (sessionId: string) => void;
  addAction: (action: Omit<AgentAction, "id" | "timestamp">) => string;
  updateAction: (actionId: string, updates: Partial<AgentAction>) => void;
  completeTrace: (summary?: string) => void;
  clearTraces: () => void;
  
  // UI state
  isTraceVisible: boolean;
  setTraceVisible: (visible: boolean) => void;
  isMinimized: boolean;
  setMinimized: (minimized: boolean) => void;
}

const AgentTraceContext = createContext<AgentTraceContextType | null>(null);

// ============================================================================
// Agent Trace Provider
// ============================================================================

export function AgentTraceProvider({ children }: { children: React.ReactNode }) {
  const [currentTrace, setCurrentTrace] = useState<AgentTrace | null>(null);
  const [allTraces, setAllTraces] = useState<AgentTrace[]>([]);
  const [recentActions, setRecentActions] = useState<AgentAction[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTraceVisible, setTraceVisible] = useState(false);
  const [isMinimized, setMinimized] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const actionIdCounter = useRef(0);
  
  // Generate unique action ID
  const generateActionId = useCallback(() => {
    actionIdCounter.current += 1;
    return `action_${Date.now()}_${actionIdCounter.current}`;
  }, []);
  
  // Connect to WebSocket for real-time agent updates
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(wsUrl("/ws/agent-trace"));
        wsRef.current = ws;
        
        ws.onopen = () => {
          console.log("[AgentTrace] WebSocket connected");
          setIsConnected(true);
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
          } catch (e) {
            console.error("[AgentTrace] Failed to parse message:", e);
          }
        };
        
        ws.onclose = () => {
          console.log("[AgentTrace] WebSocket disconnected");
          setIsConnected(false);
          // Reconnect after delay
          setTimeout(connectWebSocket, 3000);
        };
        
        ws.onerror = () => {
          console.warn("[AgentTrace] WebSocket connection error occurred");
          // Don't log the error object as it's not serializable
        };
      } catch (e) {
        console.error("[AgentTrace] Failed to connect WebSocket:", e);
        // Retry connection
        setTimeout(connectWebSocket, 5000);
      }
    };
    
    connectWebSocket();
    
    return () => {
      wsRef.current?.close();
    };
  }, []);
  
  // Handle incoming WebSocket messages
  const handleWebSocketMessage = useCallback((data: any) => {
    switch (data.type) {
      case "init":
        // Initialize with existing active traces
        if (data.traces && data.traces.length > 0) {
          const latestTrace = data.traces[0];
          setCurrentTrace({
            trace_id: latestTrace.id,
            session_id: latestTrace.context?.session_id || "unknown",
            started_at: latestTrace.started_at,
            status: latestTrace.status === "active" ? "running" : latestTrace.status,
            actions: latestTrace.actions?.map((a: any) => ({
              id: a.id,
              agent: a.agent,
              action: a.action,
              input: JSON.stringify(a.input),
              output: a.output ? JSON.stringify(a.output) : undefined,
              status: a.status === "started" ? "running" : a.status,
              duration_ms: a.duration_ms,
              timestamp: a.started_at,
            })) || [],
          });
          setTraceVisible(true);
        }
        break;
        
      case "trace_start":
        setCurrentTrace({
          trace_id: data.trace?.id,
          session_id: data.trace?.context?.session_id || "unknown",
          started_at: data.trace?.started_at || new Date().toISOString(),
          status: "running",
          actions: [],
        });
        setTraceVisible(true);
        break;
      
      case "trace_started":
        setCurrentTrace({
          trace_id: data.trace_id,
          session_id: data.session_id,
          started_at: data.timestamp || new Date().toISOString(),
          status: "running",
          actions: [],
        });
        setTraceVisible(true);
        break;
        
      case "action_start":
      case "action_started":
      case "agent_action":
        const newAction: AgentAction = {
          id: data.action?.id || data.action_id || generateActionId(),
          agent: data.action?.agent || data.agent,
          action: data.action?.action || data.action,
          input: data.action?.input ? JSON.stringify(data.action.input) : data.input,
          status: "running",
          timestamp: data.action?.started_at || data.timestamp || new Date().toISOString(),
          metadata: data.metadata,
        };
        
        setCurrentTrace(prev => {
          if (!prev) {
            // Create trace if not exists
            return {
              trace_id: data.trace_id || `trace_${Date.now()}`,
              session_id: "auto",
              started_at: new Date().toISOString(),
              status: "running",
              actions: [newAction],
              current_agent: newAction.agent,
            };
          }
          return {
            ...prev,
            current_agent: newAction.agent,
            actions: [...prev.actions, newAction],
          };
        });
        
        setRecentActions(prev => [newAction, ...prev].slice(0, 50));
        setTraceVisible(true);
        break;
        
      case "action_update":
        const updateStatus = data.status === "completed" ? "completed" : 
                           data.status === "error" ? "error" : 
                           data.status === "streaming" ? "running" : "running";
        
        setCurrentTrace(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            actions: prev.actions.map(a => 
              a.id === data.action_id 
                ? { 
                    ...a, 
                    status: updateStatus as AgentAction["status"], 
                    output: data.output ? JSON.stringify(data.output) : a.output, 
                    duration_ms: data.duration_ms 
                  }
                : a
            ),
          };
        });
        
        setRecentActions(prev => 
          prev.map(a => 
            a.id === data.action_id 
              ? { 
                  ...a, 
                  status: updateStatus as AgentAction["status"], 
                  output: data.output ? JSON.stringify(data.output) : a.output, 
                  duration_ms: data.duration_ms 
                }
              : a
          )
        );
        break;
        
      case "action_completed":
        setCurrentTrace(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            actions: prev.actions.map(a => 
              a.id === data.action_id 
                ? { ...a, status: "completed" as const, output: data.output, duration_ms: data.duration_ms }
                : a
            ),
          };
        });
        
        setRecentActions(prev => 
          prev.map(a => 
            a.id === data.action_id 
              ? { ...a, status: "completed" as const, output: data.output, duration_ms: data.duration_ms }
              : a
          )
        );
        break;
        
      case "action_error":
        setCurrentTrace(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            actions: prev.actions.map(a => 
              a.id === data.action_id 
                ? { ...a, status: "error" as const, output: data.error }
                : a
            ),
          };
        });
        break;
        
      case "trace_complete":
      case "trace_completed":
        setCurrentTrace(prev => {
          if (!prev) return prev;
          const completed = {
            ...prev,
            status: "completed" as const,
            completed_at: data.timestamp || new Date().toISOString(),
            total_duration_ms: data.duration_ms,
            summary: data.summary,
            current_agent: undefined,
          };
          setAllTraces(traces => [completed, ...traces].slice(0, 20));
          return completed;
        });
        break;
    }
  }, [generateActionId]);
  
  // Manual methods for local agent tracking (when WebSocket not available)
  const startNewTrace = useCallback((sessionId: string) => {
    const trace: AgentTrace = {
      trace_id: `trace_${Date.now()}`,
      session_id: sessionId,
      started_at: new Date().toISOString(),
      status: "running",
      actions: [],
    };
    setCurrentTrace(trace);
    setTraceVisible(true);
  }, []);
  
  const addAction = useCallback((action: Omit<AgentAction, "id" | "timestamp">) => {
    const newAction: AgentAction = {
      ...action,
      id: generateActionId(),
      timestamp: new Date().toISOString(),
    };
    
    setCurrentTrace(prev => {
      if (!prev) {
        // Auto-create trace if not exists
        return {
          trace_id: `trace_${Date.now()}`,
          session_id: "auto",
          started_at: new Date().toISOString(),
          status: "running",
          actions: [newAction],
          current_agent: action.agent,
        };
      }
      return {
        ...prev,
        current_agent: action.agent,
        actions: [...prev.actions, newAction],
      };
    });
    
    setRecentActions(prev => [newAction, ...prev].slice(0, 50));
    setTraceVisible(true);
    
    return newAction.id;
  }, [generateActionId]);
  
  const updateAction = useCallback((actionId: string, updates: Partial<AgentAction>) => {
    setCurrentTrace(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        actions: prev.actions.map(a => 
          a.id === actionId ? { ...a, ...updates } : a
        ),
      };
    });
    
    setRecentActions(prev => 
      prev.map(a => a.id === actionId ? { ...a, ...updates } : a)
    );
  }, []);
  
  const completeTrace = useCallback((summary?: string) => {
    setCurrentTrace(prev => {
      if (!prev) return prev;
      const completed = {
        ...prev,
        status: "completed" as const,
        completed_at: new Date().toISOString(),
        summary,
        current_agent: undefined,
      };
      setAllTraces(traces => [completed, ...traces].slice(0, 20));
      return completed;
    });
  }, []);
  
  const clearTraces = useCallback(() => {
    setAllTraces([]);
    setRecentActions([]);
  }, []);
  
  return (
    <AgentTraceContext.Provider
      value={{
        currentTrace,
        allTraces,
        isConnected,
        recentActions,
        startNewTrace,
        addAction,
        updateAction,
        completeTrace,
        clearTraces,
        isTraceVisible,
        setTraceVisible,
        isMinimized,
        setMinimized,
      }}
    >
      {children}
    </AgentTraceContext.Provider>
  );
}

// ============================================================================
// Hook
// ============================================================================

export function useAgentTrace() {
  const context = useContext(AgentTraceContext);
  if (!context) {
    throw new Error("useAgentTrace must be used within AgentTraceProvider");
  }
  return context;
}

// ============================================================================
// Simulated Agent Actions (for demo/testing)
// ============================================================================

export function useSimulatedAgentTrace() {
  const { addAction, updateAction, completeTrace, startNewTrace } = useAgentTrace();
  
  const simulateAgentFlow = useCallback(async (query: string) => {
    startNewTrace(`session_${Date.now()}`);
    
    // Manager Agent receives query
    const managerId = addAction({
      agent: "manager",
      action: "Analyzing request",
      input: query,
      status: "running",
    });
    await sleep(500);
    updateAction(managerId, { 
      status: "completed", 
      output: "Delegating to appropriate agents",
      duration_ms: 500 
    });
    
    // Safety Agent checks content
    const safetyId = addAction({
      agent: "safety",
      action: "Content safety check",
      input: query,
      status: "running",
    });
    await sleep(300);
    updateAction(safetyId, { 
      status: "completed", 
      output: "Content is safe for educational use",
      duration_ms: 300 
    });
    
    // Assessment Agent evaluates
    const assessmentId = addAction({
      agent: "assessment",
      action: "Evaluating student level",
      input: "Checking prior knowledge",
      status: "running",
    });
    await sleep(600);
    updateAction(assessmentId, { 
      status: "completed", 
      output: "Student level: Grade 9, Intermediate proficiency",
      duration_ms: 600 
    });
    
    // Content Agent generates
    const contentId = addAction({
      agent: "content",
      action: "Generating educational content",
      input: "Creating explanation for topic",
      status: "running",
    });
    await sleep(1000);
    updateAction(contentId, { 
      status: "completed", 
      output: "Content generated with examples and practice problems",
      duration_ms: 1000 
    });
    
    // Tutor Agent formats response
    const tutorId = addAction({
      agent: "tutor",
      action: "Formatting response",
      input: "Adapting content for student",
      status: "running",
    });
    await sleep(400);
    updateAction(tutorId, { 
      status: "completed", 
      output: "Response formatted with bilingual support",
      duration_ms: 400 
    });
    
    // Response Agent finalizes
    const responseId = addAction({
      agent: "response",
      action: "Finalizing answer",
      input: "Compiling final response",
      status: "running",
    });
    await sleep(300);
    updateAction(responseId, { 
      status: "completed", 
      output: "Answer ready for student",
      duration_ms: 300 
    });
    
    // Complete trace
    await sleep(200);
    completeTrace("Successfully processed educational query with multi-agent collaboration");
    
  }, [addAction, updateAction, completeTrace, startNewTrace]);
  
  return { simulateAgentFlow };
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
