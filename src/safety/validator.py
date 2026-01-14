"""
Content Validator for Syncora

Validates educational content for quality and appropriateness.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class ValidationResult:
    """Result of content validation"""
    is_valid: bool
    score: float  # 0.0 to 1.0
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "issues": self.issues,
            "warnings": self.warnings,
            "suggestions": self.suggestions
        }


class ContentValidator:
    """
    Validates educational content for quality, accuracy, and appropriateness.
    """
    
    # Minimum content length thresholds
    MIN_QUESTION_LENGTH = 10
    MAX_QUESTION_LENGTH = 1000
    MIN_RESPONSE_LENGTH = 50
    MAX_RESPONSE_LENGTH = 10000
    
    # Quality indicators
    QUALITY_INDICATORS = [
        r'\b(because|therefore|thus|hence|as a result)\b',  # Explanatory
        r'\b(for example|such as|like|consider)\b',  # Examples
        r'\b(step \d|first|second|third|finally)\b',  # Structured
        r'\$[^$]+\$',  # Math formulas
        r'\b(formula|equation|theorem|definition)\b',  # Technical terms
    ]
    
    # Poor quality indicators
    POOR_QUALITY_INDICATORS = [
        r'^(idk|dunno|whatever|ok)\s*$',  # Low effort responses
        r'(.)\1{4,}',  # Repeated characters
        r'\b(um+|uh+|er+)\b',  # Filler words
    ]
    
    def __init__(self):
        """Initialize content validator"""
        self._quality_re = [re.compile(p, re.IGNORECASE) for p in self.QUALITY_INDICATORS]
        self._poor_quality_re = [re.compile(p, re.IGNORECASE) for p in self.POOR_QUALITY_INDICATORS]
    
    def validate_question(self, question: str) -> ValidationResult:
        """
        Validate a student's question.
        
        Args:
            question: The question to validate
            
        Returns:
            ValidationResult with assessment
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check length
        if len(question) < self.MIN_QUESTION_LENGTH:
            issues.append("Question is too short. Please provide more details.")
            suggestions.append("Add more context to help us understand your question better.")
        elif len(question) > self.MAX_QUESTION_LENGTH:
            warnings.append("Question is quite long. Consider breaking it into smaller parts.")
        
        # Check for poor quality
        poor_matches = self._check_patterns(question, self._poor_quality_re)
        if poor_matches:
            issues.append("Please ask a clear, specific question.")
            suggestions.append("Try to be more specific about what you want to learn.")
        
        # Check for educational context
        quality_matches = self._check_patterns(question, self._quality_re)
        if quality_matches:
            # Good quality indicators present
            pass
        
        # Calculate score
        base_score = 0.7
        if len(question) >= self.MIN_QUESTION_LENGTH:
            base_score += 0.1
        if len(question) <= self.MAX_QUESTION_LENGTH:
            base_score += 0.05
        if quality_matches:
            base_score += 0.1
        if poor_matches:
            base_score -= 0.3
        
        score = max(0.0, min(1.0, base_score))
        is_valid = score >= 0.5 and not issues
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def validate_response(self, response: str, question: str = "") -> ValidationResult:
        """
        Validate an AI response.
        
        Args:
            response: The response to validate
            question: The original question (for context)
            
        Returns:
            ValidationResult with assessment
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check length
        if len(response) < self.MIN_RESPONSE_LENGTH:
            warnings.append("Response might be too brief for a complete explanation.")
        elif len(response) > self.MAX_RESPONSE_LENGTH:
            warnings.append("Response is quite long. Consider summarizing key points.")
        
        # Check quality indicators
        quality_matches = self._check_patterns(response, self._quality_re)
        
        # Check for explanatory content
        has_explanation = bool(re.search(r'\b(because|therefore|since|as)\b', response, re.I))
        has_examples = bool(re.search(r'\b(example|for instance|such as)\b', response, re.I))
        has_structure = bool(re.search(r'\b(step|first|then|finally)\b', response, re.I))
        has_math = bool(re.search(r'\$[^$]+\$|\\\(|\\\[', response))
        
        # Quality scoring
        base_score = 0.5
        
        if len(response) >= self.MIN_RESPONSE_LENGTH:
            base_score += 0.1
        if has_explanation:
            base_score += 0.1
        if has_examples:
            base_score += 0.1
        if has_structure:
            base_score += 0.1
        if has_math:
            base_score += 0.1
        
        # Suggestions for improvement
        if not has_explanation:
            suggestions.append("Consider adding explanations for 'why' things work")
        if not has_examples:
            suggestions.append("Examples can help students understand better")
        if not has_structure:
            suggestions.append("Breaking down into steps aids comprehension")
        
        score = max(0.0, min(1.0, base_score))
        is_valid = score >= 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def validate_curriculum_alignment(
        self,
        content: str,
        grade: int,
        subject: str
    ) -> ValidationResult:
        """
        Validate content alignment with curriculum.
        
        Args:
            content: The content to validate
            grade: Expected grade level
            subject: Expected subject
            
        Returns:
            ValidationResult with alignment assessment
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Grade-level vocabulary check (simplified)
        # Higher grades should have more complex vocabulary
        
        avg_word_length = self._calculate_avg_word_length(content)
        
        # Expected complexity by grade
        expected_complexity = {
            9: 5.0,
            10: 5.5,
            11: 6.0,
            12: 6.5
        }
        
        expected = expected_complexity.get(grade, 5.0)
        
        if avg_word_length < expected - 1.5:
            warnings.append(f"Content may be too simple for Grade {grade}")
            suggestions.append("Consider using more subject-specific terminology")
        elif avg_word_length > expected + 2.0:
            warnings.append(f"Content may be too complex for Grade {grade}")
            suggestions.append("Consider simplifying language for better understanding")
        
        # Subject-specific checks
        subject_keywords = self._get_subject_keywords(subject)
        keyword_count = sum(1 for kw in subject_keywords if kw.lower() in content.lower())
        
        if keyword_count == 0:
            warnings.append(f"Content may not be well-aligned with {subject}")
            suggestions.append(f"Include more {subject}-specific terminology")
        
        # Calculate score
        base_score = 0.7
        if keyword_count > 0:
            base_score += min(0.2, keyword_count * 0.05)
        if avg_word_length >= expected - 0.5 and avg_word_length <= expected + 1.0:
            base_score += 0.1
        
        score = max(0.0, min(1.0, base_score))
        is_valid = score >= 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _check_patterns(self, content: str, patterns: List[re.Pattern]) -> List[str]:
        """Check content against patterns"""
        matches = []
        for pattern in patterns:
            found = pattern.findall(content)
            matches.extend(found)
        return list(set(matches))
    
    def _calculate_avg_word_length(self, content: str) -> float:
        """Calculate average word length"""
        words = re.findall(r'\b\w+\b', content)
        if not words:
            return 0.0
        return sum(len(w) for w in words) / len(words)
    
    def _get_subject_keywords(self, subject: str) -> List[str]:
        """Get keywords for a subject"""
        keywords = {
            "mathematics": [
                "equation", "formula", "calculate", "solve", "variable",
                "function", "graph", "theorem", "proof", "algebra",
                "geometry", "trigonometry", "calculus", "derivative", "integral"
            ],
            "science": [
                "experiment", "hypothesis", "theory", "energy", "matter",
                "force", "motion", "cell", "atom", "molecule",
                "reaction", "element", "compound", "physics", "chemistry"
            ],
            "english": [
                "grammar", "vocabulary", "sentence", "paragraph", "essay",
                "literature", "poetry", "prose", "comprehension", "writing",
                "reading", "speaking", "listening", "communication"
            ],
            "urdu": [
                "زبان", "گرامر", "الفاظ", "جملہ", "مضمون",
                "شاعری", "نثر", "ادب", "تحریر", "پڑھائی"
            ]
        }
        return keywords.get(subject, [])


def get_content_validator() -> ContentValidator:
    """Get a content validator instance"""
    return ContentValidator()
