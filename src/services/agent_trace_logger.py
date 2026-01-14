"""
Agent Trace Logger
==================

Comprehensive logging for agent interactions and collaboration.
Tracks the complete flow of student requests through the agent system.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class AgentTraceLogger:
    """Logs and retrieves agent execution traces."""

    def __init__(self, logs_dir: Path = None):
        self.logs_dir = logs_dir or Path(__file__).parent.parent / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.trace_log = self.logs_dir / "agent_trace.json"
        self.analytics_log = self.logs_dir / "agent_analytics.json"

    def log_trace(self, trace: Dict[str, Any]) -> None:
        """Log a complete agent trace."""
        try:
            # Load existing traces
            traces = self._load_traces()
            
            # Add new trace
            traces.append({
                **trace,
                "log_timestamp": datetime.now().isoformat(),
            })
            
            # Keep last 5000 traces
            traces = traces[-5000:]
            
            # Save traces
            self.trace_log.write_text(json.dumps(traces, indent=2))
        except Exception as e:
            print(f"Error logging trace: {e}")

    def _load_traces(self) -> List[Dict[str, Any]]:
        """Load traces from file."""
        if not self.trace_log.exists():
            return []
        
        try:
            return json.loads(self.trace_log.read_text())
        except:
            return []

    def get_traces(
        self,
        studentId: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get traces with optional filtering."""
        traces = self._load_traces()
        
        if studentId:
            traces = [t for t in traces if t.get("studentId") == studentId]
        
        # Sort by timestamp descending
        traces.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return traces[offset:offset + limit]

    def get_trace(self, traceId: str) -> Optional[Dict[str, Any]]:
        """Get a specific trace by ID."""
        traces = self._load_traces()
        for trace in traces:
            if trace.get("timestamp") == traceId:
                return trace
        return None

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get statistics about agent execution."""
        traces = self._load_traces()
        
        if not traces:
            return {
                "totalTraces": 0,
                "successRate": 0,
                "avgResponseTime": 0,
                "agentStats": {},
            }
        
        success_count = sum(1 for t in traces if t.get("status") == "success")
        error_count = sum(1 for t in traces if t.get("status") == "error")
        
        agent_names = [
            "studentProfiler",
            "curriculumAgent",
            "tutorAgent",
            "languageAgent",
            "safetyAgent",
            "learningPathAgent",
        ]
        
        agent_stats = {}
        for agent in agent_names:
            agent_traces = [t for t in traces if agent in t.get("agents", {})]
            agent_stats[agent] = {
                "executionCount": len(agent_traces),
                "successCount": len([t for t in agent_traces if not t.get("agents", {}).get(agent, {}).get("error")]),
            }
        
        return {
            "totalTraces": len(traces),
            "successCount": success_count,
            "errorCount": error_count,
            "successRate": (success_count / len(traces) * 100) if traces else 0,
            "agentStats": agent_stats,
        }

    def get_student_learning_trace(self, studentId: str) -> Dict[str, Any]:
        """Get learning trace for a specific student."""
        traces = self.get_traces(studentId=studentId, limit=1000)
        
        topics_covered = set()
        total_interactions = 0
        accuracy_scores = []
        
        for trace in traces:
            total_interactions += 1
            
            topic = trace.get("agents", {}).get("studentProfiler", {}).get("topic")
            if topic:
                topics_covered.add(topic)
            
            # Extract accuracy if available
            # This is a placeholder for extracting accuracy data
        
        return {
            "studentId": studentId,
            "totalInteractions": total_interactions,
            "topicsCovered": list(topics_covered),
            "recentTraces": traces[:10],
            "learningTrend": "improving" if total_interactions > 5 else "initializing",
        }

    def export_traces_csv(self, studentId: Optional[str] = None) -> str:
        """Export traces in CSV format."""
        traces = self.get_traces(studentId=studentId, limit=10000)
        
        csv_lines = [
            "timestamp,studentId,topic,difficulty,language,status"
        ]
        
        for trace in traces:
            profiler = trace.get("agents", {}).get("studentProfiler", {})
            csv_lines.append(
                f"{trace.get('timestamp')},"
                f"{trace.get('studentId')},"
                f"{profiler.get('topic', 'N/A')},"
                f"{profiler.get('inputAnalysis', {}).get('nextDifficulty', 'N/A')},"
                f"{profiler.get('language', 'N/A')},"
                f"{trace.get('status', 'N/A')}"
            )
        
        return "\n".join(csv_lines)

    def get_agent_collaboration_report(self, traceId: str) -> Dict[str, Any]:
        """Get detailed report of agent collaboration for a trace."""
        trace = self.get_trace(traceId)
        if not trace:
            return {"error": "Trace not found"}
        
        agents = trace.get("agents", {})
        
        return {
            "timestamp": trace.get("timestamp"),
            "studentId": trace.get("studentId"),
            "studentInput": trace.get("studentInput"),
            "agentFlow": [
                {
                    "agent": "StudentProfiler",
                    "output": agents.get("studentProfiler"),
                    "nextAgent": "CurriculumAgent",
                },
                {
                    "agent": "CurriculumAgent",
                    "output": agents.get("curriculumAgent"),
                    "nextAgent": "TutorAgent",
                },
                {
                    "agent": "TutorAgent",
                    "output": agents.get("tutorAgent"),
                    "nextAgent": "LanguageAgent",
                },
                {
                    "agent": "LanguageAgent",
                    "output": agents.get("languageAgent"),
                    "nextAgent": "SafetyAgent",
                },
                {
                    "agent": "SafetyAgent",
                    "output": agents.get("safetyAgent"),
                    "nextAgent": "LearningPathAgent",
                },
                {
                    "agent": "LearningPathAgent",
                    "output": agents.get("learningPathAgent"),
                    "nextAgent": "Response",
                },
            ],
            "finalResponse": trace.get("finalResponse"),
            "status": trace.get("status"),
        }

    def create_agent_audit_log(self) -> str:
        """Create audit log of all agent activity."""
        traces = self._load_traces()
        
        audit_lines = [
            "=== AGENT EXECUTION AUDIT LOG ===",
            f"Generated: {datetime.now().isoformat()}",
            f"Total Traces: {len(traces)}",
            "",
            "AGENT STATISTICS:",
        ]
        
        stats = self.get_agent_statistics()
        for agent, data in stats.get("agentStats", {}).items():
            audit_lines.append(
                f"  {agent}: {data['executionCount']} executions, "
                f"{data.get('successCount', 0)} successful"
            )
        
        audit_lines.extend([
            "",
            "RECENT ACTIVITY:",
        ])
        
        recent = self.get_traces(limit=20)
        for trace in recent:
            audit_lines.append(
                f"  [{trace.get('timestamp')}] Student {trace.get('studentId')}: "
                f"Topic {trace.get('agents', {}).get('studentProfiler', {}).get('topic')} - "
                f"{trace.get('status')}"
            )
        
        return "\n".join(audit_lines)
