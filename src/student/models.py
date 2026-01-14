"""
Student Data Models
===================

Data models for student profiles, progress tracking, and assessments.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid


class LanguagePreference(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    URDU = "ur"
    PUNJABI = "pa"
    SINDHI = "sd"


class LearningStyle(str, Enum):
    """Learning style preferences."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    READING_WRITING = "reading_writing"
    KINESTHETIC = "kinesthetic"


class MasteryLevel(str, Enum):
    """Topic mastery levels."""
    NOT_STARTED = "not_started"
    BEGINNER = "beginner"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    MASTERED = "mastered"


class AssessmentType(str, Enum):
    """Types of assessments."""
    PRE_ASSESSMENT = "pre_assessment"
    PRACTICE = "practice"
    QUIZ = "quiz"
    TEST = "test"
    CHECKPOINT = "checkpoint"


@dataclass
class LearningPreferences:
    """Student learning preferences."""
    style: LearningStyle = LearningStyle.VISUAL
    pace: str = "normal"  # slow, normal, fast
    difficulty_preference: str = "adaptive"  # easy, medium, hard, adaptive
    hints_enabled: bool = True
    explanations_detailed: bool = True
    audio_enabled: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "style": self.style.value,
            "pace": self.pace,
            "difficulty_preference": self.difficulty_preference,
            "hints_enabled": self.hints_enabled,
            "explanations_detailed": self.explanations_detailed,
            "audio_enabled": self.audio_enabled,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningPreferences":
        return cls(
            style=LearningStyle(data.get("style", "visual")),
            pace=data.get("pace", "normal"),
            difficulty_preference=data.get("difficulty_preference", "adaptive"),
            hints_enabled=data.get("hints_enabled", True),
            explanations_detailed=data.get("explanations_detailed", True),
            audio_enabled=data.get("audio_enabled", False),
        )


@dataclass
class StudentProfile:
    """Complete student profile."""
    student_id: str
    name: str
    name_ur: str = ""  # Name in Urdu
    grade: int = 9
    board: str = "punjab"  # Curriculum board
    language: LanguagePreference = LanguagePreference.URDU
    subjects: List[str] = field(default_factory=list)  # Enrolled subjects
    preferences: LearningPreferences = field(default_factory=LearningPreferences)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    # Progress tracking
    total_time_minutes: int = 0
    topics_completed: int = 0
    topics_in_progress: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    points: int = 0
    badges: List[str] = field(default_factory=list)
    
    # Knowledge gaps and strengths
    weak_topics: List[str] = field(default_factory=list)
    strong_topics: List[str] = field(default_factory=list)
    recommended_topics: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "name_ur": self.name_ur,
            "grade": self.grade,
            "board": self.board,
            "language": self.language.value,
            "subjects": self.subjects,
            "preferences": self.preferences.to_dict(),
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "total_time_minutes": self.total_time_minutes,
            "topics_completed": self.topics_completed,
            "topics_in_progress": self.topics_in_progress,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "points": self.points,
            "badges": self.badges,
            "weak_topics": self.weak_topics,
            "strong_topics": self.strong_topics,
            "recommended_topics": self.recommended_topics,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentProfile":
        return cls(
            student_id=data.get("student_id", str(uuid.uuid4())),
            name=data.get("name", "Student"),
            name_ur=data.get("name_ur", ""),
            grade=data.get("grade", 9),
            board=data.get("board", "punjab"),
            language=LanguagePreference(data.get("language", "ur")),
            subjects=data.get("subjects", []),
            preferences=LearningPreferences.from_dict(data.get("preferences", {})),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            last_active=datetime.fromisoformat(data["last_active"]) if "last_active" in data else datetime.now(),
            total_time_minutes=data.get("total_time_minutes", 0),
            topics_completed=data.get("topics_completed", 0),
            topics_in_progress=data.get("topics_in_progress", 0),
            current_streak=data.get("current_streak", 0),
            longest_streak=data.get("longest_streak", 0),
            points=data.get("points", 0),
            badges=data.get("badges", []),
            weak_topics=data.get("weak_topics", []),
            strong_topics=data.get("strong_topics", []),
            recommended_topics=data.get("recommended_topics", []),
        )


@dataclass
class StudentProgress:
    """Progress on a specific topic."""
    id: str
    student_id: str
    topic_id: str
    subject_id: str
    
    # Status
    status: MasteryLevel = MasteryLevel.NOT_STARTED
    mastery_score: float = 0.0  # 0.0 to 1.0
    
    # Statistics
    attempts: int = 0
    correct_answers: int = 0
    wrong_answers: int = 0
    hints_used: int = 0
    time_spent_minutes: int = 0
    
    # Assessment history
    assessment_scores: List[float] = field(default_factory=list)
    last_assessment_score: float = 0.0
    best_score: float = 0.0
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_practiced: Optional[datetime] = None
    
    # Notes
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "topic_id": self.topic_id,
            "subject_id": self.subject_id,
            "status": self.status.value,
            "mastery_score": self.mastery_score,
            "attempts": self.attempts,
            "correct_answers": self.correct_answers,
            "wrong_answers": self.wrong_answers,
            "hints_used": self.hints_used,
            "time_spent_minutes": self.time_spent_minutes,
            "assessment_scores": self.assessment_scores,
            "last_assessment_score": self.last_assessment_score,
            "best_score": self.best_score,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_practiced": self.last_practiced.isoformat() if self.last_practiced else None,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentProgress":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            student_id=data["student_id"],
            topic_id=data["topic_id"],
            subject_id=data.get("subject_id", ""),
            status=MasteryLevel(data.get("status", "not_started")),
            mastery_score=data.get("mastery_score", 0.0),
            attempts=data.get("attempts", 0),
            correct_answers=data.get("correct_answers", 0),
            wrong_answers=data.get("wrong_answers", 0),
            hints_used=data.get("hints_used", 0),
            time_spent_minutes=data.get("time_spent_minutes", 0),
            assessment_scores=data.get("assessment_scores", []),
            last_assessment_score=data.get("last_assessment_score", 0.0),
            best_score=data.get("best_score", 0.0),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            last_practiced=datetime.fromisoformat(data["last_practiced"]) if data.get("last_practiced") else None,
            notes=data.get("notes", ""),
        )
    
    def update_mastery(self) -> None:
        """Update mastery level based on score."""
        if self.mastery_score >= 0.9:
            self.status = MasteryLevel.MASTERED
        elif self.mastery_score >= 0.75:
            self.status = MasteryLevel.PROFICIENT
        elif self.mastery_score >= 0.5:
            self.status = MasteryLevel.DEVELOPING
        elif self.mastery_score > 0:
            self.status = MasteryLevel.BEGINNER
        else:
            self.status = MasteryLevel.NOT_STARTED


@dataclass
class AssessmentQuestion:
    """A question in an assessment."""
    id: str
    question_text: str
    question_text_ur: str = ""
    question_type: str = "multiple_choice"  # multiple_choice, true_false, short_answer, fill_blank
    options: List[str] = field(default_factory=list)
    options_ur: List[str] = field(default_factory=list)
    correct_answer: str = ""
    explanation: str = ""
    explanation_ur: str = ""
    difficulty: str = "medium"
    topic_id: str = ""
    objective_id: str = ""
    points: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question_text": self.question_text,
            "question_text_ur": self.question_text_ur,
            "question_type": self.question_type,
            "options": self.options,
            "options_ur": self.options_ur,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "explanation_ur": self.explanation_ur,
            "difficulty": self.difficulty,
            "topic_id": self.topic_id,
            "objective_id": self.objective_id,
            "points": self.points,
        }


@dataclass
class Assessment:
    """A complete assessment session."""
    id: str
    student_id: str
    assessment_type: AssessmentType
    topic_ids: List[str] = field(default_factory=list)
    subject_id: str = ""
    grade: int = 9
    language: str = "ur"
    
    # Questions and answers
    questions: List[AssessmentQuestion] = field(default_factory=list)
    answers: Dict[str, str] = field(default_factory=dict)  # question_id -> answer
    
    # Results
    total_questions: int = 0
    correct_count: int = 0
    wrong_count: int = 0
    score: float = 0.0  # 0.0 to 1.0
    total_points: int = 0
    earned_points: int = 0
    
    # Timing
    time_limit_minutes: int = 30
    time_taken_seconds: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, abandoned
    
    # Analysis
    weak_areas: List[str] = field(default_factory=list)
    strong_areas: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "assessment_type": self.assessment_type.value,
            "topic_ids": self.topic_ids,
            "subject_id": self.subject_id,
            "grade": self.grade,
            "language": self.language,
            "questions": [q.to_dict() for q in self.questions],
            "answers": self.answers,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "wrong_count": self.wrong_count,
            "score": self.score,
            "total_points": self.total_points,
            "earned_points": self.earned_points,
            "time_limit_minutes": self.time_limit_minutes,
            "time_taken_seconds": self.time_taken_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "weak_areas": self.weak_areas,
            "strong_areas": self.strong_areas,
            "recommendations": self.recommendations,
        }
    
    def calculate_score(self) -> None:
        """Calculate the assessment score."""
        if self.total_questions > 0:
            self.score = self.correct_count / self.total_questions
        else:
            self.score = 0.0
        
        if self.total_points > 0:
            self.score = self.earned_points / self.total_points
