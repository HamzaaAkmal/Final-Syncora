"""
Curriculum Manager
==================

Provides methods to query and manage curriculum data.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from .models import Subject, Chapter, Topic, CurriculumBoard, DifficultyLevel
from .data import CURRICULUM_DATA, SUBJECTS, ALL_TOPICS, ALL_CHAPTERS


class CurriculumManager:
    """
    Manages curriculum data and provides query methods.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the curriculum manager.
        
        Args:
            data_dir: Optional path to store/load custom curriculum data
        """
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / "data" / "curriculum"
        self.subjects = {s.id: s for s in SUBJECTS}
        self.topics = {t.id: t for t in ALL_TOPICS}
        self.chapters = {c.id: c for c in ALL_CHAPTERS}
    
    # =========================================================================
    # Subject Methods
    # =========================================================================
    
    def get_subjects(
        self,
        grade: Optional[int] = None,
        board: Optional[CurriculumBoard] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all subjects, optionally filtered by grade and board.
        
        Args:
            grade: Filter by grade level (1-12)
            board: Filter by curriculum board
            
        Returns:
            List of subject dictionaries
        """
        result = []
        for subject in self.subjects.values():
            if grade and grade not in subject.grades:
                continue
            if board and subject.board != board:
                continue
            result.append(subject.to_dict())
        return result
    
    def get_subject(self, subject_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific subject by ID.
        
        Args:
            subject_id: The subject ID (e.g., "mathematics")
            
        Returns:
            Subject dictionary or None
        """
        subject = self.subjects.get(subject_id)
        return subject.to_dict() if subject else None
    
    # =========================================================================
    # Chapter Methods
    # =========================================================================
    
    def get_chapters(
        self,
        subject_id: str,
        grade: int,
    ) -> List[Dict[str, Any]]:
        """
        Get chapters for a subject and grade.
        
        Args:
            subject_id: The subject ID
            grade: The grade level
            
        Returns:
            List of chapter dictionaries
        """
        subject = self.subjects.get(subject_id)
        if not subject:
            return []
        
        chapters = subject.chapters.get(grade, [])
        return [chapter.to_dict() for chapter in chapters]
    
    def get_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific chapter by ID.
        
        Args:
            chapter_id: The chapter ID
            
        Returns:
            Chapter dictionary or None
        """
        chapter = self.chapters.get(chapter_id)
        return chapter.to_dict() if chapter else None
    
    # =========================================================================
    # Topic Methods
    # =========================================================================
    
    def get_topics(
        self,
        subject_id: Optional[str] = None,
        grade: Optional[int] = None,
        chapter_id: Optional[str] = None,
        difficulty: Optional[DifficultyLevel] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get topics with optional filters.
        
        Args:
            subject_id: Filter by subject
            grade: Filter by grade
            chapter_id: Filter by chapter
            difficulty: Filter by difficulty level
            
        Returns:
            List of topic dictionaries
        """
        result = []
        for topic in self.topics.values():
            if subject_id and topic.subject_id != subject_id:
                continue
            if grade and topic.grade != grade:
                continue
            if chapter_id and topic.chapter_id != chapter_id:
                continue
            if difficulty and topic.difficulty != difficulty:
                continue
            result.append(topic.to_dict())
        
        # Sort by order
        result.sort(key=lambda x: (x.get("chapter_id", ""), x.get("order", 0)))
        return result
    
    def get_topic(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific topic by ID.
        
        Args:
            topic_id: The topic ID
            
        Returns:
            Topic dictionary or None
        """
        topic = self.topics.get(topic_id)
        return topic.to_dict() if topic else None
    
    def get_prerequisites(self, topic_id: str) -> List[Dict[str, Any]]:
        """
        Get prerequisite topics for a given topic.
        
        Args:
            topic_id: The topic ID
            
        Returns:
            List of prerequisite topic dictionaries
        """
        topic = self.topics.get(topic_id)
        if not topic:
            return []
        
        return [
            self.topics[prereq_id].to_dict()
            for prereq_id in topic.prerequisites
            if prereq_id in self.topics
        ]
    
    def get_learning_path(
        self,
        topic_id: str,
        include_prerequisites: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get a learning path for a topic including prerequisites.
        
        Args:
            topic_id: The target topic ID
            include_prerequisites: Whether to include prerequisites
            
        Returns:
            Ordered list of topics to learn
        """
        topic = self.topics.get(topic_id)
        if not topic:
            return []
        
        path = []
        visited = set()
        
        def add_with_prereqs(t_id: str):
            if t_id in visited:
                return
            visited.add(t_id)
            
            t = self.topics.get(t_id)
            if not t:
                return
            
            # First add prerequisites
            if include_prerequisites:
                for prereq_id in t.prerequisites:
                    add_with_prereqs(prereq_id)
            
            path.append(t.to_dict())
        
        add_with_prereqs(topic_id)
        return path
    
    # =========================================================================
    # Search Methods
    # =========================================================================
    
    def search_topics(
        self,
        query: str,
        subject_id: Optional[str] = None,
        grade: Optional[int] = None,
        language: str = "en",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search topics by keyword.
        
        Args:
            query: Search query
            subject_id: Optional subject filter
            grade: Optional grade filter
            language: Language for search ("en" or "ur")
            limit: Maximum results
            
        Returns:
            List of matching topic dictionaries
        """
        query_lower = query.lower()
        results = []
        
        for topic in self.topics.values():
            if subject_id and topic.subject_id != subject_id:
                continue
            if grade and topic.grade != grade:
                continue
            
            # Score based on match quality
            score = 0
            
            # Check name
            if language == "ur":
                if query in topic.name_ur:
                    score += 10
            else:
                if query_lower in topic.name.lower():
                    score += 10
            
            # Check keywords
            for keyword in topic.keywords:
                if query_lower in keyword.lower() or query in keyword:
                    score += 5
            
            # Check description
            if language == "ur":
                if query in topic.description_ur:
                    score += 3
            else:
                if query_lower in topic.description.lower():
                    score += 3
            
            if score > 0:
                topic_dict = topic.to_dict()
                topic_dict["search_score"] = score
                results.append(topic_dict)
        
        # Sort by score and limit
        results.sort(key=lambda x: x["search_score"], reverse=True)
        return results[:limit]
    
    # =========================================================================
    # Curriculum Alignment Methods
    # =========================================================================
    
    def align_content_to_curriculum(
        self,
        content: str,
        subject_id: Optional[str] = None,
        grade: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find curriculum topics that align with given content.
        
        Args:
            content: The content to align
            subject_id: Optional subject filter
            grade: Optional grade filter
            
        Returns:
            List of aligned topic dictionaries with alignment scores
        """
        content_lower = content.lower()
        results = []
        
        for topic in self.topics.values():
            if subject_id and topic.subject_id != subject_id:
                continue
            if grade and topic.grade != grade:
                continue
            
            score = 0
            matched_keywords = []
            
            # Check keywords
            for keyword in topic.keywords:
                if keyword.lower() in content_lower or keyword in content:
                    score += 10
                    matched_keywords.append(keyword)
            
            # Check topic name
            if topic.name.lower() in content_lower:
                score += 15
                matched_keywords.append(topic.name)
            
            # Check objectives
            for obj in topic.objectives:
                for keyword in obj.keywords:
                    if keyword.lower() in content_lower:
                        score += 5
                        matched_keywords.append(keyword)
            
            if score > 0:
                topic_dict = topic.to_dict()
                topic_dict["alignment_score"] = score
                topic_dict["matched_keywords"] = list(set(matched_keywords))
                results.append(topic_dict)
        
        # Sort by alignment score
        results.sort(key=lambda x: x["alignment_score"], reverse=True)
        return results
    
    def get_topic_by_keywords(
        self,
        keywords: List[str],
        subject_id: Optional[str] = None,
        grade: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best matching topic for given keywords.
        
        Args:
            keywords: List of keywords to match
            subject_id: Optional subject filter
            grade: Optional grade filter
            
        Returns:
            Best matching topic dictionary or None
        """
        results = self.align_content_to_curriculum(
            content=" ".join(keywords),
            subject_id=subject_id,
            grade=grade,
        )
        return results[0] if results else None
    
    # =========================================================================
    # Statistics Methods
    # =========================================================================
    
    def get_curriculum_stats(
        self,
        subject_id: Optional[str] = None,
        grade: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get curriculum statistics.
        
        Args:
            subject_id: Optional subject filter
            grade: Optional grade filter
            
        Returns:
            Statistics dictionary
        """
        topics = self.get_topics(subject_id=subject_id, grade=grade)
        
        total_hours = sum(t.get("estimated_hours", 0) for t in topics)
        difficulty_counts = {}
        for t in topics:
            diff = t.get("difficulty", "medium")
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        return {
            "total_topics": len(topics),
            "total_estimated_hours": total_hours,
            "difficulty_distribution": difficulty_counts,
            "subjects": len(set(t.get("subject_id") for t in topics)),
        }
    
    # =========================================================================
    # Export/Import Methods
    # =========================================================================
    
    def export_curriculum(self, filepath: Path) -> None:
        """
        Export curriculum data to a JSON file.
        
        Args:
            filepath: Path to export file
        """
        data = {
            "subjects": [s.to_dict() for s in self.subjects.values()],
            "chapters": [c.to_dict() for c in self.chapters.values()],
            "topics": [t.to_dict() for t in self.topics.values()],
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_grade_curriculum_summary(
        self,
        grade: int,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Get a summary of all subjects and topics for a grade.
        
        Args:
            grade: Grade level
            language: Language for text ("en" or "ur")
            
        Returns:
            Curriculum summary dictionary
        """
        subjects_data = []
        
        for subject in self.subjects.values():
            if grade not in subject.grades:
                continue
            
            chapters = subject.chapters.get(grade, [])
            chapters_data = []
            
            for chapter in chapters:
                topics_data = []
                for topic in chapter.topics:
                    topics_data.append({
                        "id": topic.id,
                        "name": topic.name_ur if language == "ur" else topic.name,
                        "difficulty": topic.difficulty.value,
                        "estimated_hours": topic.estimated_hours,
                    })
                
                chapters_data.append({
                    "id": chapter.id,
                    "name": chapter.name_ur if language == "ur" else chapter.name,
                    "topics": topics_data,
                    "topic_count": len(topics_data),
                })
            
            subjects_data.append({
                "id": subject.id,
                "name": subject.name_ur if language == "ur" else subject.name,
                "icon": subject.icon,
                "chapters": chapters_data,
                "chapter_count": len(chapters_data),
                "total_topics": sum(len(c.topics) for c in chapters),
            })
        
        return {
            "grade": grade,
            "language": language,
            "subjects": subjects_data,
            "total_subjects": len(subjects_data),
        }


# Global instance
_curriculum_manager: Optional[CurriculumManager] = None


def get_curriculum_manager() -> CurriculumManager:
    """Get or create the global curriculum manager instance."""
    global _curriculum_manager
    if _curriculum_manager is None:
        _curriculum_manager = CurriculumManager()
    return _curriculum_manager
