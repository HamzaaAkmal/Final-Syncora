"""
Agent Trace Broadcaster - Manages WebSocket broadcasting of agent activities

Enables real-time visualization of multi-agent collaboration during chat and solve operations.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from fastapi import WebSocket
from enum import Enum


class AgentType(str, Enum):
    MANAGER = "manager"
    ASSESSMENT = "assessment"
    CONTENT = "content"
    TUTOR = "tutor"
    SOLVE = "solve"
    SAFETY = "safety"
    RESEARCH = "research"
    RESPONSE = "response"


class ActionStatus(str, Enum):
    STARTED = "started"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"


class AgentTraceBroadcaster:
    """
    Singleton broadcaster for agent trace events.
    Manages WebSocket connections and broadcasts agent activities in real-time.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._connections: set[WebSocket] = set()
        self._active_traces: Dict[str, dict] = {}  # trace_id -> trace data
        self._lock = asyncio.Lock()
        self._initialized = True
    
    async def connect(self, websocket: WebSocket):
        """Connect a new WebSocket client"""
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        print(f"[AgentTrace] WebSocket connected. Total: {len(self._connections)}")
        
        # Send current active traces to new connection
        if self._active_traces:
            try:
                await websocket.send_json({
                    "type": "init",
                    "traces": list(self._active_traces.values())
                })
            except Exception as e:
                print(f"[AgentTrace] Error sending init: {e}")
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        async with self._lock:
            self._connections.discard(websocket)
        print(f"[AgentTrace] WebSocket disconnected. Total: {len(self._connections)}")
    
    async def _broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self._connections:
            return
        
        to_remove = []
        async with self._lock:
            connections = list(self._connections)
        
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                print(f"[AgentTrace] Error broadcasting: {e}")
                to_remove.append(ws)
        
        if to_remove:
            async with self._lock:
                for ws in to_remove:
                    self._connections.discard(ws)
    
    def start_trace(self, trace_id: str, query: str, context: Optional[dict] = None) -> dict:
        """Start a new agent trace session"""
        trace = {
            "id": trace_id,
            "query": query,
            "context": context or {},
            "started_at": datetime.now().isoformat(),
            "status": "active",
            "actions": []
        }
        self._active_traces[trace_id] = trace
        
        asyncio.create_task(self._broadcast({
            "type": "trace_start",
            "trace": trace
        }))
        
        return trace
    
    def add_action(
        self,
        trace_id: str,
        action_id: str,
        agent: AgentType,
        action_type: str,
        description: str,
        input_data: Optional[dict] = None
    ) -> Optional[dict]:
        """Add a new action to a trace"""
        if trace_id not in self._active_traces:
            return None
        
        action = {
            "id": action_id,
            "agent": agent.value if isinstance(agent, AgentType) else agent,
            "action": action_type,
            "description": description,
            "input": input_data,
            "output": None,
            "status": ActionStatus.STARTED.value,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "duration_ms": None
        }
        
        self._active_traces[trace_id]["actions"].append(action)
        
        asyncio.create_task(self._broadcast({
            "type": "action_start",
            "trace_id": trace_id,
            "action": action
        }))
        
        return action
    
    def update_action(
        self,
        trace_id: str,
        action_id: str,
        status: Optional[ActionStatus] = None,
        output: Optional[Any] = None,
        streaming_content: Optional[str] = None
    ):
        """Update an existing action"""
        if trace_id not in self._active_traces:
            return
        
        trace = self._active_traces[trace_id]
        for action in trace["actions"]:
            if action["id"] == action_id:
                if status:
                    action["status"] = status.value if isinstance(status, ActionStatus) else status
                if output is not None:
                    action["output"] = output
                if status in [ActionStatus.COMPLETED, ActionStatus.ERROR]:
                    action["completed_at"] = datetime.now().isoformat()
                    # Calculate duration
                    if action.get("started_at"):
                        start = datetime.fromisoformat(action["started_at"])
                        end = datetime.now()
                        action["duration_ms"] = int((end - start).total_seconds() * 1000)
                
                asyncio.create_task(self._broadcast({
                    "type": "action_update",
                    "trace_id": trace_id,
                    "action_id": action_id,
                    "status": action["status"],
                    "output": output,
                    "streaming_content": streaming_content,
                    "duration_ms": action.get("duration_ms")
                }))
                break
    
    def complete_trace(self, trace_id: str, result: Optional[Any] = None):
        """Complete a trace session"""
        if trace_id not in self._active_traces:
            return
        
        trace = self._active_traces[trace_id]
        trace["status"] = "completed"
        trace["completed_at"] = datetime.now().isoformat()
        trace["result"] = result
        
        # Calculate total duration
        start = datetime.fromisoformat(trace["started_at"])
        end = datetime.now()
        trace["total_duration_ms"] = int((end - start).total_seconds() * 1000)
        
        asyncio.create_task(self._broadcast({
            "type": "trace_complete",
            "trace_id": trace_id,
            "result": result,
            "total_duration_ms": trace["total_duration_ms"]
        }))
        
        # Keep trace for a while then remove
        asyncio.create_task(self._cleanup_trace(trace_id, delay=60))
    
    async def _cleanup_trace(self, trace_id: str, delay: int = 60):
        """Remove completed trace after delay"""
        await asyncio.sleep(delay)
        self._active_traces.pop(trace_id, None)
    
    def get_active_traces(self) -> List[dict]:
        """Get all active traces"""
        return list(self._active_traces.values())


# Global singleton instance
agent_trace_broadcaster = AgentTraceBroadcaster()


# Convenience functions for use throughout the codebase
def emit_trace_start(trace_id: str, query: str, context: Optional[dict] = None) -> dict:
    """Start a new agent trace"""
    return agent_trace_broadcaster.start_trace(trace_id, query, context)


def emit_action_start(
    trace_id: str,
    action_id: str,
    agent: str,
    action_type: str,
    description: str,
    input_data: Optional[dict] = None
) -> Optional[dict]:
    """Emit an action start event"""
    return agent_trace_broadcaster.add_action(
        trace_id, action_id, agent, action_type, description, input_data
    )


def emit_action_update(
    trace_id: str,
    action_id: str,
    status: str = None,
    output: Any = None,
    streaming_content: str = None
):
    """Update an action's status or output"""
    status_enum = ActionStatus(status) if status else None
    agent_trace_broadcaster.update_action(
        trace_id, action_id, status_enum, output, streaming_content
    )


def emit_action_complete(trace_id: str, action_id: str, output: Any = None):
    """Mark an action as completed"""
    emit_action_update(trace_id, action_id, "completed", output)


def emit_action_error(trace_id: str, action_id: str, error: str):
    """Mark an action as errored"""
    emit_action_update(trace_id, action_id, "error", {"error": error})


def emit_trace_complete(trace_id: str, result: Any = None):
    """Complete a trace session"""
    agent_trace_broadcaster.complete_trace(trace_id, result)
