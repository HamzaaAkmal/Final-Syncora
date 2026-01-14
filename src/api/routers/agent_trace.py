"""
Agent Trace WebSocket Router

Provides WebSocket endpoint for real-time agent activity streaming.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.utils.agent_trace_broadcaster import agent_trace_broadcaster

router = APIRouter(tags=["agent-trace"])


@router.websocket("/ws/agent-trace")
async def agent_trace_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent trace updates.
    
    Clients connect to receive live updates about:
    - Agent actions during chat/solve operations
    - Multi-agent collaboration events
    - Processing status and results
    
    Message types:
    - init: Current active traces on connection
    - trace_start: New trace session started
    - action_start: Agent started an action
    - action_update: Action status/output updated
    - trace_complete: Trace session completed
    """
    await agent_trace_broadcaster.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            
            # Handle ping/pong for keep-alive
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        await agent_trace_broadcaster.disconnect(websocket)
    except Exception as e:
        print(f"[AgentTrace WS] Error: {e}")
        await agent_trace_broadcaster.disconnect(websocket)


@router.get("/api/v1/agent-trace/active")
async def get_active_traces():
    """Get all currently active agent traces."""
    return {
        "traces": agent_trace_broadcaster.get_active_traces(),
        "count": len(agent_trace_broadcaster.get_active_traces())
    }
