"""
Agentic Chat Router
===================

API endpoints for the agentic AI student learning companion.
Integrates all agents through the orchestrator.
"""

import uuid
from pathlib import Path
import sys
import asyncio
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel

_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

from src.agents.agentic_system import AgentOrchestrator
from src.services.agent_trace_logger import AgentTraceLogger
from src.services.system_prompt import SystemPromptService
from src.logging import get_logger

# Initialize logger
project_root = Path(__file__).parent.parent.parent.parent
logger = get_logger("AgenticChatAPI", level="INFO")

router = APIRouter()

# Initialize orchestrator and logger (with fallback)
try:
    orchestrator = AgentOrchestrator(project_root=project_root)
    trace_logger = AgentTraceLogger(logs_dir=project_root / "logs")
except Exception as e:
    logger.warning(f"Failed to initialize agentic system at module load: {e}")
    orchestrator = None
    trace_logger = None


# =============================================================================
# Pydantic Models
# =============================================================================

class AgenticMessageRequest(BaseModel):
    """Request model for agentic chat."""
    message: str
    student_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AgenticResponse(BaseModel):
    """Response model for agentic chat."""
    response: Dict[str, Any]
    trace: Dict[str, Any]
    status: str


class AgentTraceRequest(BaseModel):
    """Request for retrieving traces."""
    student_id: Optional[str] = None
    limit: int = 20


# =============================================================================
# Main Agentic Chat Endpoint
# =============================================================================

@router.post("/agentic/chat")
async def agentic_chat(request: AgenticMessageRequest):
    """
    Process student message through entire agentic system.
    
    Flow:
    1. StudentProfiler analyzes input
    2. CurriculumAgent validates curriculum
    3. TutorAgent generates explanation
    4. LanguageAgent adapts language
    5. SafetyAgent checks safety
    6. LearningPathAgent creates path
    7. Log complete trace
    """
    try:
        if orchestrator is None:
            raise HTTPException(status_code=503, detail="Agentic system not available")
        
        # Get system prompt
        system_prompt = SystemPromptService.get_master_prompt()
        
        logger.info(f"Received agentic chat request: {request.message[:100]}")
        
        # Process through orchestrator
        result = await orchestrator.process_student_input(
            studentInput=request.message,
            studentId=request.student_id,
            context=request.context,
        )
        
        logger.info(f"Agentic chat processed successfully for student {request.student_id}")
        
        return AgenticResponse(
            response=result["response"],
            trace=result["trace"],
            status="success",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agentic chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# WebSocket for Real-time Agentic Chat
# =============================================================================

@router.websocket("/agentic/chat/{session_id}")
async def websocket_agentic_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming agentic responses."""
    await websocket.accept()
    
    try:
        if orchestrator is None:
            await websocket.send_json({
                "status": "error",
                "detail": "Agentic system not available"
            })
            await websocket.close(code=1008)
            return
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            student_message = data.get("message", "")
            student_id = data.get("student_id")
            
            logger.info(f"WebSocket agentic message from {student_id}: {student_message[:100]}")
            
            # Process through orchestrator
            try:
                result = await orchestrator.process_student_input(
                    studentInput=student_message,
                    studentId=student_id,
                    context=data.get("context"),
                )
                
                # Send response back
                await websocket.send_json({
                    "status": "success",
                    "response": result["response"],
                    "trace_summary": {
                        "studentProfiler": result["trace"]["agents"].get("studentProfiler", {}),
                        "curriculumAgent": result["trace"]["agents"].get("curriculumAgent", {}),
                        "tutorAgent": result["trace"]["agents"].get("tutorAgent", {}),
                        "languageAgent": result["trace"]["agents"].get("languageAgent", {}),
                        "safetyAgent": result["trace"]["agents"].get("safetyAgent", {}),
                        "learningPathAgent": result["trace"]["agents"].get("learningPathAgent", {}),
                    },
                })
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                await websocket.send_json({
                    "status": "error",
                    "message": str(e),
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")


# =============================================================================
# Agent Trace Endpoints
# =============================================================================

@router.get("/agentic/traces")
async def get_traces(
    student_id: Optional[str] = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
):
    """Get agent execution traces."""
    try:
        traces = trace_logger.get_traces(
            studentId=student_id,
            limit=limit,
            offset=offset,
        )
        
        return {
            "status": "success",
            "count": len(traces),
            "traces": traces,
        }
    except Exception as e:
        logger.error(f"Error retrieving traces: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agentic/traces/{trace_id}")
async def get_trace_detail(trace_id: str):
    """Get detailed agent collaboration report for a specific trace."""
    try:
        report = trace_logger.get_agent_collaboration_report(trace_id)
        return {
            "status": "success",
            "report": report,
        }
    except Exception as e:
        logger.error(f"Error retrieving trace detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agentic/traces/student/{student_id}")
async def get_student_learning_trace(student_id: str):
    """Get complete learning trace for a student."""
    try:
        learning_trace = trace_logger.get_student_learning_trace(student_id)
        return {
            "status": "success",
            "trace": learning_trace,
        }
    except Exception as e:
        logger.error(f"Error retrieving student trace: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agentic/statistics")
async def get_agent_statistics():
    """Get system-wide agent statistics."""
    try:
        stats = trace_logger.get_agent_statistics()
        return {
            "status": "success",
            "statistics": stats,
        }
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agentic/export/traces")
async def export_traces_csv(student_id: Optional[str] = Query(None)):
    """Export traces as CSV."""
    try:
        csv_data = trace_logger.export_traces_csv(student_id=student_id)
        return {
            "status": "success",
            "format": "csv",
            "data": csv_data,
        }
    except Exception as e:
        logger.error(f"Error exporting traces: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# System Configuration Endpoints
# =============================================================================

@router.get("/agentic/system/prompt")
async def get_system_prompt():
    """Get master system prompt."""
    try:
        return {
            "status": "success",
            "prompt": SystemPromptService.get_master_prompt(),
        }
    except Exception as e:
        logger.error(f"Error retrieving system prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agentic/system/context")
async def get_system_context():
    """Get system context."""
    try:
        return {
            "status": "success",
            "context": SystemPromptService.get_system_context(),
        }
    except Exception as e:
        logger.error(f"Error retrieving system context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agentic/system/quick-reference")
async def get_quick_reference():
    """Get quick reference guide."""
    try:
        return {
            "status": "success",
            "reference": SystemPromptService.get_quick_reference(),
        }
    except Exception as e:
        logger.error(f"Error retrieving quick reference: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Student Profile Endpoints
# =============================================================================

@router.get("/agentic/student/{student_id}/profile")
async def get_student_profile(student_id: str):
    """Get student profile."""
    try:
        profile = orchestrator.student_profiler.load_profile()
        return {
            "status": "success",
            "profile": profile,
        }
    except Exception as e:
        logger.error(f"Error retrieving student profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agentic/student/{student_id}/profile")
async def update_student_profile(student_id: str, updates: Dict[str, Any]):
    """Update student profile."""
    try:
        updated_profile = orchestrator.student_profiler.update_profile(**updates)
        return {
            "status": "success",
            "profile": updated_profile,
        }
    except Exception as e:
        logger.error(f"Error updating student profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Curriculum Endpoints
# =============================================================================

@router.get("/agentic/curriculum/subjects")
async def get_curriculum_subjects(grade: Optional[str] = None):
    """Get available curriculum subjects."""
    try:
        curriculum = orchestrator.curriculum_agent.get_curriculum_for_student(
            grade=grade or "9",
        )
        return {
            "status": "success",
            "subjects": list(curriculum.keys()),
            "curriculum": curriculum,
        }
    except Exception as e:
        logger.error(f"Error retrieving subjects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agentic/curriculum/topic/{grade}/{subject}/{topic}")
async def get_topic_content(grade: str, subject: str, topic: str):
    """Get curriculum content for a topic."""
    try:
        content = orchestrator.curriculum_agent.get_topic_content(
            grade=grade,
            subject=subject,
            topic=topic,
        )
        validation = orchestrator.curriculum_agent.validate_content(
            grade=grade,
            subject=subject,
            topic=topic,
        )
        
        return {
            "status": "success",
            "content": content,
            "validation": validation,
        }
    except Exception as e:
        logger.error(f"Error retrieving topic content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Audit & Monitoring Endpoints
# =============================================================================

@router.get("/agentic/audit/log")
async def get_audit_log():
    """Get agent activity audit log."""
    try:
        audit_log = trace_logger.create_agent_audit_log()
        return {
            "status": "success",
            "audit_log": audit_log,
        }
    except Exception as e:
        logger.error(f"Error generating audit log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agentic/health")
async def health_check():
    """Health check for agentic system."""
    try:
        return {
            "status": "healthy",
            "timestamp": str(Path(__file__).parent.parent.parent),
            "orchestrator": "active",
            "trace_logger": "active",
            "agents": [
                "StudentProfiler",
                "CurriculumAgent",
                "TutorAgent",
                "LanguageAgent",
                "SafetyAgent",
                "LearningPathAgent",
            ],
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
