"""
Student Manager
===============

Handles student profile management and progress tracking.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid

from .models import (
    StudentProfile,
    StudentProgress,
    LanguagePreference,
    MasteryLevel,
    LearningPreferences,
)


class StudentManager:
    """
    Manages student profiles and progress.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the student manager.
        
        Args:
            data_dir: Directory for storing student data
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "user" / "students"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.profiles_file = self.data_dir / "profiles.json"
        self.progress_file = self.data_dir / "progress.json"
        
        # Load existing data
        self.profiles: Dict[str, StudentProfile] = {}
        self.progress: Dict[str, Dict[str, StudentProgress]] = {}  # student_id -> topic_id -> progress
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from files."""
        # Load profiles
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for profile_data in data.get("profiles", []):
                        profile = StudentProfile.from_dict(profile_data)
                        self.profiles[profile.student_id] = profile
            except Exception:
                pass
        
        # Load progress
        if self.progress_file.exists():
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for student_id, topics in data.get("progress", {}).items():
                        self.progress[student_id] = {}
                        for topic_id, progress_data in topics.items():
                            progress = StudentProgress.from_dict(progress_data)
                            self.progress[student_id][topic_id] = progress
            except Exception:
                pass
    
    def _save_profiles(self) -> None:
        """Save profiles to file."""
        data = {
            "profiles": [p.to_dict() for p in self.profiles.values()],
            "updated_at": datetime.now().isoformat(),
        }
        with open(self.profiles_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_progress(self) -> None:
        """Save progress to file."""
        data = {
            "progress": {
                student_id: {
                    topic_id: progress.to_dict()
                    for topic_id, progress in topics.items()
                }
                for student_id, topics in self.progress.items()
            },
            "updated_at": datetime.now().isoformat(),
        }
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # =========================================================================
    # Profile Management
    # =========================================================================
    
    def create_student(
        self,
        name: str,
        grade: int = 9,
        language: str = "ur",
        name_ur: str = "",
        board: str = "punjab",
        subjects: Optional[List[str]] = None,
    ) -> StudentProfile:
        """
        Create a new student profile.
        
        Args:
            name: Student name
            grade: Grade level (1-12)
            language: Preferred language ("en", "ur", "pa", "sd")
            name_ur: Name in Urdu (optional)
            board: Curriculum board
            subjects: List of subject IDs
            
        Returns:
            Created student profile
        """
        student_id = str(uuid.uuid4())[:8]
        
        profile = StudentProfile(
            student_id=student_id,
            name=name,
            name_ur=name_ur or name,
            grade=grade,
            board=board,
            language=LanguagePreference(language),
            subjects=subjects or ["mathematics", "science", "english", "urdu"],
        )
        
        self.profiles[student_id] = profile
        self.progress[student_id] = {}
        self._save_profiles()
        
        return profile
    
    def get_student(self, student_id: str) -> Optional[StudentProfile]:
        """Get a student profile by ID."""
        return self.profiles.get(student_id)
    
    def update_student(
        self,
        student_id: str,
        **updates: Any,
    ) -> Optional[StudentProfile]:
        """
        Update a student profile.
        
        Args:
            student_id: Student ID
            **updates: Fields to update
            
        Returns:
            Updated profile or None
        """
        profile = self.profiles.get(student_id)
        if not profile:
            return None
        
        for key, value in updates.items():
            if hasattr(profile, key):
                if key == "language":
                    value = LanguagePreference(value)
                elif key == "preferences":
                    value = LearningPreferences.from_dict(value)
                setattr(profile, key, value)
        
        profile.last_active = datetime.now()
        self._save_profiles()
        return profile
    
    def delete_student(self, student_id: str) -> bool:
        """Delete a student profile."""
        if student_id in self.profiles:
            del self.profiles[student_id]
            if student_id in self.progress:
                del self.progress[student_id]
            self._save_profiles()
            self._save_progress()
            return True
        return False
    
    def list_students(self) -> List[Dict[str, Any]]:
        """List all students."""
        return [p.to_dict() for p in self.profiles.values()]
    
    # =========================================================================
    # Progress Tracking
    # =========================================================================
    
    def get_progress(
        self,
        student_id: str,
        topic_id: str,
    ) -> Optional[StudentProgress]:
        """Get progress for a specific topic."""
        return self.progress.get(student_id, {}).get(topic_id)
    
    def update_progress(
        self,
        student_id: str,
        topic_id: str,
        subject_id: str = "",
        correct: bool = False,
        time_minutes: int = 0,
        hints_used: int = 0,
        assessment_score: Optional[float] = None,
    ) -> StudentProgress:
        """
        Update progress on a topic.
        
        Args:
            student_id: Student ID
            topic_id: Topic ID
            subject_id: Subject ID
            correct: Whether the last attempt was correct
            time_minutes: Time spent
            hints_used: Number of hints used
            assessment_score: Score from an assessment
            
        Returns:
            Updated progress
        """
        if student_id not in self.progress:
            self.progress[student_id] = {}
        
        if topic_id not in self.progress[student_id]:
            self.progress[student_id][topic_id] = StudentProgress(
                id=str(uuid.uuid4())[:8],
                student_id=student_id,
                topic_id=topic_id,
                subject_id=subject_id,
                started_at=datetime.now(),
            )
        
        progress = self.progress[student_id][topic_id]
        progress.attempts += 1
        progress.time_spent_minutes += time_minutes
        progress.hints_used += hints_used
        progress.last_practiced = datetime.now()
        
        if correct:
            progress.correct_answers += 1
        else:
            progress.wrong_answers += 1
        
        if assessment_score is not None:
            progress.assessment_scores.append(assessment_score)
            progress.last_assessment_score = assessment_score
            progress.best_score = max(progress.best_score, assessment_score)
            
            # Calculate mastery from recent scores
            recent_scores = progress.assessment_scores[-5:]
            progress.mastery_score = sum(recent_scores) / len(recent_scores)
        else:
            # Calculate mastery from correct/wrong ratio
            total = progress.correct_answers + progress.wrong_answers
            if total > 0:
                progress.mastery_score = progress.correct_answers / total
        
        progress.update_mastery()
        
        # Check if completed
        if progress.mastery_score >= 0.8 and progress.attempts >= 5:
            progress.status = MasteryLevel.MASTERED
            progress.completed_at = datetime.now()
        
        self._save_progress()
        return progress
    
    def get_all_progress(
        self,
        student_id: str,
        subject_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all progress for a student.
        
        Args:
            student_id: Student ID
            subject_id: Optional subject filter
            
        Returns:
            List of progress dictionaries
        """
        student_progress = self.progress.get(student_id, {})
        result = []
        
        for topic_id, progress in student_progress.items():
            if subject_id and progress.subject_id != subject_id:
                continue
            result.append(progress.to_dict())
        
        return result
    
    # =========================================================================
    # Statistics & Analytics
    # =========================================================================
    
    def get_student_stats(self, student_id: str) -> Dict[str, Any]:
        """
        Get comprehensive stats for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            Statistics dictionary
        """
        profile = self.profiles.get(student_id)
        if not profile:
            return {}
        
        student_progress = self.progress.get(student_id, {})
        
        total_topics = len(student_progress)
        mastered = sum(1 for p in student_progress.values() if p.status == MasteryLevel.MASTERED)
        proficient = sum(1 for p in student_progress.values() if p.status == MasteryLevel.PROFICIENT)
        developing = sum(1 for p in student_progress.values() if p.status == MasteryLevel.DEVELOPING)
        beginner = sum(1 for p in student_progress.values() if p.status == MasteryLevel.BEGINNER)
        
        total_time = sum(p.time_spent_minutes for p in student_progress.values())
        total_correct = sum(p.correct_answers for p in student_progress.values())
        total_wrong = sum(p.wrong_answers for p in student_progress.values())
        total_attempts = total_correct + total_wrong
        
        # Identify weak and strong topics
        weak_topics = [
            p.topic_id for p in student_progress.values()
            if p.mastery_score < 0.5 and p.attempts >= 3
        ]
        strong_topics = [
            p.topic_id for p in student_progress.values()
            if p.mastery_score >= 0.8
        ]
        
        return {
            "student_id": student_id,
            "name": profile.name,
            "grade": profile.grade,
            "total_topics": total_topics,
            "mastered_count": mastered,
            "proficient_count": proficient,
            "developing_count": developing,
            "beginner_count": beginner,
            "total_time_minutes": total_time,
            "total_attempts": total_attempts,
            "accuracy": total_correct / total_attempts if total_attempts > 0 else 0,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "current_streak": profile.current_streak,
            "points": profile.points,
            "badges": profile.badges,
        }
    
    def get_recommendations(
        self,
        student_id: str,
        subject_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Get topic recommendations for a student.
        
        Args:
            student_id: Student ID
            subject_id: Optional subject filter
            limit: Maximum recommendations
            
        Returns:
            List of recommended topic info
        """
        student_progress = self.progress.get(student_id, {})
        
        # Find topics needing improvement
        needs_practice = []
        for topic_id, progress in student_progress.items():
            if subject_id and progress.subject_id != subject_id:
                continue
            
            # Topics with low mastery that have been attempted
            if progress.mastery_score < 0.7 and progress.attempts >= 1:
                needs_practice.append({
                    "topic_id": topic_id,
                    "reason": "needs_practice",
                    "mastery_score": progress.mastery_score,
                    "last_practiced": progress.last_practiced.isoformat() if progress.last_practiced else None,
                })
            
            # Topics not practiced recently
            elif progress.last_practiced:
                days_since = (datetime.now() - progress.last_practiced).days
                if days_since > 7 and progress.mastery_score < 0.9:
                    needs_practice.append({
                        "topic_id": topic_id,
                        "reason": "spaced_repetition",
                        "days_since_practice": days_since,
                        "mastery_score": progress.mastery_score,
                    })
        
        # Sort by mastery score (lowest first)
        needs_practice.sort(key=lambda x: x.get("mastery_score", 1.0))
        
        return needs_practice[:limit]
    
    def update_streak(self, student_id: str) -> int:
        """
        Update the daily streak for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            Updated streak count
        """
        profile = self.profiles.get(student_id)
        if not profile:
            return 0
        
        now = datetime.now()
        last = profile.last_active
        
        if last.date() == now.date():
            # Same day, no change
            pass
        elif last.date() == (now - timedelta(days=1)).date():
            # Consecutive day
            profile.current_streak += 1
            profile.longest_streak = max(profile.longest_streak, profile.current_streak)
        else:
            # Streak broken
            profile.current_streak = 1
        
        profile.last_active = now
        self._save_profiles()
        
        return profile.current_streak
    
    def award_points(
        self,
        student_id: str,
        points: int,
        reason: str = "",
    ) -> int:
        """
        Award points to a student.
        
        Args:
            student_id: Student ID
            points: Points to award
            reason: Reason for awarding
            
        Returns:
            New total points
        """
        profile = self.profiles.get(student_id)
        if not profile:
            return 0
        
        profile.points += points
        self._save_profiles()
        
        return profile.points
    
    def award_badge(
        self,
        student_id: str,
        badge_id: str,
    ) -> List[str]:
        """
        Award a badge to a student.
        
        Args:
            student_id: Student ID
            badge_id: Badge ID
            
        Returns:
            Updated badge list
        """
        profile = self.profiles.get(student_id)
        if not profile:
            return []
        
        if badge_id not in profile.badges:
            profile.badges.append(badge_id)
            self._save_profiles()
        
        return profile.badges


# Global instance
_student_manager: Optional[StudentManager] = None


def get_student_manager() -> StudentManager:
    """Get or create the global student manager instance."""
    global _student_manager
    if _student_manager is None:
        _student_manager = StudentManager()
    return _student_manager
