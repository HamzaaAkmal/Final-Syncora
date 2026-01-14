"""
Safety Agent
============

Enforces content safety and syllabus boundaries.
Prevents harmful content and ensures age-appropriate learning.
"""

from typing import Dict, List, Any


class SafetyAgent:
    """Ensures content safety and policy compliance."""

    def __init__(self):
        self.safety_levels = {
            "unrestricted": 1,
            "general": 2,
            "educational": 3,
            "restricted": 4,
        }
        
        self.banned_keywords = [
            "violence", "hate", "discrimination", "abuse",
            "drug", "alcohol", "smoking", "adult",
        ]
        
        self.age_appropriate_topics = {
            "grade_1_3": ["basic_math", "colors", "animals", "numbers"],
            "grade_4_6": ["multiplication", "division", "simple_geometry", "science_basics"],
            "grade_7_8": ["algebra", "geometry", "physics_basics", "chemistry_basics"],
            "grade_9_10": ["advanced_algebra", "trigonometry", "physics", "chemistry"],
            "grade_11_12": ["calculus", "advanced_physics", "organic_chemistry", "statistics"],
        }

    def check_content_safety(
        self,
        content: str,
        grade: int,
        topic: str,
    ) -> Dict[str, Any]:
        """
        Check if content is safe and appropriate.
        
        Returns:
            {
                "isSafe": bool,
                "safetyLevel": str,
                "issues": [],
                "recommendations": [],
            }
        """
        issues = []
        
        # Check for banned keywords
        for keyword in self.banned_keywords:
            if keyword.lower() in content.lower():
                issues.append(f"Contains banned keyword: {keyword}")
        
        # Check age appropriateness
        age_check = self._check_age_appropriateness(grade, topic)
        if not age_check["isAppropriate"]:
            issues.append(age_check["reason"])
        
        # Check for violent or harmful content
        if self._contains_harmful_content(content):
            issues.append("Content contains potentially harmful material")
        
        # Determine safety level
        isSafe = len(issues) == 0
        safetyLevel = self._determine_safety_level(issues, grade)
        
        return {
            "isSafe": isSafe,
            "safetyLevel": safetyLevel,
            "issues": issues,
            "recommendations": self._generate_recommendations(issues, topic),
            "grade": grade,
            "topic": topic,
        }

    def _check_age_appropriateness(self, grade: int, topic: str) -> Dict[str, Any]:
        """Check if topic is appropriate for grade."""
        if grade <= 3:
            grade_range = "grade_1_3"
        elif grade <= 6:
            grade_range = "grade_4_6"
        elif grade <= 8:
            grade_range = "grade_7_8"
        elif grade <= 10:
            grade_range = "grade_9_10"
        else:
            grade_range = "grade_11_12"
        
        allowed_topics = self.age_appropriate_topics.get(grade_range, [])
        
        # Simple check: see if topic matches allowed topics
        is_appropriate = any(
            allowed in topic.lower() for allowed in allowed_topics
        )
        
        return {
            "isAppropriate": is_appropriate,
            "reason": f"Topic '{topic}' not appropriate for grade {grade}" if not is_appropriate else "",
            "gradeRange": grade_range,
        }

    def _contains_harmful_content(self, content: str) -> bool:
        """Check for harmful content patterns."""
        harmful_patterns = [
            "hurt yourself",
            "harm others",
            "dangerous method",
            "illegal",
            "hate",
        ]
        
        return any(pattern in content.lower() for pattern in harmful_patterns)

    def _determine_safety_level(self, issues: List[str], grade: int) -> str:
        """Determine safety level based on issues."""
        if len(issues) == 0:
            return "educational"
        elif len(issues) == 1:
            return "general"
        elif len(issues) <= 3:
            return "restricted"
        else:
            return "unsafe"

    def _generate_recommendations(self, issues: List[str], topic: str) -> List[str]:
        """Generate recommendations to fix issues."""
        recommendations = []
        
        if not issues:
            recommendations.append("Content is safe to use")
            return recommendations
        
        if "banned keyword" in str(issues):
            recommendations.append("Remove or replace banned keywords")
        
        if "age" in str(issues):
            recommendations.append("Consider simplifying content for younger students")
        
        if "harmful" in str(issues):
            recommendations.append("Replace harmful content with safe alternatives")
        
        recommendations.append(f"Review and revise content on topic: {topic}")
        
        return recommendations

    def validate_against_syllabus(
        self,
        content: str,
        grade: str,
        subject: str,
        topic: str,
        curriculumTopics: List[str],
    ) -> Dict[str, Any]:
        """Validate content is within syllabus."""
        inSyllabus = topic in curriculumTopics
        
        return {
            "inSyllabus": inSyllabus,
            "topic": topic,
            "subject": subject,
            "grade": grade,
            "message": (
                f"Content aligns with {grade} {subject} syllabus"
                if inSyllabus
                else f"Warning: '{topic}' not in {grade} {subject} syllabus"
            ),
        }

    def filter_response(
        self,
        response: str,
        grade: int,
        language: str,
    ) -> Dict[str, Any]:
        """Filter response to ensure safety."""
        filtered_response = response
        censored_count = 0
        
        for keyword in self.banned_keywords:
            if keyword in filtered_response.lower():
                # Replace with asterisks
                filtered_response = filtered_response.replace(keyword, "*" * len(keyword))
                censored_count += 1
        
        return {
            "originalLength": len(response),
            "filteredLength": len(filtered_response),
            "censored": censored_count,
            "isSafe": censored_count == 0,
            "response": filtered_response,
            "grade": grade,
            "language": language,
        }

    def log_safety_check(
        self,
        studentId: str,
        content: str,
        result: Dict[str, Any],
    ) -> None:
        """Log safety check for auditing."""
        # Can be extended to write to file/database
        pass

    def get_safety_guidelines(self, grade: int) -> Dict[str, Any]:
        """Get safety guidelines for grade."""
        return {
            "grade": grade,
            "guidelines": [
                "All content must be curriculum-aligned",
                "No violent or harmful content",
                "Age-appropriate language and examples",
                "Respectful and inclusive content",
                "Accurate and factually correct information",
            ],
            "bannedTopics": [
                "Violence", "Discrimination", "Illegal activities",
                "Adult content", "Self-harm"
            ],
            "reportingProcedure": "Flag inappropriate content immediately",
        }
