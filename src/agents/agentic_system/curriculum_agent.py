"""
Curriculum Agent
================

Retrieves curriculum-aligned content from curriculum database.
Ensures all learning material is aligned with syllabus.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class CurriculumAgent:
    """Manages curriculum data and ensures content alignment."""

    def __init__(self, curriculum_dir: Path = None):
        self.curriculum_dir = curriculum_dir or Path(__file__).parent.parent.parent.parent / "curriculum"
        self.curriculum_dir.mkdir(parents=True, exist_ok=True)
        self._load_curriculum_index()

    def _load_curriculum_index(self):
        """Load all curriculum files into index."""
        self.curriculum_index = {}
        for file_path in self.curriculum_dir.glob("*.json"):
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
                grade = data.get("grade")
                subject = data.get("subject")
                key = f"{grade}_{subject}"
                self.curriculum_index[key] = data
            except Exception as e:
                print(f"Error loading curriculum file {file_path}: {e}")

    def get_curriculum_for_student(
        self,
        grade: str,
        board: str = "national",
        subject: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get curriculum data for a student."""
        if subject:
            key = f"{grade}_{subject}"
            return self.curriculum_index.get(key, {})
        
        # Return all subjects for grade
        return {
            k: v for k, v in self.curriculum_index.items()
            if k.startswith(f"{grade}_")
        }

    def get_topic_content(
        self,
        grade: str,
        subject: str,
        topic: str,
    ) -> Dict[str, Any]:
        """Get detailed content for a specific topic."""
        curriculum = self.get_curriculum_for_student(grade, subject=subject)
        if not curriculum:
            return {}
        
        chapters = curriculum.get("chapters", [])
        for chapter in chapters:
            topics = chapter.get("topics", [])
            for t in topics:
                if t.get("name", "").lower() == topic.lower():
                    return {
                        "topic": t.get("name"),
                        "chapter": chapter.get("name"),
                        "explanation": t.get("explanation"),
                        "examples": t.get("examples", []),
                        "difficulty": t.get("difficulty", "medium"),
                        "estimatedTime": t.get("estimatedTime"),
                        "objectives": t.get("objectives", []),
                        "prerequisites": t.get("prerequisites", []),
                    }
        
        return {}

    def validate_content(
        self,
        grade: str,
        subject: str,
        topic: str,
    ) -> Dict[str, Any]:
        """Validate if topic is in syllabus."""
        content = self.get_topic_content(grade, subject, topic)
        
        return {
            "isValid": bool(content),
            "inSyllabus": bool(content),
            "topic": topic,
            "grade": grade,
            "subject": subject,
            "message": (
                f"Topic '{topic}' found in {grade} {subject} curriculum"
                if content
                else f"Topic '{topic}' NOT found in {grade} {subject} curriculum"
            ),
        }

    def get_chapter_sequence(
        self,
        grade: str,
        subject: str,
    ) -> List[Dict[str, Any]]:
        """Get recommended chapter sequence."""
        curriculum = self.get_curriculum_for_student(grade, subject=subject)
        if not curriculum:
            return []
        
        chapters = curriculum.get("chapters", [])
        return [
            {
                "order": idx,
                "name": ch.get("name"),
                "topicCount": len(ch.get("topics", [])),
                "estimatedHours": ch.get("estimatedHours"),
            }
            for idx, ch in enumerate(chapters)
        ]

    def get_learning_objectives(
        self,
        grade: str,
        subject: str,
        topic: str,
    ) -> List[str]:
        """Get learning objectives for a topic."""
        content = self.get_topic_content(grade, subject, topic)
        return content.get("objectives", [])

    def get_similar_topics(
        self,
        grade: str,
        subject: str,
        topic: str,
    ) -> List[str]:
        """Get similar topics for reinforcement."""
        curriculum = self.get_curriculum_for_student(grade, subject=subject)
        if not curriculum:
            return []
        
        chapters = curriculum.get("chapters", [])
        similar = []
        
        for chapter in chapters:
            for t in chapter.get("topics", []):
                topic_name = t.get("name", "").lower()
                if topic.lower() in topic_name or topic_name in topic.lower():
                    if t.get("name") != topic:
                        similar.append(t.get("name"))
        
        return similar[:5]  # Return top 5

    def get_prerequisites(
        self,
        grade: str,
        subject: str,
        topic: str,
    ) -> List[str]:
        """Get prerequisite topics for a topic."""
        content = self.get_topic_content(grade, subject, topic)
        return content.get("prerequisites", [])

    def check_prerequisite_mastery(
        self,
        grade: str,
        subject: str,
        topic: str,
        studentMastery: Dict[str, int],
    ) -> Dict[str, Any]:
        """Check if student has mastered prerequisites."""
        prerequisites = self.get_prerequisites(grade, subject, topic)
        
        mastered = []
        notMastered = []
        
        for prereq in prerequisites:
            mastery_level = studentMastery.get(prereq, 0)
            if mastery_level >= 70:
                mastered.append(prereq)
            else:
                notMastered.append({
                    "topic": prereq,
                    "currentMastery": mastery_level,
                    "required": 70,
                })
        
        return {
            "canProceed": len(notMastered) == 0,
            "prerequisites": prerequisites,
            "mastered": mastered,
            "needToReview": notMastered,
        }

    def get_syllabus_compliance_report(
        self,
        grade: str,
        board: str,
    ) -> Dict[str, Any]:
        """Generate syllabus compliance report."""
        curricula = self.get_curriculum_for_student(grade)
        
        total_topics = 0
        total_chapters = 0
        
        for curr in curricula.values():
            for chapter in curr.get("chapters", []):
                total_chapters += 1
                total_topics += len(chapter.get("topics", []))
        
        return {
            "grade": grade,
            "board": board,
            "totalChapters": total_chapters,
            "totalTopics": total_topics,
            "subjects": list(curricula.keys()),
        }
