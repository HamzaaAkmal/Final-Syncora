"""
Tutor Agent
===========

Generates explanations and tutoring content based on student needs.
Adapts explanation difficulty and style to student level.
"""

from typing import Dict, List, Any, Optional


class TutorAgent:
    """Provides personalized tutoring and explanations."""

    def __init__(self):
        self.explanation_templates = {
            "beginner": {
                "structure": ["simple_intro", "basic_concept", "one_example", "key_takeaway"],
                "vocabulary": "simple",
                "examples": 1,
            },
            "intermediate": {
                "structure": ["intro", "concept", "two_examples", "applications", "summary"],
                "vocabulary": "technical",
                "examples": 2,
            },
            "advanced": {
                "structure": ["intro", "deep_concept", "multiple_examples", "proofs", "extensions"],
                "vocabulary": "advanced",
                "examples": 3,
            },
        }

    def generate_explanation(
        self,
        topic: str,
        content: Dict[str, Any],
        difficulty: str = "intermediate",
        style: str = "structured",
    ) -> Dict[str, Any]:
        """
        Generate an explanation for a topic.
        
        Args:
            topic: Topic name
            content: Curriculum content for topic
            difficulty: beginner, intermediate, advanced
            style: structured, conversational, story_based
        """
        template = self.explanation_templates.get(difficulty, self.explanation_templates["intermediate"])
        
        explanation = {
            "topic": topic,
            "difficulty": difficulty,
            "style": style,
            "structure": self._build_explanation_structure(
                topic,
                content,
                template,
                style,
            ),
            "keyPoints": self._extract_key_points(content),
            "examples": self._select_examples(content, template["examples"]),
            "commonMistakes": self._identify_common_mistakes(topic, difficulty),
        }
        
        return explanation

    def _build_explanation_structure(
        self,
        topic: str,
        content: Dict[str, Any],
        template: Dict[str, Any],
        style: str,
    ) -> str:
        """Build explanation following template."""
        parts = []
        
        # Intro
        parts.append(f"Let's understand {topic}.\n")
        
        # Main explanation
        explanation = content.get("explanation", "")
        parts.append(explanation)
        
        # Examples
        examples = content.get("examples", [])
        if examples:
            parts.append("\n\nExamples:")
            for i, example in enumerate(examples[:2], 1):
                parts.append(f"\nExample {i}: {example}")
        
        return "\n".join(parts)

    def _extract_key_points(self, content: Dict[str, Any]) -> List[str]:
        """Extract key learning points."""
        objectives = content.get("objectives", [])
        return objectives

    def _select_examples(self, content: Dict[str, Any], count: int) -> List[str]:
        """Select appropriate number of examples."""
        examples = content.get("examples", [])
        return examples[:count]

    def _identify_common_mistakes(self, topic: str, difficulty: str) -> List[str]:
        """Identify common mistakes for a topic."""
        common_mistakes = {
            "algebra": [
                "Forgetting to apply operation to both sides of equation",
                "Sign errors when moving terms across equals sign",
                "Not distributing coefficients correctly",
            ],
            "geometry": [
                "Confusing perimeter and area",
                "Not using correct angle relationships",
                "Missing units in final answer",
            ],
            "physics": [
                "Confusing velocity and acceleration",
                "Forgetting to include direction in vector answers",
                "Not considering all forces in force diagrams",
            ],
        }
        
        return common_mistakes.get(topic, ["Check your work carefully"])

    def generate_practice_question(
        self,
        topic: str,
        difficulty: str = "intermediate",
        questionType: str = "problem",
    ) -> Dict[str, Any]:
        """Generate a practice question."""
        return {
            "topic": topic,
            "difficulty": difficulty,
            "type": questionType,
            "question": f"[Practice question on {topic} at {difficulty} level]",
            "hint": f"Remember the key concepts of {topic}",
            "solution": "[Step-by-step solution]",
            "explanation": "[Why this solution is correct]",
        }

    def generate_hint(
        self,
        topic: str,
        studentAttempt: str,
        mistake: str = None,
    ) -> Dict[str, Any]:
        """Generate helpful hint based on student attempt."""
        return {
            "level": 1,
            "hint": f"Think about the definition of {topic}",
            "guidance": "Try breaking down the problem into smaller steps",
            "nextHint": f"What are the key properties of {topic}?",
        }

    def adapt_difficulty(
        self,
        currentDifficulty: str,
        studentPerformance: Dict[str, Any],
    ) -> str:
        """Adapt difficulty based on performance."""
        accuracy = studentPerformance.get("accuracy", 0)
        confidence = studentPerformance.get("confidence", 50)
        speed = studentPerformance.get("speed", "normal")
        
        # Increase difficulty if performing well
        if accuracy > 80 and confidence > 70 and speed == "fast":
            difficulty_map = {
                "beginner": "intermediate",
                "intermediate": "advanced",
                "advanced": "advanced",
            }
            return difficulty_map.get(currentDifficulty, currentDifficulty)
        
        # Decrease difficulty if struggling
        elif accuracy < 50 or confidence < 30:
            difficulty_map = {
                "beginner": "beginner",
                "intermediate": "beginner",
                "advanced": "intermediate",
            }
            return difficulty_map.get(currentDifficulty, currentDifficulty)
        
        return currentDifficulty

    def generate_reinforcement_content(
        self,
        topic: str,
        weeknesses: List[str],
    ) -> Dict[str, Any]:
        """Generate content to reinforce weak areas."""
        return {
            "topic": topic,
            "reinforcementType": "conceptual_review",
            "activities": [
                f"Review basic definition of {topic}",
                f"Work through simple examples of {topic}",
                f"Identify key differences in edge cases",
            ],
            "estimatedTime": "15 minutes",
        }

    def generate_challenge_content(
        self,
        topic: str,
        strengths: List[str],
    ) -> Dict[str, Any]:
        """Generate challenging content for advanced students."""
        return {
            "topic": topic,
            "challengeType": "advanced_application",
            "activities": [
                f"Apply {topic} to real-world scenarios",
                f"Solve complex multi-step problems using {topic}",
                f"Explore extensions and variations of {topic}",
            ],
            "estimatedTime": "30 minutes",
        }
