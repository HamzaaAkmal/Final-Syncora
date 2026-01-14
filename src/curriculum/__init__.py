"""
Curriculum Management Module
============================

This module provides curriculum structure, alignment, and management
for the Pakistan education system including:
- Punjab Curriculum (PCTB)
- Sindh Curriculum
- National Curriculum

Usage:
    from src.curriculum import CurriculumManager, Subject, Topic
    
    manager = CurriculumManager()
    subjects = manager.get_subjects(grade=9)
    topics = manager.get_topics(subject_id="math", grade=9)
"""

from .models import (
    Subject,
    Topic,
    Chapter,
    LearningObjective,
    CurriculumBoard,
    GradeLevel,
)
from .manager import CurriculumManager, get_curriculum_manager
from .data import CURRICULUM_DATA

__all__ = [
    "Subject",
    "Topic",
    "Chapter",
    "LearningObjective",
    "CurriculumBoard",
    "GradeLevel",
    "CurriculumManager",
    "get_curriculum_manager",
    "CURRICULUM_DATA",
]
