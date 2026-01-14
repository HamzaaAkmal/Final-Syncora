"""
Assessment Engine
==================

Handles assessments, quizzes, and adaptive difficulty.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import os
import sys

# Add project root to path
_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from .models import (
    Assessment,
    AssessmentQuestion,
    AssessmentType,
    StudentProgress,
    MasteryLevel,
)
from .manager import StudentManager, get_student_manager
from src.curriculum import CurriculumManager, get_curriculum_manager


class AssessmentEngine:
    """
    Manages assessments and adaptive difficulty.
    """
    
    def __init__(
        self,
        student_manager: Optional[StudentManager] = None,
        curriculum_manager: Optional[CurriculumManager] = None,
        data_dir: Optional[Path] = None,
    ):
        """
        Initialize the assessment engine.
        
        Args:
            student_manager: Student manager instance
            curriculum_manager: Curriculum manager instance
            data_dir: Directory for storing assessment data
        """
        self.student_manager = student_manager or get_student_manager()
        self.curriculum_manager = curriculum_manager or get_curriculum_manager()
        
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "user" / "assessments"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Question bank cache
        self._question_bank: Dict[str, List[AssessmentQuestion]] = {}
    
    # =========================================================================
    # Assessment Creation
    # =========================================================================
    
    async def create_pre_assessment(
        self,
        student_id: str,
        subject_id: str,
        grade: int,
        language: str = "ur",
        num_questions: int = 10,
    ) -> Assessment:
        """
        Create a pre-assessment for a student.
        
        Args:
            student_id: Student ID
            subject_id: Subject ID
            grade: Grade level
            language: Assessment language
            num_questions: Number of questions
            
        Returns:
            Created assessment
        """
        # Get topics for the subject/grade
        topics = self.curriculum_manager.get_topics(
            subject_id=subject_id,
            grade=grade,
        )
        
        topic_ids = [t["id"] for t in topics]
        
        # Generate questions
        questions = await self._generate_questions(
            topic_ids=topic_ids,
            num_questions=num_questions,
            language=language,
            difficulty_mix={"easy": 0.4, "medium": 0.4, "hard": 0.2},
        )
        
        assessment = Assessment(
            id=str(uuid.uuid4())[:8],
            student_id=student_id,
            assessment_type=AssessmentType.PRE_ASSESSMENT,
            topic_ids=topic_ids,
            subject_id=subject_id,
            grade=grade,
            language=language,
            questions=questions,
            total_questions=len(questions),
            total_points=sum(q.points for q in questions),
            status="pending",
        )
        
        # Save assessment
        self._save_assessment(assessment)
        
        return assessment
    
    async def create_topic_quiz(
        self,
        student_id: str,
        topic_id: str,
        language: str = "ur",
        num_questions: int = 5,
        adaptive: bool = True,
    ) -> Assessment:
        """
        Create a quiz for a specific topic.
        
        Args:
            student_id: Student ID
            topic_id: Topic ID
            language: Quiz language
            num_questions: Number of questions
            adaptive: Whether to adapt difficulty based on progress
            
        Returns:
            Created assessment
        """
        topic = self.curriculum_manager.get_topic(topic_id)
        if not topic:
            raise ValueError(f"Topic not found: {topic_id}")
        
        # Determine difficulty based on student progress
        difficulty_mix = {"easy": 0.2, "medium": 0.5, "hard": 0.3}
        
        if adaptive:
            progress = self.student_manager.get_progress(student_id, topic_id)
            if progress:
                if progress.mastery_score < 0.3:
                    difficulty_mix = {"easy": 0.6, "medium": 0.3, "hard": 0.1}
                elif progress.mastery_score < 0.6:
                    difficulty_mix = {"easy": 0.3, "medium": 0.5, "hard": 0.2}
                elif progress.mastery_score < 0.8:
                    difficulty_mix = {"easy": 0.1, "medium": 0.5, "hard": 0.4}
                else:
                    difficulty_mix = {"easy": 0.0, "medium": 0.3, "hard": 0.7}
        
        questions = await self._generate_questions(
            topic_ids=[topic_id],
            num_questions=num_questions,
            language=language,
            difficulty_mix=difficulty_mix,
        )
        
        assessment = Assessment(
            id=str(uuid.uuid4())[:8],
            student_id=student_id,
            assessment_type=AssessmentType.QUIZ,
            topic_ids=[topic_id],
            subject_id=topic["subject_id"],
            grade=topic["grade"],
            language=language,
            questions=questions,
            total_questions=len(questions),
            total_points=sum(q.points for q in questions),
            time_limit_minutes=10,
            status="pending",
        )
        
        self._save_assessment(assessment)
        return assessment
    
    async def create_practice(
        self,
        student_id: str,
        topic_ids: List[str],
        language: str = "ur",
        num_questions: int = 5,
    ) -> Assessment:
        """
        Create a practice session.
        
        Args:
            student_id: Student ID
            topic_ids: List of topic IDs
            language: Practice language
            num_questions: Number of questions
            
        Returns:
            Created assessment
        """
        questions = await self._generate_questions(
            topic_ids=topic_ids,
            num_questions=num_questions,
            language=language,
            difficulty_mix={"easy": 0.3, "medium": 0.5, "hard": 0.2},
        )
        
        # Get subject and grade from first topic
        subject_id = ""
        grade = 9
        if topic_ids:
            topic = self.curriculum_manager.get_topic(topic_ids[0])
            if topic:
                subject_id = topic["subject_id"]
                grade = topic["grade"]
        
        assessment = Assessment(
            id=str(uuid.uuid4())[:8],
            student_id=student_id,
            assessment_type=AssessmentType.PRACTICE,
            topic_ids=topic_ids,
            subject_id=subject_id,
            grade=grade,
            language=language,
            questions=questions,
            total_questions=len(questions),
            total_points=sum(q.points for q in questions),
            time_limit_minutes=0,  # No time limit for practice
            status="pending",
        )
        
        self._save_assessment(assessment)
        return assessment
    
    # =========================================================================
    # Question Generation
    # =========================================================================
    
    async def _generate_questions(
        self,
        topic_ids: List[str],
        num_questions: int,
        language: str,
        difficulty_mix: Dict[str, float],
    ) -> List[AssessmentQuestion]:
        """
        Generate questions for topics.
        
        Args:
            topic_ids: List of topic IDs
            num_questions: Number of questions
            language: Language for questions
            difficulty_mix: Difficulty distribution
            
        Returns:
            List of generated questions
        """
        questions = []
        
        # Calculate questions per difficulty
        easy_count = int(num_questions * difficulty_mix.get("easy", 0.3))
        medium_count = int(num_questions * difficulty_mix.get("medium", 0.5))
        hard_count = num_questions - easy_count - medium_count
        
        # Get questions from bank or generate
        for topic_id in topic_ids:
            topic = self.curriculum_manager.get_topic(topic_id)
            if not topic:
                continue
            
            # Generate sample questions based on topic
            topic_questions = self._get_sample_questions_for_topic(
                topic,
                language,
                easy_count=easy_count // len(topic_ids) + 1,
                medium_count=medium_count // len(topic_ids) + 1,
                hard_count=hard_count // len(topic_ids) + 1,
            )
            questions.extend(topic_questions)
        
        # Limit to requested number
        return questions[:num_questions]
    
    def _get_sample_questions_for_topic(
        self,
        topic: Dict[str, Any],
        language: str,
        easy_count: int = 1,
        medium_count: int = 2,
        hard_count: int = 1,
    ) -> List[AssessmentQuestion]:
        """
        Get sample questions for a topic.
        
        This generates template questions based on topic.
        In production, these would come from LLM or question bank.
        """
        questions = []
        topic_id = topic["id"]
        topic_name = topic["name_ur"] if language == "ur" else topic["name"]
        
        # Sample question templates based on topic type
        templates_en = {
            "conceptual": {
                "question": f"What is the main concept behind {topic_name}?",
                "type": "multiple_choice",
                "difficulty": "easy",
            },
            "application": {
                "question": f"Apply the principles of {topic_name} to solve the following problem:",
                "type": "short_answer",
                "difficulty": "medium",
            },
            "analysis": {
                "question": f"Analyze and compare different approaches in {topic_name}:",
                "type": "multiple_choice",
                "difficulty": "hard",
            },
        }
        
        templates_ur = {
            "conceptual": {
                "question": f"{topic_name} کا بنیادی تصور کیا ہے؟",
                "type": "multiple_choice",
                "difficulty": "easy",
            },
            "application": {
                "question": f"{topic_name} کے اصولوں کو درج ذیل مسئلے میں لاگو کریں:",
                "type": "short_answer",
                "difficulty": "medium",
            },
            "analysis": {
                "question": f"{topic_name} میں مختلف طریقوں کا تجزیہ اور موازنہ کریں:",
                "type": "multiple_choice",
                "difficulty": "hard",
            },
        }
        
        templates = templates_ur if language == "ur" else templates_en
        
        # Generate questions based on objectives
        for i, obj in enumerate(topic.get("objectives", [])):
            if i >= easy_count + medium_count + hard_count:
                break
            
            if i < easy_count:
                template = templates["conceptual"]
                diff = "easy"
            elif i < easy_count + medium_count:
                template = templates["application"]
                diff = "medium"
            else:
                template = templates["analysis"]
                diff = "hard"
            
            obj_desc = obj.get("description_ur", obj.get("description", ""))
            if language == "en":
                obj_desc = obj.get("description", "")
            
            questions.append(AssessmentQuestion(
                id=f"{topic_id}_q{i+1}_{uuid.uuid4().hex[:4]}",
                question_text=template["question"],
                question_text_ur=templates_ur[list(templates_ur.keys())[min(i, 2)]]["question"],
                question_type=template["type"],
                options=[
                    "Option A" if language == "en" else "اختیار الف",
                    "Option B" if language == "en" else "اختیار ب",
                    "Option C" if language == "en" else "اختیار ج",
                    "Option D" if language == "en" else "اختیار د",
                ],
                correct_answer="Option A" if language == "en" else "اختیار الف",
                explanation=f"This relates to: {obj_desc}",
                explanation_ur=f"یہ اس سے متعلق ہے: {obj.get('description_ur', '')}",
                difficulty=diff,
                topic_id=topic_id,
                objective_id=obj.get("id", ""),
                points=1 if diff == "easy" else (2 if diff == "medium" else 3),
            ))
        
        # If no objectives, generate default questions
        if not questions:
            questions.append(AssessmentQuestion(
                id=f"{topic_id}_q1_{uuid.uuid4().hex[:4]}",
                question_text=templates["conceptual"]["question"],
                question_text_ur=templates_ur["conceptual"]["question"],
                question_type="multiple_choice",
                options=[
                    "Option A" if language == "en" else "اختیار الف",
                    "Option B" if language == "en" else "اختیار ب",
                    "Option C" if language == "en" else "اختیار ج",
                    "Option D" if language == "en" else "اختیار د",
                ],
                correct_answer="Option A" if language == "en" else "اختیار الف",
                difficulty="medium",
                topic_id=topic_id,
                points=2,
            ))
        
        return questions
    
    # =========================================================================
    # Assessment Submission & Grading
    # =========================================================================
    
    def start_assessment(self, assessment_id: str) -> Optional[Assessment]:
        """
        Start an assessment.
        
        Args:
            assessment_id: Assessment ID
            
        Returns:
            Updated assessment
        """
        assessment = self._load_assessment(assessment_id)
        if not assessment:
            return None
        
        assessment.status = "in_progress"
        assessment.started_at = datetime.now()
        self._save_assessment(assessment)
        
        return assessment
    
    def submit_answer(
        self,
        assessment_id: str,
        question_id: str,
        answer: str,
    ) -> Dict[str, Any]:
        """
        Submit an answer to a question.
        
        Args:
            assessment_id: Assessment ID
            question_id: Question ID
            answer: Student's answer
            
        Returns:
            Feedback dictionary
        """
        assessment = self._load_assessment(assessment_id)
        if not assessment:
            return {"error": "Assessment not found"}
        
        # Find the question
        question = None
        for q in assessment.questions:
            if q.id == question_id:
                question = q
                break
        
        if not question:
            return {"error": "Question not found"}
        
        # Record answer
        assessment.answers[question_id] = answer
        
        # Check if correct
        is_correct = answer.strip().lower() == question.correct_answer.strip().lower()
        
        if is_correct:
            assessment.correct_count += 1
            assessment.earned_points += question.points
        else:
            assessment.wrong_count += 1
        
        self._save_assessment(assessment)
        
        return {
            "question_id": question_id,
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation_ur if assessment.language == "ur" else question.explanation,
            "points_earned": question.points if is_correct else 0,
        }
    
    def complete_assessment(self, assessment_id: str) -> Optional[Assessment]:
        """
        Complete an assessment and calculate results.
        
        Args:
            assessment_id: Assessment ID
            
        Returns:
            Completed assessment with results
        """
        assessment = self._load_assessment(assessment_id)
        if not assessment:
            return None
        
        assessment.status = "completed"
        assessment.completed_at = datetime.now()
        
        if assessment.started_at:
            assessment.time_taken_seconds = int(
                (assessment.completed_at - assessment.started_at).total_seconds()
            )
        
        assessment.calculate_score()
        
        # Analyze results
        self._analyze_results(assessment)
        
        # Update student progress
        for topic_id in assessment.topic_ids:
            self.student_manager.update_progress(
                student_id=assessment.student_id,
                topic_id=topic_id,
                subject_id=assessment.subject_id,
                assessment_score=assessment.score,
            )
        
        # Award points
        self.student_manager.award_points(
            assessment.student_id,
            assessment.earned_points,
            f"Completed {assessment.assessment_type.value}",
        )
        
        self._save_assessment(assessment)
        return assessment
    
    def _analyze_results(self, assessment: Assessment) -> None:
        """Analyze assessment results to identify weak/strong areas."""
        topic_scores: Dict[str, Dict[str, int]] = {}
        
        for question in assessment.questions:
            topic_id = question.topic_id
            if topic_id not in topic_scores:
                topic_scores[topic_id] = {"correct": 0, "total": 0}
            
            topic_scores[topic_id]["total"] += 1
            if assessment.answers.get(question.id, "").strip().lower() == question.correct_answer.strip().lower():
                topic_scores[topic_id]["correct"] += 1
        
        # Identify weak and strong areas
        for topic_id, scores in topic_scores.items():
            ratio = scores["correct"] / scores["total"] if scores["total"] > 0 else 0
            
            if ratio < 0.5:
                assessment.weak_areas.append(topic_id)
                topic = self.curriculum_manager.get_topic(topic_id)
                if topic:
                    assessment.recommendations.append(
                        f"Review: {topic['name_ur'] if assessment.language == 'ur' else topic['name']}"
                    )
            elif ratio >= 0.8:
                assessment.strong_areas.append(topic_id)
    
    # =========================================================================
    # Storage
    # =========================================================================
    
    def _save_assessment(self, assessment: Assessment) -> None:
        """Save assessment to file."""
        filepath = self.data_dir / f"{assessment.id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(assessment.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_assessment(self, assessment_id: str) -> Optional[Assessment]:
        """Load assessment from file."""
        filepath = self.data_dir / f"{assessment_id}.json"
        if not filepath.exists():
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Reconstruct assessment
        assessment = Assessment(
            id=data["id"],
            student_id=data["student_id"],
            assessment_type=AssessmentType(data["assessment_type"]),
            topic_ids=data.get("topic_ids", []),
            subject_id=data.get("subject_id", ""),
            grade=data.get("grade", 9),
            language=data.get("language", "ur"),
            questions=[
                AssessmentQuestion(**q) for q in data.get("questions", [])
            ],
            answers=data.get("answers", {}),
            total_questions=data.get("total_questions", 0),
            correct_count=data.get("correct_count", 0),
            wrong_count=data.get("wrong_count", 0),
            score=data.get("score", 0.0),
            total_points=data.get("total_points", 0),
            earned_points=data.get("earned_points", 0),
            time_limit_minutes=data.get("time_limit_minutes", 30),
            time_taken_seconds=data.get("time_taken_seconds", 0),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            status=data.get("status", "pending"),
            weak_areas=data.get("weak_areas", []),
            strong_areas=data.get("strong_areas", []),
            recommendations=data.get("recommendations", []),
        )
        
        return assessment
    
    def get_student_assessments(
        self,
        student_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get recent assessments for a student.
        
        Args:
            student_id: Student ID
            limit: Maximum number of assessments
            
        Returns:
            List of assessment summaries
        """
        assessments = []
        
        for filepath in self.data_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if data.get("student_id") == student_id:
                    assessments.append({
                        "id": data["id"],
                        "type": data["assessment_type"],
                        "subject_id": data.get("subject_id"),
                        "score": data.get("score", 0),
                        "status": data.get("status"),
                        "completed_at": data.get("completed_at"),
                    })
            except Exception:
                continue
        
        # Sort by completion date (most recent first)
        assessments.sort(
            key=lambda x: x.get("completed_at") or "",
            reverse=True,
        )
        
        return assessments[:limit]
    
    # =========================================================================
    # Adaptive Difficulty
    # =========================================================================
    
    def get_recommended_difficulty(
        self,
        student_id: str,
        topic_id: str,
    ) -> str:
        """
        Get recommended difficulty level for a student on a topic.
        
        Args:
            student_id: Student ID
            topic_id: Topic ID
            
        Returns:
            Difficulty level: "easy", "medium", or "hard"
        """
        progress = self.student_manager.get_progress(student_id, topic_id)
        
        if not progress:
            return "easy"
        
        if progress.mastery_score < 0.3:
            return "easy"
        elif progress.mastery_score < 0.6:
            return "medium"
        elif progress.mastery_score < 0.85:
            return "hard"
        else:
            # Mastered - challenge with harder problems
            return "hard"
    
    def check_prerequisites(
        self,
        student_id: str,
        topic_id: str,
    ) -> Dict[str, Any]:
        """
        Check if student has mastered prerequisites for a topic.
        
        Args:
            student_id: Student ID
            topic_id: Topic ID
            
        Returns:
            Prerequisite check result
        """
        topic = self.curriculum_manager.get_topic(topic_id)
        if not topic:
            return {"ready": True, "missing": []}
        
        prerequisites = topic.get("prerequisites", [])
        missing = []
        
        for prereq_id in prerequisites:
            progress = self.student_manager.get_progress(student_id, prereq_id)
            if not progress or progress.mastery_score < 0.6:
                prereq_topic = self.curriculum_manager.get_topic(prereq_id)
                if prereq_topic:
                    missing.append({
                        "topic_id": prereq_id,
                        "name": prereq_topic["name"],
                        "name_ur": prereq_topic["name_ur"],
                        "mastery": progress.mastery_score if progress else 0,
                    })
        
        return {
            "ready": len(missing) == 0,
            "missing": missing,
            "message": "Ready to learn!" if not missing else f"Please complete {len(missing)} prerequisite topic(s) first.",
            "message_ur": "سیکھنے کے لیے تیار!" if not missing else f"پہلے {len(missing)} لازمی موضوع(عات) مکمل کریں۔",
        }


# Global instance
_assessment_engine: Optional[AssessmentEngine] = None


def get_assessment_engine() -> AssessmentEngine:
    """Get or create the global assessment engine instance."""
    global _assessment_engine
    if _assessment_engine is None:
        _assessment_engine = AssessmentEngine()
    return _assessment_engine
