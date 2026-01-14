"""
Agent Orchestrator
==================

Coordinates all agents and orchestrates the learning experience.
Receives student input and produces final response through agent pipeline.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.agents.agentic_system.student_profiler import StudentProfiler
from src.agents.agentic_system.curriculum_agent import CurriculumAgent
from src.agents.agentic_system.tutor_agent import TutorAgent
from src.agents.agentic_system.language_agent import LanguageAgent
from src.agents.agentic_system.safety_agent import SafetyAgent
from src.agents.agentic_system.learning_path_agent import LearningPathAgent


class AgentOrchestrator:
    """
    Master orchestrator that coordinates all agents.
    
    Flow:
    StudentInput → StudentProfiler → CurriculumAgent → TutorAgent 
                → LanguageAgent → SafetyAgent → LearningPathAgent → Response
    """

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        
        # Initialize all agents
        self.student_profiler = StudentProfiler(
            profile_dir=self.project_root / "data"
        )
        self.curriculum_agent = CurriculumAgent(
            curriculum_dir=self.project_root / "curriculum"
        )
        self.tutor_agent = TutorAgent()
        self.language_agent = LanguageAgent()
        self.safety_agent = SafetyAgent()
        self.learning_path_agent = LearningPathAgent()
        
        # Initialize logging
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.trace_log = self.logs_dir / "agent_trace.json"

    async def process_student_input(
        self,
        studentInput: str,
        studentId: Optional[str] = None,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Process student input through entire agent pipeline.
        
        Args:
            studentInput: Student's question or input
            studentId: Optional student ID (will use default if not provided)
            context: Optional additional context
        
        Returns:
            Final response with trace of all agent outputs
        """
        trace = {
            "timestamp": datetime.now().isoformat(),
            "studentInput": studentInput,
            "studentId": studentId or self.student_profiler.student_id,
            "agents": {},
        }
        
        try:
            # Step 1: Student Profiler
            profiler_output = await self._run_student_profiler(studentInput)
            trace["agents"]["studentProfiler"] = profiler_output
            
            # Step 2: Curriculum Agent
            curriculum_output = await self._run_curriculum_agent(
                profiler_output,
                context,
            )
            trace["agents"]["curriculumAgent"] = curriculum_output
            
            # Step 3: Tutor Agent
            tutor_output = await self._run_tutor_agent(
                studentInput,
                profiler_output,
                curriculum_output,
            )
            trace["agents"]["tutorAgent"] = tutor_output
            
            # Step 4: Language Agent
            language_output = await self._run_language_agent(
                tutor_output,
                profiler_output,
            )
            trace["agents"]["languageAgent"] = language_output
            
            # Step 5: Safety Agent
            safety_output = await self._run_safety_agent(
                language_output,
                profiler_output,
                curriculum_output,
            )
            trace["agents"]["safetyAgent"] = safety_output
            
            # Step 6: Learning Path Agent
            path_output = await self._run_learning_path_agent(
                profiler_output,
                curriculum_output,
            )
            trace["agents"]["learningPathAgent"] = path_output
            
            # Step 7: Compile final response
            final_response = await self._compile_final_response(
                trace,
                profiler_output,
            )
            
            trace["finalResponse"] = final_response
            trace["status"] = "success"
            
        except Exception as e:
            trace["status"] = "error"
            trace["error"] = str(e)
            final_response = {
                "status": "error",
                "message": "An error occurred processing your request",
                "error": str(e),
            }
        
        # Log the trace
        self._log_trace(trace)
        
        return {
            "response": final_response,
            "trace": trace,
        }

    async def _run_student_profiler(self, studentInput: str) -> Dict[str, Any]:
        """Run StudentProfiler agent."""
        analysis = self.student_profiler.analyze_input(studentInput)
        profile = self.student_profiler.get_student_summary()
        
        return {
            "inputAnalysis": analysis,
            "studentProfile": profile,
            "language": analysis.get("language"),
            "confidence": analysis.get("confidence"),
            "topic": analysis.get("topicOfInterest"),
        }

    async def _run_curriculum_agent(
        self,
        profilerOutput: Dict[str, Any],
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Run CurriculumAgent agent."""
        grade = profilerOutput["studentProfile"].get("grade")
        board = profilerOutput["studentProfile"].get("board")
        topic = profilerOutput.get("topic")
        
        if not grade or not topic:
            return {
                "error": "Missing grade or topic",
                "isValid": False,
            }
        
        # Get curriculum content
        curriculum = self.curriculum_agent.get_curriculum_for_student(grade, board)
        
        # Validate topic
        validation = self.curriculum_agent.validate_content(grade, "general", topic)
        
        # Get prerequisites
        prerequisites = self.curriculum_agent.get_prerequisites(grade, "general", topic)
        
        return {
            "isValid": validation.get("isValid"),
            "curriculum": curriculum,
            "topicValidation": validation,
            "prerequisites": prerequisites,
            "syllabus_compliant": validation.get("inSyllabus", False),
        }

    async def _run_tutor_agent(
        self,
        studentInput: str,
        profilerOutput: Dict[str, Any],
        curriculumOutput: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run TutorAgent agent."""
        difficulty = profilerOutput["inputAnalysis"].get("nextDifficulty", "intermediate")
        topic = profilerOutput.get("topic")
        
        if not curriculumOutput.get("isValid"):
            return {
                "error": "Invalid curriculum topic",
                "content": None,
            }
        
        # Generate explanation
        explanation = self.tutor_agent.generate_explanation(
            topic=topic,
            content=curriculumOutput.get("curriculum", {}),
            difficulty=difficulty,
        )
        
        # Generate practice question
        practice = self.tutor_agent.generate_practice_question(
            topic=topic,
            difficulty=difficulty,
        )
        
        return {
            "explanation": explanation,
            "practiceQuestion": practice,
            "difficulty": difficulty,
            "topicCovered": topic,
        }

    async def _run_language_agent(
        self,
        tutorOutput: Dict[str, Any],
        profilerOutput: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run LanguageAgent agent."""
        language = profilerOutput.get("language", "en")
        
        # Get explanation as text
        explanation_text = tutorOutput.get("explanation", {}).get("structure", "")
        
        # Translate/format for language
        multilingual_response = self.language_agent.generate_multilingual_response(
            explanation_text,
            language,
        )
        
        # Get cultural context
        cultural_context = self.language_agent.get_cultural_context(language)
        
        return {
            "language": language,
            "response": multilingual_response,
            "culturalContext": cultural_context,
            "direction": multilingual_response.get("direction"),
        }

    async def _run_safety_agent(
        self,
        languageOutput: Dict[str, Any],
        profilerOutput: Dict[str, Any],
        curriculumOutput: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run SafetyAgent agent."""
        grade = profilerOutput["studentProfile"].get("grade")
        language = languageOutput.get("language", "en")
        response_text = languageOutput.get("response", {}).get("content", "")
        topic = profilerOutput.get("topic")
        
        # Check content safety
        safety_check = self.safety_agent.check_content_safety(
            response_text,
            grade or 9,
            topic or "general",
        )
        
        # Filter response if needed
        filtered = self.safety_agent.filter_response(
            response_text,
            grade or 9,
            language,
        )
        
        return {
            "safetyCheck": safety_check,
            "filteredResponse": filtered.get("response"),
            "isSafe": safety_check.get("isSafe"),
            "safetyLevel": safety_check.get("safetyLevel"),
            "issues": safety_check.get("issues", []),
        }

    async def _run_learning_path_agent(
        self,
        profilerOutput: Dict[str, Any],
        curriculumOutput: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run LearningPathAgent agent."""
        grade = profilerOutput["studentProfile"].get("grade")
        topic = profilerOutput.get("topic")
        mastery = profilerOutput["studentProfile"].get("avgMastery", 0)
        
        if not grade or not topic:
            return {"error": "Missing grade or topic"}
        
        # Generate learning path
        path = self.learning_path_agent.generate_learning_path(
            grade=str(grade),
            subject="general",
            topic=topic,
            studentProfile=profilerOutput["studentProfile"],
            curriculum=curriculumOutput.get("curriculum", {}),
        )
        
        return {
            "learningPath": path,
            "stages": path.get("stages", []),
            "checkpoints": path.get("checkpoints", []),
            "estimatedDuration": path.get("estimatedDuration"),
        }

    async def _compile_final_response(
        self,
        trace: Dict[str, Any],
        profilerOutput: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compile all agent outputs into final response."""
        tutor = trace["agents"].get("tutorAgent", {})
        safety = trace["agents"].get("safetyAgent", {})
        language = trace["agents"].get("languageAgent", {})
        path = trace["agents"].get("learningPathAgent", {})
        
        # Build final response
        final = {
            "status": "success",
            "message": safety.get("filteredResponse", ""),
            "topic": profilerOutput.get("topic"),
            "explanation": tutor.get("explanation", {}),
            "practiceQuestion": tutor.get("practiceQuestion", {}),
            "learningPath": path.get("learningPath", {}),
            "language": language.get("language"),
            "difficulty": tutor.get("difficulty"),
            "nextSteps": self._generate_next_steps(trace),
            "studentProfile": profilerOutput.get("studentProfile"),
        }
        
        return final

    def _generate_next_steps(self, trace: Dict[str, Any]) -> List[str]:
        """Generate next steps for student."""
        learning_path = trace["agents"].get("learningPathAgent", {})
        stages = learning_path.get("stages", [])
        
        if not stages:
            return ["Review the explanation", "Try the practice question"]
        
        first_stage = stages[0]
        activities = first_stage.get("activities", [])
        
        next_steps = [f"Complete: {a.get('name')}" for a in activities[:2]]
        next_steps.append("Review learning checkpoints")
        
        return next_steps

    def _log_trace(self, trace: Dict[str, Any]) -> None:
        """Log trace of agent execution."""
        try:
            # Load existing traces
            traces = []
            if self.trace_log.exists():
                try:
                    traces = json.loads(self.trace_log.read_text())
                except:
                    traces = []
            
            # Add new trace
            traces.append(trace)
            
            # Keep last 1000 traces
            traces = traces[-1000:]
            
            # Save traces
            self.trace_log.write_text(json.dumps(traces, indent=2))
        except Exception as e:
            print(f"Error logging trace: {e}")

    def get_agent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent agent traces."""
        if not self.trace_log.exists():
            return []
        
        try:
            traces = json.loads(self.trace_log.read_text())
            return traces[-limit:]
        except:
            return []

    def get_trace_summary(self, studentId: str = None) -> Dict[str, Any]:
        """Get summary of agent traces."""
        traces = self.get_agent_traces(limit=100)
        
        if studentId:
            traces = [t for t in traces if t.get("studentId") == studentId]
        
        return {
            "totalTraces": len(traces),
            "successCount": sum(1 for t in traces if t.get("status") == "success"),
            "errorCount": sum(1 for t in traces if t.get("status") == "error"),
            "avgResponseTime": "N/A",  # Would calculate from timestamps
        }
