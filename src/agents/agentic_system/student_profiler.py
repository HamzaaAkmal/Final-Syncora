"""
Student Profiler Agent
======================

Analyzes student input and builds/updates student profile.
Tracks learning speed, confidence, mastery levels, and mistakes.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class StudentProfiler:
    """Profiles student based on input, performance, and interaction patterns."""

    def __init__(self, profile_dir: Path = None):
        self.profile_dir = profile_dir or Path(__file__).parent.parent.parent.parent / "data"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.profile_path = self.profile_dir / "studentProfile.json"
        self.student_id = self._get_or_create_student_id()

    def _get_or_create_student_id(self) -> str:
        """Get existing student ID or create new one."""
        if self.profile_path.exists():
            try:
                data = json.loads(self.profile_path.read_text())
                return data.get("student_id")
            except:
                pass
        return str(uuid.uuid4())

    def load_profile(self) -> Dict[str, Any]:
        """Load student profile from file."""
        if self.profile_path.exists():
            try:
                return json.loads(self.profile_path.read_text())
            except:
                pass
        
        # Default profile
        return {
            "student_id": self.student_id,
            "grade": None,
            "board": "national",  # national, punjab, sindh, kpk
            "language": "en",     # en, ur, ur_roman
            "learningSpeed": "normal",  # slow, normal, fast
            "topicMastery": {},   # topic_id -> mastery_level (0-100)
            "mistakes": [],       # Recent mistakes
            "confidence": 50,     # 0-100
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "interactions": 0,
            "strengths": [],
            "weaknesses": [],
        }

    def analyze_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze student input to extract information.
        
        Returns:
            {
                "grade": inferred grade,
                "board": inferred board,
                "language": detected language,
                "learningSpeed": assessed speed,
                "confidence": assessed confidence (0-100),
                "topicOfInterest": detected topic,
                "mistakeDetected": whether mistake was made,
                "nextDifficulty": recommended difficulty,
            }
        """
        profile = self.load_profile()
        
        analysis = {
            "grade": profile.get("grade"),
            "board": profile.get("board"),
            "language": self._detect_language(user_input),
            "learningSpeed": profile.get("learningSpeed"),
            "confidence": self._assess_confidence(user_input, profile),
            "topicOfInterest": self._extract_topic(user_input),
            "mistakeDetected": self._detect_mistake(user_input),
            "nextDifficulty": self._assess_next_difficulty(profile),
            "engagementLevel": self._assess_engagement(profile),
        }
        
        return analysis

    def _detect_language(self, text: str) -> str:
        """Detect language: en, ur, ur_roman."""
        if not text:
            return "en"
        
        # Simple detection
        urdu_chars = "آ ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن ں و ہ ء ی ے"
        if any(char in text for char in urdu_chars):
            return "ur"
        
        # Roman Urdu detection (common patterns)
        roman_urdu_patterns = ["kya", "hai", "acha", "bilkul", "theek"]
        if any(pattern in text.lower() for pattern in roman_urdu_patterns):
            return "ur_roman"
        
        return "en"

    def _assess_confidence(self, text: str, profile: Dict) -> int:
        """Assess student's confidence level."""
        base = profile.get("confidence", 50)
        
        confidence_indicators = {
            "i'm sure": 10,
            "i think": -5,
            "i don't know": -15,
            "definitely": 15,
            "maybe": -10,
            "confused": -20,
        }
        
        adjustment = 0
        text_lower = text.lower()
        for indicator, value in confidence_indicators.items():
            if indicator in text_lower:
                adjustment += value
        
        return max(0, min(100, base + adjustment))

    def _extract_topic(self, text: str) -> Optional[str]:
        """Extract topic from student input."""
        # Simple keyword matching
        topics = {
            "algebra": ["equation", "variable", "linear", "quadratic"],
            "geometry": ["triangle", "circle", "angle", "area", "perimeter"],
            "physics": ["force", "motion", "energy", "newton", "velocity"],
            "chemistry": ["element", "compound", "reaction", "atom", "molecule"],
            "biology": ["cell", "organism", "evolution", "genetics", "photosynthesis"],
            "english": ["grammar", "vocabulary", "reading", "writing", "comprehension"],
            "urdu": ["grammar", "vocabulary", "شاعری", "grammar"],
        }
        
        text_lower = text.lower()
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        
        return None

    def _detect_mistake(self, text: str) -> bool:
        """Detect if student made a conceptual mistake."""
        # Simple heuristic
        mistake_patterns = [
            "i got",
            "my answer was",
            "i think it's",
            "is this right",
            "why is",
        ]
        return any(pattern in text.lower() for pattern in mistake_patterns)

    def _assess_next_difficulty(self, profile: Dict) -> str:
        """Recommend difficulty level based on profile."""
        mastery = profile.get("topicMastery", {})
        if not mastery:
            return "beginner"
        
        avg_mastery = sum(mastery.values()) / len(mastery) if mastery else 0
        confidence = profile.get("confidence", 50)
        
        if avg_mastery > 80 and confidence > 75:
            return "advanced"
        elif avg_mastery > 60 and confidence > 50:
            return "intermediate"
        else:
            return "beginner"

    def _assess_engagement(self, profile: Dict) -> str:
        """Assess student engagement level."""
        interactions = profile.get("interactions", 0)
        if interactions > 50:
            return "highly_engaged"
        elif interactions > 20:
            return "engaged"
        elif interactions > 5:
            return "moderately_engaged"
        else:
            return "new_user"

    def update_profile(
        self,
        grade: str = None,
        board: str = None,
        language: str = None,
        learningSpeed: str = None,
        topicId: str = None,
        masteryLevel: int = None,
        mistakeMade: bool = False,
        confidenceAdjustment: int = 0,
    ) -> Dict[str, Any]:
        """Update student profile with new information."""
        profile = self.load_profile()
        
        if grade:
            profile["grade"] = grade
        if board:
            profile["board"] = board
        if language:
            profile["language"] = language
        if learningSpeed:
            profile["learningSpeed"] = learningSpeed
        
        # Update topic mastery
        if topicId and masteryLevel is not None:
            profile["topicMastery"][topicId] = masteryLevel
        
        # Track mistakes
        if mistakeMade:
            profile["mistakes"].append({
                "timestamp": datetime.now().isoformat(),
                "topic": topicId,
            })
            # Keep only last 10 mistakes
            profile["mistakes"] = profile["mistakes"][-10:]
        
        # Update confidence
        profile["confidence"] = max(0, min(100, profile.get("confidence", 50) + confidenceAdjustment))
        
        # Update interaction count
        profile["interactions"] = profile.get("interactions", 0) + 1
        
        # Update timestamp
        profile["last_updated"] = datetime.now().isoformat()
        
        # Save profile
        self.profile_path.write_text(json.dumps(profile, indent=2))
        
        return profile

    def get_student_summary(self) -> Dict[str, Any]:
        """Get summary of student profile for other agents."""
        profile = self.load_profile()
        
        return {
            "student_id": profile.get("student_id"),
            "grade": profile.get("grade"),
            "board": profile.get("board"),
            "language": profile.get("language"),
            "learningSpeed": profile.get("learningSpeed"),
            "avgMastery": (
                sum(profile.get("topicMastery", {}).values()) / len(profile.get("topicMastery", {}))
                if profile.get("topicMastery")
                else 0
            ),
            "recentMistakes": profile.get("mistakes", [])[-3:],
            "confidence": profile.get("confidence", 50),
            "engagementLevel": self._assess_engagement(profile),
        }
