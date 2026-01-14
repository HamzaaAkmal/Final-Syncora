"""
Curriculum Data Models
======================

Defines the data structures for curriculum management.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class CurriculumBoard(str, Enum):
    """Pakistan curriculum boards."""
    NATIONAL = "national"
    PUNJAB = "punjab"  # PCTB
    SINDH = "sindh"
    KPK = "kpk"
    BALOCHISTAN = "balochistan"
    FEDERAL = "federal"


class GradeLevel(int, Enum):
    """Grade levels (1-12)."""
    GRADE_1 = 1
    GRADE_2 = 2
    GRADE_3 = 3
    GRADE_4 = 4
    GRADE_5 = 5
    GRADE_6 = 6
    GRADE_7 = 7
    GRADE_8 = 8
    GRADE_9 = 9
    GRADE_10 = 10
    GRADE_11 = 11
    GRADE_12 = 12


class DifficultyLevel(str, Enum):
    """Question/content difficulty levels."""
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ADVANCED = "advanced"


@dataclass
class LearningObjective:
    """A specific learning objective within a topic."""
    id: str
    description: str
    description_ur: str  # Urdu translation
    bloom_level: str  # remember, understand, apply, analyze, evaluate, create
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "description_ur": self.description_ur,
            "bloom_level": self.bloom_level,
            "keywords": self.keywords,
        }


@dataclass
class Topic:
    """A topic within a chapter."""
    id: str
    name: str
    name_ur: str  # Urdu name
    chapter_id: str
    subject_id: str
    grade: int
    order: int  # Order within the chapter
    description: str = ""
    description_ur: str = ""
    objectives: List[LearningObjective] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)  # Topic IDs
    estimated_hours: float = 1.0
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ur": self.name_ur,
            "chapter_id": self.chapter_id,
            "subject_id": self.subject_id,
            "grade": self.grade,
            "order": self.order,
            "description": self.description,
            "description_ur": self.description_ur,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "prerequisites": self.prerequisites,
            "estimated_hours": self.estimated_hours,
            "difficulty": self.difficulty.value,
            "keywords": self.keywords,
        }


@dataclass
class Chapter:
    """A chapter within a subject."""
    id: str
    name: str
    name_ur: str  # Urdu name
    subject_id: str
    grade: int
    order: int  # Chapter number/order
    description: str = ""
    description_ur: str = ""
    topics: List[Topic] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ur": self.name_ur,
            "subject_id": self.subject_id,
            "grade": self.grade,
            "order": self.order,
            "description": self.description,
            "description_ur": self.description_ur,
            "topics": [topic.to_dict() for topic in self.topics],
        }


@dataclass
class Subject:
    """A subject/course in the curriculum."""
    id: str
    name: str
    name_ur: str  # Urdu name
    board: CurriculumBoard = CurriculumBoard.NATIONAL
    grades: List[int] = field(default_factory=list)  # Grades where this subject is taught
    description: str = ""
    description_ur: str = ""
    icon: str = "📚"  # Emoji icon for UI
    chapters: Dict[int, List[Chapter]] = field(default_factory=dict)  # Grade -> Chapters
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ur": self.name_ur,
            "board": self.board.value,
            "grades": self.grades,
            "description": self.description,
            "description_ur": self.description_ur,
            "icon": self.icon,
        }


@dataclass
class StudentProgress:
    """Tracks student progress on a topic."""
    student_id: str
    topic_id: str
    status: str  # not_started, in_progress, completed, mastered
    mastery_level: float  # 0.0 to 1.0
    attempts: int = 0
    correct_answers: int = 0
    time_spent_minutes: int = 0
    last_accessed: Optional[datetime] = None
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "topic_id": self.topic_id,
            "status": self.status,
            "mastery_level": self.mastery_level,
            "attempts": self.attempts,
            "correct_answers": self.correct_answers,
            "time_spent_minutes": self.time_spent_minutes,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "notes": self.notes,
        }


@dataclass
class AssessmentResult:
    """Result of a student assessment."""
    id: str
    student_id: str
    topic_id: str
    assessment_type: str  # pre_assessment, practice, quiz, test
    score: float  # 0.0 to 1.0
    questions_total: int
    questions_correct: int
    time_taken_seconds: int
    created_at: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "topic_id": self.topic_id,
            "assessment_type": self.assessment_type,
            "score": self.score,
            "questions_total": self.questions_total,
            "questions_correct": self.questions_correct,
            "time_taken_seconds": self.time_taken_seconds,
            "created_at": self.created_at.isoformat(),
            "details": self.details,
        }
