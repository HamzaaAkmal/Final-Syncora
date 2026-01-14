"""
Safety Checker for DeepTutor

Unified safety checking that combines filtering and validation.
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .filters import ContentFilter, ContentSafetyLevel, FilterResult
from .validator import ContentValidator, ValidationResult


@dataclass
class SafetyCheckResult:
    """Combined result from safety checks"""
    is_safe: bool
    is_valid: bool
    overall_score: float
    filter_result: FilterResult
    validation_result: ValidationResult
    blocked: bool = False
    block_reason: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "is_safe": self.is_safe,
            "is_valid": self.is_valid,
            "overall_score": self.overall_score,
            "blocked": self.blocked,
            "block_reason": self.block_reason,
            "recommendations": self.recommendations,
            "filter_details": self.filter_result.to_dict(),
            "validation_details": self.validation_result.to_dict()
        }


class SafetyChecker:
    """
    Unified safety checker for DeepTutor content.
    
    Combines content filtering and validation to ensure safe, quality educational content.
    """
    
    def __init__(self, grade: int = 9, subject: str = "mathematics"):
        """
        Initialize safety checker.
        
        Args:
            grade: Student's grade level (1-12)
            subject: Subject area
        """
        self.grade = grade
        self.subject = subject
        
        # Determine safety level based on grade
        if grade <= 5:
            safety_level = ContentSafetyLevel.STRICT
        elif grade <= 8:
            safety_level = ContentSafetyLevel.MODERATE
        elif grade <= 10:
            safety_level = ContentSafetyLevel.STANDARD
        else:
            safety_level = ContentSafetyLevel.RELAXED
        
        self.content_filter = ContentFilter(safety_level)
        self.content_validator = ContentValidator()
    
    def check_input(self, user_input: str) -> SafetyCheckResult:
        """
        Check user input (question) for safety and quality.
        
        Args:
            user_input: The user's input/question
            
        Returns:
            SafetyCheckResult with combined assessment
        """
        # Filter for safety
        filter_result = self.content_filter.check_question(user_input, self.grade)
        
        # Validate for quality
        validation_result = self.content_validator.validate_question(user_input)
        
        # Combine results
        overall_score = (filter_result.confidence + validation_result.score) / 2
        is_safe = filter_result.is_safe
        is_valid = validation_result.is_valid
        
        # Determine if content should be blocked
        blocked = not is_safe
        block_reason = None
        if blocked:
            block_reason = filter_result.issues[0] if filter_result.issues else "Content flagged as unsafe"
        
        # Compile recommendations
        recommendations = []
        recommendations.extend(filter_result.suggestions)
        recommendations.extend(validation_result.suggestions)
        
        return SafetyCheckResult(
            is_safe=is_safe,
            is_valid=is_valid,
            overall_score=overall_score,
            filter_result=filter_result,
            validation_result=validation_result,
            blocked=blocked,
            block_reason=block_reason,
            recommendations=list(set(recommendations))  # Remove duplicates
        )
    
    def check_output(self, ai_response: str, user_input: str = "") -> SafetyCheckResult:
        """
        Check AI output (response) for safety and quality.
        
        Args:
            ai_response: The AI's response
            user_input: The original user input (for context)
            
        Returns:
            SafetyCheckResult with combined assessment
        """
        # Filter for safety
        filter_result = self.content_filter.check_response(ai_response, self.grade)
        
        # Validate for quality
        validation_result = self.content_validator.validate_response(ai_response, user_input)
        
        # Check curriculum alignment
        alignment_result = self.content_validator.validate_curriculum_alignment(
            ai_response, self.grade, self.subject
        )
        
        # Combine results
        overall_score = (
            filter_result.confidence * 0.4 +
            validation_result.score * 0.3 +
            alignment_result.score * 0.3
        )
        
        is_safe = filter_result.is_safe
        is_valid = validation_result.is_valid and alignment_result.is_valid
        
        # Determine if content should be blocked
        blocked = not is_safe
        block_reason = None
        if blocked:
            block_reason = filter_result.issues[0] if filter_result.issues else "Content flagged as unsafe"
        
        # Compile recommendations
        recommendations = []
        recommendations.extend(filter_result.suggestions)
        recommendations.extend(validation_result.suggestions)
        recommendations.extend(alignment_result.suggestions)
        
        return SafetyCheckResult(
            is_safe=is_safe,
            is_valid=is_valid,
            overall_score=overall_score,
            filter_result=filter_result,
            validation_result=validation_result,
            blocked=blocked,
            block_reason=block_reason,
            recommendations=list(set(recommendations))
        )
    
    def update_context(self, grade: int = None, subject: str = None):
        """
        Update the checker's context.
        
        Args:
            grade: New grade level
            subject: New subject
        """
        if grade:
            self.grade = grade
            # Update safety level
            if grade <= 5:
                safety_level = ContentSafetyLevel.STRICT
            elif grade <= 8:
                safety_level = ContentSafetyLevel.MODERATE
            elif grade <= 10:
                safety_level = ContentSafetyLevel.STANDARD
            else:
                safety_level = ContentSafetyLevel.RELAXED
            self.content_filter.safety_level = safety_level
        
        if subject:
            self.subject = subject


# Singleton instance for the checker
_safety_checker: Optional[SafetyChecker] = None


def get_safety_checker(grade: int = 9, subject: str = "mathematics") -> SafetyChecker:
    """
    Get the safety checker instance.
    
    Args:
        grade: Student's grade level
        subject: Subject area
        
    Returns:
        SafetyChecker instance
    """
    global _safety_checker
    
    if _safety_checker is None:
        _safety_checker = SafetyChecker(grade, subject)
    else:
        _safety_checker.update_context(grade, subject)
    
    return _safety_checker


def check_content_safety(
    content: str,
    content_type: str = "input",
    grade: int = 9,
    subject: str = "mathematics"
) -> SafetyCheckResult:
    """
    Convenience function to check content safety.
    
    Args:
        content: The content to check
        content_type: Either "input" (user question) or "output" (AI response)
        grade: Student's grade level
        subject: Subject area
        
    Returns:
        SafetyCheckResult
    """
    checker = get_safety_checker(grade, subject)
    
    if content_type == "input":
        return checker.check_input(content)
    else:
        return checker.check_output(content)
