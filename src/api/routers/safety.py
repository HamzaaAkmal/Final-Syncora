"""
Safety API Router for DeepTutor

Provides API endpoints for content safety checking.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from src.safety import ContentFilter, ContentSafetyLevel, ContentValidator, SafetyChecker


router = APIRouter()


# Request/Response Models
class ContentCheckRequest(BaseModel):
    """Request model for content safety check"""
    content: str = Field(..., description="Content to check")
    content_type: str = Field(default="input", description="Type: 'input' or 'output'")
    grade: int = Field(default=9, ge=1, le=12, description="Student grade level")
    subject: str = Field(default="mathematics", description="Subject area")


class SafetyCheckResponse(BaseModel):
    """Response model for safety check"""
    is_safe: bool
    is_valid: bool
    overall_score: float
    blocked: bool
    block_reason: Optional[str]
    recommendations: list
    details: dict


class QuickCheckRequest(BaseModel):
    """Quick check request for just filtering"""
    content: str = Field(..., description="Content to check")
    grade: int = Field(default=9, ge=1, le=12, description="Student grade level")


class QuickCheckResponse(BaseModel):
    """Quick check response"""
    is_safe: bool
    category: str
    confidence: float
    issues: list


# Endpoints
@router.post("/check", response_model=SafetyCheckResponse)
async def check_content_safety(request: ContentCheckRequest):
    """
    Check content for safety and quality.
    
    Performs comprehensive safety and quality checks on content.
    """
    try:
        checker = SafetyChecker(grade=request.grade, subject=request.subject)
        
        if request.content_type == "input":
            result = checker.check_input(request.content)
        else:
            result = checker.check_output(request.content)
        
        return SafetyCheckResponse(
            is_safe=result.is_safe,
            is_valid=result.is_valid,
            overall_score=result.overall_score,
            blocked=result.blocked,
            block_reason=result.block_reason,
            recommendations=result.recommendations,
            details=result.to_dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-check", response_model=QuickCheckResponse)
async def quick_safety_check(request: QuickCheckRequest):
    """
    Quick safety check for filtering only.
    
    Fast check without full validation - good for real-time filtering.
    """
    try:
        # Determine safety level based on grade
        if request.grade <= 5:
            safety_level = ContentSafetyLevel.STRICT
        elif request.grade <= 8:
            safety_level = ContentSafetyLevel.MODERATE
        elif request.grade <= 10:
            safety_level = ContentSafetyLevel.STANDARD
        else:
            safety_level = ContentSafetyLevel.RELAXED
        
        content_filter = ContentFilter(safety_level)
        result = content_filter.filter(request.content)
        
        return QuickCheckResponse(
            is_safe=result.is_safe,
            category=result.category.value,
            confidence=result.confidence,
            issues=result.issues
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/levels")
async def get_safety_levels():
    """
    Get available safety levels and their grade ranges.
    """
    return {
        "levels": [
            {
                "level": "strict",
                "grades": "1-5",
                "age_range": "6-10",
                "description": "Maximum filtering for young learners"
            },
            {
                "level": "moderate",
                "grades": "6-8",
                "age_range": "11-13",
                "description": "Balanced filtering for pre-teens"
            },
            {
                "level": "standard",
                "grades": "9-10",
                "age_range": "14-15",
                "description": "Standard filtering for teenagers"
            },
            {
                "level": "relaxed",
                "grades": "11-12",
                "age_range": "16-18",
                "description": "Minimal filtering for young adults"
            }
        ]
    }


@router.post("/validate-question")
async def validate_question(request: QuickCheckRequest):
    """
    Validate a student's question for quality.
    """
    try:
        validator = ContentValidator()
        result = validator.validate_question(request.content)
        
        return {
            "is_valid": result.is_valid,
            "score": result.score,
            "issues": result.issues,
            "warnings": result.warnings,
            "suggestions": result.suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-response")
async def validate_response(
    content: str,
    question: str = "",
    grade: int = 9,
    subject: str = "mathematics"
):
    """
    Validate an AI response for quality and curriculum alignment.
    """
    try:
        validator = ContentValidator()
        
        # Validate response quality
        response_result = validator.validate_response(content, question)
        
        # Validate curriculum alignment
        alignment_result = validator.validate_curriculum_alignment(content, grade, subject)
        
        return {
            "quality": {
                "is_valid": response_result.is_valid,
                "score": response_result.score,
                "issues": response_result.issues,
                "warnings": response_result.warnings,
                "suggestions": response_result.suggestions
            },
            "curriculum_alignment": {
                "is_valid": alignment_result.is_valid,
                "score": alignment_result.score,
                "warnings": alignment_result.warnings,
                "suggestions": alignment_result.suggestions
            },
            "overall_score": (response_result.score + alignment_result.score) / 2
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
