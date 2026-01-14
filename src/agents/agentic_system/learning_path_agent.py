"""
Learning Path Agent
===================

Adapts learning difficulty dynamically and generates personalized learning paths.
"""

from typing import Dict, List, Any, Optional


class LearningPathAgent:
    """Generates and adapts personalized learning paths."""

    def __init__(self):
        self.difficulty_levels = ["beginner", "intermediate", "advanced"]
        self.learning_pace = ["slow", "normal", "fast"]

    def generate_learning_path(
        self,
        grade: str,
        subject: str,
        topic: str,
        studentProfile: Dict[str, Any],
        curriculum: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate personalized learning path.
        
        Returns recommended sequence of learning steps.
        """
        # Get student's current mastery
        mastery = studentProfile.get("topicMastery", {}).get(topic, 0)
        confidence = studentProfile.get("confidence", 50)
        speed = studentProfile.get("learningSpeed", "normal")
        
        # Determine starting point
        if mastery == 0:
            starting_level = "beginner"
        elif mastery < 40:
            starting_level = "beginner"
        elif mastery < 70:
            starting_level = "intermediate"
        else:
            starting_level = "advanced"
        
        # Build path
        path = {
            "topic": topic,
            "subject": subject,
            "grade": grade,
            "startingLevel": starting_level,
            "studentId": studentProfile.get("student_id"),
            "stages": self._build_learning_stages(
                topic,
                starting_level,
                curriculum,
                speed,
            ),
            "estimatedDuration": self._estimate_duration(speed, starting_level),
            "checkpoints": self._create_checkpoints(topic, starting_level),
            "resources": self._select_resources(topic, starting_level),
        }
        
        return path

    def _build_learning_stages(
        self,
        topic: str,
        startingLevel: str,
        curriculum: Dict[str, Any],
        speed: str,
    ) -> List[Dict[str, Any]]:
        """Build stages for learning path."""
        stages = []
        
        level_index = self.difficulty_levels.index(startingLevel)
        
        for idx in range(level_index, len(self.difficulty_levels)):
            level = self.difficulty_levels[idx]
            
            stage = {
                "stageNumber": idx - level_index + 1,
                "level": level,
                "duration": self._get_stage_duration(level, speed),
                "objectives": self._get_stage_objectives(topic, level),
                "activities": self._get_stage_activities(topic, level),
                "assessment": self._get_stage_assessment(topic, level),
                "prerequisite": self._get_prerequisite(topic, level),
            }
            stages.append(stage)
        
        return stages

    def _get_stage_duration(self, level: str, speed: str) -> int:
        """Get estimated duration in minutes."""
        base_duration = {
            "beginner": 30,
            "intermediate": 45,
            "advanced": 60,
        }
        
        speed_multiplier = {
            "slow": 1.5,
            "normal": 1.0,
            "fast": 0.7,
        }
        
        base = base_duration.get(level, 45)
        multiplier = speed_multiplier.get(speed, 1.0)
        
        return int(base * multiplier)

    def _get_stage_objectives(self, topic: str, level: str) -> List[str]:
        """Get learning objectives for stage."""
        objectives_map = {
            "beginner": [
                f"Understand basic concepts of {topic}",
                f"Learn fundamental terminology related to {topic}",
                f"Recognize common {topic} patterns",
            ],
            "intermediate": [
                f"Apply {topic} to solve problems",
                f"Understand relationships between {topic} concepts",
                f"Solve intermediate difficulty {topic} problems",
            ],
            "advanced": [
                f"Solve complex {topic} problems",
                f"Extend {topic} concepts to new domains",
                f"Create novel solutions using {topic}",
            ],
        }
        
        return objectives_map.get(level, [])

    def _get_stage_activities(self, topic: str, level: str) -> List[Dict[str, str]]:
        """Get recommended activities for stage."""
        activities_map = {
            "beginner": [
                {"type": "video", "name": f"Introduction to {topic}"},
                {"type": "reading", "name": f"Basic concepts of {topic}"},
                {"type": "practice", "name": f"Simple {topic} problems"},
            ],
            "intermediate": [
                {"type": "examples", "name": f"Worked examples of {topic}"},
                {"type": "practice", "name": f"Medium difficulty {topic} problems"},
                {"type": "quiz", "name": f"{topic} comprehension check"},
            ],
            "advanced": [
                {"type": "challenge", "name": f"Complex {topic} problems"},
                {"type": "project", "name": f"Real-world {topic} application"},
                {"type": "quiz", "name": f"Advanced {topic} assessment"},
            ],
        }
        
        return activities_map.get(level, [])

    def _get_stage_assessment(self, topic: str, level: str) -> Dict[str, Any]:
        """Get assessment for stage."""
        return {
            "type": "quiz",
            "questions": 5 if level == "beginner" else (8 if level == "intermediate" else 10),
            "passingScore": 70,
            "timeLimit": 15 if level == "beginner" else (20 if level == "intermediate" else 30),
        }

    def _get_prerequisite(self, topic: str, level: str) -> Optional[str]:
        """Get prerequisite for stage."""
        if level == "intermediate":
            return "beginner"
        elif level == "advanced":
            return "intermediate"
        return None

    def _estimate_duration(self, speed: str, startingLevel: str) -> Dict[str, int]:
        """Estimate total duration in minutes."""
        levels_to_cover = len(self.difficulty_levels) - self.difficulty_levels.index(startingLevel)
        
        base_minutes = {
            "beginner": 30,
            "intermediate": 45,
            "advanced": 60,
        }
        
        speed_multiplier = {
            "slow": 1.5,
            "normal": 1.0,
            "fast": 0.7,
        }
        
        total = sum(base_minutes.values()) * speed_multiplier.get(speed, 1.0)
        
        return {
            "total": int(total),
            "perLevel": int(sum(base_minutes.values()) / len(base_minutes) * speed_multiplier.get(speed, 1.0)),
        }

    def _create_checkpoints(self, topic: str, startingLevel: str) -> List[Dict[str, Any]]:
        """Create checkpoints for progress tracking."""
        return [
            {
                "number": 1,
                "description": f"Completed {startingLevel} level basics",
                "reward": 10,
            },
            {
                "number": 2,
                "description": f"Solved 5 {startingLevel} problems correctly",
                "reward": 20,
            },
            {
                "number": 3,
                "description": f"Passed {startingLevel} assessment",
                "reward": 50,
            },
        ]

    def _select_resources(self, topic: str, level: str) -> List[Dict[str, str]]:
        """Select learning resources."""
        return [
            {"type": "textbook", "title": f"{topic} - Chapter {level.upper()}"},
            {"type": "video", "title": f"Learn {topic} in {level} level"},
            {"type": "worksheet", "title": f"{topic} - {level} practice sheet"},
        ]

    def adapt_difficulty(
        self,
        currentDifficulty: str,
        performance: Dict[str, Any],
        studentProfile: Dict[str, Any],
    ) -> str:
        """Adapt difficulty based on performance."""
        accuracy = performance.get("accuracy", 0)
        speed = performance.get("speed", "normal")
        attempts = performance.get("attempts", 1)
        
        # Strong performance: increase difficulty
        if accuracy > 85 and speed == "fast" and attempts <= 2:
            if currentDifficulty == "beginner":
                return "intermediate"
            elif currentDifficulty == "intermediate":
                return "advanced"
        
        # Weak performance: decrease difficulty
        elif accuracy < 60 or attempts > 4:
            if currentDifficulty == "advanced":
                return "intermediate"
            elif currentDifficulty == "intermediate":
                return "beginner"
        
        # Medium performance: stay or slight adjustment
        elif accuracy > 70 and speed != "slow":
            if currentDifficulty in ["beginner", "intermediate"]:
                return "intermediate" if currentDifficulty == "beginner" else "intermediate"
        
        return currentDifficulty

    def get_next_topic_recommendation(
        self,
        completedTopics: List[str],
        studentProfile: Dict[str, Any],
        curriculum: Dict[str, Any],
    ) -> Optional[str]:
        """Recommend next topic to study."""
        # Get all topics in curriculum
        all_topics = self._extract_topics_from_curriculum(curriculum)
        
        # Filter out completed topics
        remaining_topics = [t for t in all_topics if t not in completedTopics]
        
        if not remaining_topics:
            return None
        
        # Prefer topics with completed prerequisites
        prerequisites_met = [
            t for t in remaining_topics
            if self._prerequisites_met(t, completedTopics)
        ]
        
        if prerequisites_met:
            return prerequisites_met[0]
        
        return remaining_topics[0]

    def _extract_topics_from_curriculum(self, curriculum: Dict[str, Any]) -> List[str]:
        """Extract all topics from curriculum."""
        topics = []
        chapters = curriculum.get("chapters", [])
        for chapter in chapters:
            for topic in chapter.get("topics", []):
                topics.append(topic.get("name"))
        return topics

    def _prerequisites_met(self, topic: str, completedTopics: List[str]) -> bool:
        """Check if prerequisites for topic are met."""
        # This would typically check a prerequisite graph
        return True
