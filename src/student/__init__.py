"""
Student Management Module
=========================

This module handles student profiles, progress tracking, and assessments.

Usage:
    from src.student import StudentManager, StudentProfile
    
    manager = StudentManager()
    profile = manager.create_student(name="Ali", grade=9, language="ur")
    progress = manager.get_progress(profile.student_id, "math_9_1_1")
"""

from .models import (
    StudentProfile,
    StudentProgress,
    Assessment,
    AssessmentQuestion,
    LearningPreferences,
)
from .manager import StudentManager, get_student_manager
from .assessment import AssessmentEngine, get_assessment_engine

__all__ = [
    "StudentProfile",
    "StudentProgress",
    "Assessment",
    "AssessmentQuestion",
    "LearningPreferences",
    "StudentManager",
    "get_student_manager",
    "AssessmentEngine",
    "get_assessment_engine",
]
