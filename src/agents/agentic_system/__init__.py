"""
Agentic System
==============

Multi-agent AI system for student learning.
Includes StudentProfiler, CurriculumAgent, TutorAgent, LanguageAgent,
SafetyAgent, LearningPathAgent, and Orchestrator.
"""

from src.agents.agentic_system.student_profiler import StudentProfiler
from src.agents.agentic_system.curriculum_agent import CurriculumAgent
from src.agents.agentic_system.tutor_agent import TutorAgent
from src.agents.agentic_system.language_agent import LanguageAgent
from src.agents.agentic_system.safety_agent import SafetyAgent
from src.agents.agentic_system.learning_path_agent import LearningPathAgent
from src.agents.agentic_system.orchestrator import AgentOrchestrator

__all__ = [
    "StudentProfiler",
    "CurriculumAgent",
    "TutorAgent",
    "LanguageAgent",
    "SafetyAgent",
    "LearningPathAgent",
    "AgentOrchestrator",
]
