"""
Content Filtering for DeepTutor

Provides content filtering for age-appropriate and culturally sensitive content.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Set, Tuple


class ContentSafetyLevel(Enum):
    """Content safety levels for different age groups"""
    STRICT = "strict"           # Grade 1-5 (ages 6-10)
    MODERATE = "moderate"       # Grade 6-8 (ages 11-13)
    STANDARD = "standard"       # Grade 9-10 (ages 14-15)
    RELAXED = "relaxed"         # Grade 11-12 (ages 16-18)


class ContentCategory(Enum):
    """Categories of content for filtering"""
    SAFE = "safe"
    EDUCATIONAL = "educational"
    SENSITIVE = "sensitive"
    INAPPROPRIATE = "inappropriate"
    HARMFUL = "harmful"


@dataclass
class FilterResult:
    """Result of content filtering"""
    is_safe: bool
    category: ContentCategory
    confidence: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    filtered_content: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "is_safe": self.is_safe,
            "category": self.category.value,
            "confidence": self.confidence,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "filtered_content": self.filtered_content
        }


class ContentFilter:
    """
    Content filter for ensuring age-appropriate and culturally sensitive content.
    
    This filter is designed specifically for Pakistani educational context.
    """
    
    # Patterns for different types of content (simplified for educational purposes)
    # These patterns catch obvious issues - a production system would use ML models
    
    HARMFUL_PATTERNS = [
        r'\b(violence|kill|murder|attack|weapon|bomb|terrorist)\b',
        r'\b(drug|cocaine|heroin|meth|marijuana)\b',
        r'\b(suicide|self.?harm)\b',
        r'\b(gambling|betting)\b',
    ]
    
    INAPPROPRIATE_PATTERNS = [
        r'\b(dating|romance|boyfriend|girlfriend)\b',
        r'\b(alcohol|beer|wine|vodka|whiskey)\b',
    ]
    
    SENSITIVE_PATTERNS = [
        r'\b(politics|election|government|corruption)\b',
        r'\b(religion|hindu|christian|jew)\b',  # Need careful handling
        r'\b(india|israel|war)\b',
    ]
    
    # Positive educational patterns
    EDUCATIONAL_PATTERNS = [
        r'\b(learn|study|education|school|college|university)\b',
        r'\b(mathematics|science|physics|chemistry|biology)\b',
        r'\b(history|geography|literature|language)\b',
        r'\b(formula|equation|theorem|proof|calculate)\b',
        r'\b(read|write|practice|homework|assignment)\b',
    ]
    
    # Islamic/Cultural keywords to handle with respect
    CULTURAL_KEYWORDS = {
        'allah', 'god', 'prophet', 'muhammad', 'quran', 'islam',
        'mosque', 'prayer', 'ramadan', 'eid', 'hajj', 'zakah'
    }
    
    def __init__(self, safety_level: ContentSafetyLevel = ContentSafetyLevel.STANDARD):
        """
        Initialize content filter.
        
        Args:
            safety_level: The safety level for filtering
        """
        self.safety_level = safety_level
        
        # Compile patterns for efficiency
        self._harmful_re = [re.compile(p, re.IGNORECASE) for p in self.HARMFUL_PATTERNS]
        self._inappropriate_re = [re.compile(p, re.IGNORECASE) for p in self.INAPPROPRIATE_PATTERNS]
        self._sensitive_re = [re.compile(p, re.IGNORECASE) for p in self.SENSITIVE_PATTERNS]
        self._educational_re = [re.compile(p, re.IGNORECASE) for p in self.EDUCATIONAL_PATTERNS]
    
    def filter(self, content: str) -> FilterResult:
        """
        Filter content for safety.
        
        Args:
            content: The content to filter
            
        Returns:
            FilterResult with safety assessment
        """
        issues = []
        suggestions = []
        
        # Check for harmful content
        harmful_matches = self._check_patterns(content, self._harmful_re)
        if harmful_matches:
            issues.append(f"Contains potentially harmful content: {', '.join(harmful_matches[:3])}")
            return FilterResult(
                is_safe=False,
                category=ContentCategory.HARMFUL,
                confidence=0.9,
                issues=issues,
                suggestions=["Please rephrase your question to focus on educational content"],
                filtered_content=self._sanitize_content(content, harmful_matches)
            )
        
        # Check for inappropriate content based on safety level
        if self.safety_level in [ContentSafetyLevel.STRICT, ContentSafetyLevel.MODERATE]:
            inappropriate_matches = self._check_patterns(content, self._inappropriate_re)
            if inappropriate_matches:
                issues.append(f"Contains age-inappropriate content")
                return FilterResult(
                    is_safe=False,
                    category=ContentCategory.INAPPROPRIATE,
                    confidence=0.8,
                    issues=issues,
                    suggestions=["This content may not be suitable for your age group"],
                    filtered_content=self._sanitize_content(content, inappropriate_matches)
                )
        
        # Check for sensitive content
        sensitive_matches = self._check_patterns(content, self._sensitive_re)
        if sensitive_matches and self.safety_level == ContentSafetyLevel.STRICT:
            issues.append(f"Contains sensitive topics")
            suggestions.append("Consider discussing this with a teacher or parent")
        
        # Check for educational content (positive signal)
        educational_matches = self._check_patterns(content, self._educational_re)
        is_educational = len(educational_matches) > 0
        
        # Check cultural/religious content for respectful handling
        cultural_found = self._check_cultural_content(content)
        if cultural_found:
            suggestions.append("Religious and cultural topics will be handled with respect")
        
        # Determine final category and safety
        if is_educational and not issues:
            category = ContentCategory.EDUCATIONAL
            is_safe = True
            confidence = 0.95
        elif sensitive_matches:
            category = ContentCategory.SENSITIVE
            is_safe = True  # Sensitive but not blocked
            confidence = 0.7
        else:
            category = ContentCategory.SAFE
            is_safe = True
            confidence = 0.85
        
        return FilterResult(
            is_safe=is_safe,
            category=category,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
            filtered_content=content
        )
    
    def _check_patterns(self, content: str, patterns: List[re.Pattern]) -> List[str]:
        """Check content against regex patterns"""
        matches = []
        for pattern in patterns:
            found = pattern.findall(content)
            matches.extend(found)
        return list(set(matches))
    
    def _check_cultural_content(self, content: str) -> bool:
        """Check if content contains cultural/religious keywords"""
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in self.CULTURAL_KEYWORDS)
    
    def _sanitize_content(self, content: str, matches: List[str]) -> str:
        """Sanitize content by replacing matched words with asterisks"""
        sanitized = content
        for match in matches:
            replacement = '*' * len(match)
            sanitized = re.sub(re.escape(match), replacement, sanitized, flags=re.IGNORECASE)
        return sanitized
    
    def check_question(self, question: str, grade: int = 9) -> FilterResult:
        """
        Check if a student's question is appropriate.
        
        Args:
            question: The student's question
            grade: The student's grade level (1-12)
            
        Returns:
            FilterResult with assessment
        """
        # Determine safety level based on grade
        if grade <= 5:
            self.safety_level = ContentSafetyLevel.STRICT
        elif grade <= 8:
            self.safety_level = ContentSafetyLevel.MODERATE
        elif grade <= 10:
            self.safety_level = ContentSafetyLevel.STANDARD
        else:
            self.safety_level = ContentSafetyLevel.RELAXED
        
        return self.filter(question)
    
    def check_response(self, response: str, grade: int = 9) -> FilterResult:
        """
        Check if an AI response is appropriate for the student.
        
        Args:
            response: The AI's response
            grade: The student's grade level
            
        Returns:
            FilterResult with assessment
        """
        # Same filtering logic but may have different thresholds for responses
        return self.check_question(response, grade)


def get_content_filter(safety_level: ContentSafetyLevel = ContentSafetyLevel.STANDARD) -> ContentFilter:
    """Get a content filter instance"""
    return ContentFilter(safety_level)
