"""
Student API Router
==================

API endpoints for student management, including:
- Student profiles
- Progress tracking
- Assessments
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.student import (
    StudentManager,
    get_student_manager,
    AssessmentEngine,
    get_assessment_engine,
)

router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class CreateStudentRequest(BaseModel):
    name: str
    grade: int = 9
    language: str = "ur"
    name_ur: str = ""
    board: str = "punjab"
    subjects: Optional[List[str]] = None


class UpdateStudentRequest(BaseModel):
    name: Optional[str] = None
    name_ur: Optional[str] = None
    grade: Optional[int] = None
    language: Optional[str] = None
    board: Optional[str] = None
    subjects: Optional[List[str]] = None


class UpdateProgressRequest(BaseModel):
    topic_id: str
    subject_id: str = ""
    correct: bool = False
    time_minutes: int = 0
    hints_used: int = 0
    assessment_score: Optional[float] = None


class CreateAssessmentRequest(BaseModel):
    assessment_type: str = "pre_assessment"  # pre_assessment, quiz, practice
    subject_id: Optional[str] = None
    topic_ids: Optional[List[str]] = None
    grade: int = 9
    language: str = "ur"
    num_questions: int = 10
    adaptive: bool = True


class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer: str


# ============================================================================
# Student Profile Endpoints
# ============================================================================

@router.post("/students")
async def create_student(request: CreateStudentRequest):
    """
    Create a new student profile.
    """
    manager = get_student_manager()
    profile = manager.create_student(
        name=request.name,
        grade=request.grade,
        language=request.language,
        name_ur=request.name_ur,
        board=request.board,
        subjects=request.subjects,
    )
    return profile.to_dict()


@router.get("/students")
async def list_students():
    """
    List all students.
    """
    manager = get_student_manager()
    return manager.list_students()


@router.get("/students/{student_id}")
async def get_student(student_id: str):
    """
    Get a student profile by ID.
    """
    manager = get_student_manager()
    profile = manager.get_student(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    return profile.to_dict()


@router.put("/students/{student_id}")
async def update_student(student_id: str, request: UpdateStudentRequest):
    """
    Update a student profile.
    """
    manager = get_student_manager()
    
    updates = request.model_dump(exclude_none=True)
    profile = manager.update_student(student_id, **updates)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return profile.to_dict()


@router.delete("/students/{student_id}")
async def delete_student(student_id: str):
    """
    Delete a student profile.
    """
    manager = get_student_manager()
    success = manager.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}


# ============================================================================
# Progress Tracking Endpoints
# ============================================================================

@router.get("/students/{student_id}/progress")
async def get_all_progress(
    student_id: str,
    subject_id: Optional[str] = Query(None, description="Filter by subject"),
):
    """
    Get all progress for a student.
    """
    manager = get_student_manager()
    
    profile = manager.get_student(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    progress = manager.get_all_progress(student_id, subject_id=subject_id)
    return progress


@router.get("/students/{student_id}/progress/{topic_id}")
async def get_topic_progress(student_id: str, topic_id: str):
    """
    Get progress for a specific topic.
    """
    manager = get_student_manager()
    progress = manager.get_progress(student_id, topic_id)
    if not progress:
        return {
            "topic_id": topic_id,
            "status": "not_started",
            "mastery_score": 0,
        }
    return progress.to_dict()


@router.post("/students/{student_id}/progress")
async def update_progress(student_id: str, request: UpdateProgressRequest):
    """
    Update progress on a topic.
    """
    manager = get_student_manager()
    
    profile = manager.get_student(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    progress = manager.update_progress(
        student_id=student_id,
        topic_id=request.topic_id,
        subject_id=request.subject_id,
        correct=request.correct,
        time_minutes=request.time_minutes,
        hints_used=request.hints_used,
        assessment_score=request.assessment_score,
    )
    return progress.to_dict()


# ============================================================================
# Statistics & Analytics Endpoints
# ============================================================================

@router.get("/students/{student_id}/stats")
async def get_student_stats(student_id: str):
    """
    Get comprehensive stats for a student in dashboard-friendly format.
    """
    manager = get_student_manager()
    
    profile = manager.get_student(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    base_stats = manager.get_student_stats(student_id)
    
    # Calculate subject progress for dashboard
    # Get all progress entries grouped by subject
    all_progress = manager.get_all_progress(student_id)
    
    # Group progress by subject
    subject_data: dict = {}
    for progress in all_progress:
        subj = progress.get("subject_id", "general")
        if subj not in subject_data:
            subject_data[subj] = {
                "total": 0,
                "completed": 0,
                "mastery_sum": 0,
            }
        subject_data[subj]["total"] += 1
        if progress.get("mastery_score", 0) >= 0.7:
            subject_data[subj]["completed"] += 1
        subject_data[subj]["mastery_sum"] += progress.get("mastery_score", 0)
    
    # Subject name mappings
    subject_names = {
        "math_9": {"en": "Mathematics", "ur": "ریاضی"},
        "science_9": {"en": "Science", "ur": "سائنس"},
        "english_9": {"en": "English", "ur": "انگریزی"},
        "urdu_9": {"en": "Urdu", "ur": "اردو"},
        "general": {"en": "General", "ur": "عمومی"},
    }
    
    # Build subjects progress array
    subjects_progress = []
    for subj_id, data in subject_data.items():
        names = subject_names.get(subj_id, {"en": subj_id, "ur": subj_id})
        avg_mastery = data["mastery_sum"] / data["total"] if data["total"] > 0 else 0
        subjects_progress.append({
            "subject": names["en"],
            "subject_ur": names["ur"],
            "mastery_score": avg_mastery,
            "topics_completed": data["completed"],
            "total_topics": data["total"],
        })
    
    # If no progress yet, return default subjects
    if not subjects_progress:
        for subj_id, names in subject_names.items():
            if subj_id != "general":
                subjects_progress.append({
                    "subject": names["en"],
                    "subject_ur": names["ur"],
                    "mastery_score": 0,
                    "topics_completed": 0,
                    "total_topics": 10,
                })
    
    # Calculate average score
    total_attempts = base_stats.get("total_attempts", 0)
    accuracy = base_stats.get("accuracy", 0)
    average_score = accuracy * 100 if total_attempts > 0 else 0
    
    return {
        "total_study_time": base_stats.get("total_time_minutes", 0),
        "questions_asked": total_attempts,
        "assessments_completed": base_stats.get("mastered_count", 0) + base_stats.get("proficient_count", 0),
        "average_score": average_score,
        "subjects_progress": subjects_progress,
        # Additional stats
        "current_streak": base_stats.get("current_streak", 0),
        "points": base_stats.get("points", 0),
        "badges": base_stats.get("badges", []),
        "weak_topics": base_stats.get("weak_topics", []),
        "strong_topics": base_stats.get("strong_topics", []),
    }


@router.get("/students/{student_id}/recommendations")
async def get_recommendations(
    student_id: str,
    subject_id: Optional[str] = Query(None, description="Filter by subject"),
    limit: int = Query(5, description="Maximum recommendations"),
):
    """
    Get topic recommendations for a student.
    """
    manager = get_student_manager()
    
    profile = manager.get_student(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    recommendations = manager.get_recommendations(
        student_id=student_id,
        subject_id=subject_id,
        limit=limit,
    )
    return recommendations


@router.post("/students/{student_id}/streak")
async def update_streak(student_id: str):
    """
    Update the daily streak for a student.
    """
    manager = get_student_manager()
    
    profile = manager.get_student(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    streak = manager.update_streak(student_id)
    return {"streak": streak}


@router.post("/students/{student_id}/points")
async def award_points(student_id: str, points: int = Query(..., description="Points to award")):
    """
    Award points to a student.
    """
    manager = get_student_manager()
    
    profile = manager.get_student(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    total = manager.award_points(student_id, points)
    return {"total_points": total}


# ============================================================================
# Assessment Endpoints
# ============================================================================

@router.post("/students/{student_id}/assessments")
async def create_assessment(student_id: str, request: CreateAssessmentRequest):
    """
    Create a new assessment for a student.
    """
    manager = get_student_manager()
    engine = get_assessment_engine()
    
    profile = manager.get_student(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if request.assessment_type == "pre_assessment":
        if not request.subject_id:
            raise HTTPException(status_code=400, detail="subject_id required for pre-assessment")
        assessment = await engine.create_pre_assessment(
            student_id=student_id,
            subject_id=request.subject_id,
            grade=request.grade,
            language=request.language,
            num_questions=request.num_questions,
        )
    elif request.assessment_type == "quiz":
        if not request.topic_ids or len(request.topic_ids) == 0:
            raise HTTPException(status_code=400, detail="topic_ids required for quiz")
        assessment = await engine.create_topic_quiz(
            student_id=student_id,
            topic_id=request.topic_ids[0],
            language=request.language,
            num_questions=request.num_questions,
            adaptive=request.adaptive,
        )
    elif request.assessment_type == "practice":
        if not request.topic_ids:
            raise HTTPException(status_code=400, detail="topic_ids required for practice")
        assessment = await engine.create_practice(
            student_id=student_id,
            topic_ids=request.topic_ids,
            language=request.language,
            num_questions=request.num_questions,
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid assessment type")
    
    return assessment.to_dict()


@router.get("/students/{student_id}/assessments")
async def list_assessments(
    student_id: str,
    limit: int = Query(10, description="Maximum assessments"),
):
    """
    Get recent assessments for a student.
    """
    engine = get_assessment_engine()
    assessments = engine.get_student_assessments(student_id, limit=limit)
    return assessments


@router.post("/assessments/{assessment_id}/start")
async def start_assessment(assessment_id: str):
    """
    Start an assessment.
    """
    engine = get_assessment_engine()
    assessment = engine.start_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment.to_dict()


@router.post("/assessments/{assessment_id}/submit")
async def submit_answer(assessment_id: str, request: SubmitAnswerRequest):
    """
    Submit an answer to a question.
    """
    engine = get_assessment_engine()
    result = engine.submit_answer(
        assessment_id=assessment_id,
        question_id=request.question_id,
        answer=request.answer,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/assessments/{assessment_id}/complete")
async def complete_assessment(assessment_id: str):
    """
    Complete an assessment and get results.
    """
    engine = get_assessment_engine()
    assessment = engine.complete_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment.to_dict()


# ============================================================================
# Prerequisite Check
# ============================================================================

@router.get("/students/{student_id}/check-prerequisites/{topic_id}")
async def check_prerequisites(student_id: str, topic_id: str):
    """
    Check if student has mastered prerequisites for a topic.
    """
    engine = get_assessment_engine()
    result = engine.check_prerequisites(student_id, topic_id)
    return result


@router.get("/students/{student_id}/recommended-difficulty/{topic_id}")
async def get_recommended_difficulty(student_id: str, topic_id: str):
    """
    Get recommended difficulty level for a student on a topic.
    """
    engine = get_assessment_engine()
    difficulty = engine.get_recommended_difficulty(student_id, topic_id)
    return {"difficulty": difficulty}
