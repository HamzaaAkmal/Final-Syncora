"""
Curriculum API Router
=====================

API endpoints for curriculum management, including:
- Subjects, chapters, topics
- Curriculum search and alignment
- Learning paths
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

from src.curriculum import CurriculumManager, get_curriculum_manager

router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class SubjectResponse(BaseModel):
    id: str
    name: str
    name_ur: str
    icon: str
    grades: List[int]
    description: str
    description_ur: str


class TopicResponse(BaseModel):
    id: str
    name: str
    name_ur: str
    chapter_id: str
    subject_id: str
    grade: int
    difficulty: str
    estimated_hours: float
    prerequisites: List[str]


class ChapterResponse(BaseModel):
    id: str
    name: str
    name_ur: str
    subject_id: str
    grade: int
    order: int
    topic_count: int


class SearchResult(BaseModel):
    id: str
    name: str
    name_ur: str
    subject_id: str
    grade: int
    search_score: int


class LearningPathItem(BaseModel):
    id: str
    name: str
    name_ur: str
    order: int
    is_prerequisite: bool


# ============================================================================
# Subject Endpoints
# ============================================================================

@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(
    grade: Optional[int] = Query(None, description="Filter by grade (1-12)"),
    board: Optional[str] = Query(None, description="Filter by curriculum board"),
):
    """
    Get all subjects, optionally filtered by grade and board.
    """
    manager = get_curriculum_manager()
    subjects = manager.get_subjects(grade=grade)
    return subjects


@router.get("/subjects/{subject_id}")
async def get_subject(subject_id: str):
    """
    Get a specific subject by ID.
    """
    manager = get_curriculum_manager()
    subject = manager.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


# ============================================================================
# Chapter Endpoints
# ============================================================================

@router.get("/subjects/{subject_id}/grades/{grade}/chapters")
async def get_chapters(subject_id: str, grade: int):
    """
    Get chapters for a subject and grade.
    """
    manager = get_curriculum_manager()
    chapters = manager.get_chapters(subject_id=subject_id, grade=grade)
    return chapters


@router.get("/chapters/{chapter_id}")
async def get_chapter(chapter_id: str):
    """
    Get a specific chapter by ID.
    """
    manager = get_curriculum_manager()
    chapter = manager.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


# ============================================================================
# Topic Endpoints
# ============================================================================

@router.get("/topics")
async def get_topics(
    subject_id: Optional[str] = Query(None, description="Filter by subject"),
    grade: Optional[int] = Query(None, description="Filter by grade"),
    chapter_id: Optional[str] = Query(None, description="Filter by chapter"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
):
    """
    Get topics with optional filters.
    """
    manager = get_curriculum_manager()
    topics = manager.get_topics(
        subject_id=subject_id,
        grade=grade,
        chapter_id=chapter_id,
    )
    
    if difficulty:
        topics = [t for t in topics if t.get("difficulty") == difficulty]
    
    return topics


@router.get("/topics/{topic_id}")
async def get_topic(topic_id: str):
    """
    Get a specific topic by ID.
    """
    manager = get_curriculum_manager()
    topic = manager.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.get("/topics/{topic_id}/prerequisites")
async def get_prerequisites(topic_id: str):
    """
    Get prerequisite topics for a given topic.
    """
    manager = get_curriculum_manager()
    prerequisites = manager.get_prerequisites(topic_id)
    return prerequisites


@router.get("/topics/{topic_id}/learning-path")
async def get_learning_path(
    topic_id: str,
    include_prerequisites: bool = Query(True, description="Include prerequisites"),
):
    """
    Get a learning path for a topic.
    """
    manager = get_curriculum_manager()
    path = manager.get_learning_path(
        topic_id=topic_id,
        include_prerequisites=include_prerequisites,
    )
    return path


# ============================================================================
# Search Endpoints
# ============================================================================

@router.get("/search")
async def search_topics(
    q: str = Query(..., description="Search query"),
    subject_id: Optional[str] = Query(None, description="Filter by subject"),
    grade: Optional[int] = Query(None, description="Filter by grade"),
    language: str = Query("en", description="Search language (en/ur)"),
    limit: int = Query(10, description="Maximum results"),
):
    """
    Search topics by keyword.
    """
    manager = get_curriculum_manager()
    results = manager.search_topics(
        query=q,
        subject_id=subject_id,
        grade=grade,
        language=language,
        limit=limit,
    )
    return results


@router.post("/align")
async def align_content(
    content: str,
    subject_id: Optional[str] = None,
    grade: Optional[int] = None,
):
    """
    Find curriculum topics that align with given content.
    """
    manager = get_curriculum_manager()
    results = manager.align_content_to_curriculum(
        content=content,
        subject_id=subject_id,
        grade=grade,
    )
    return results


# ============================================================================
# Summary Endpoints
# ============================================================================

@router.get("/grades/{grade}/summary")
async def get_grade_summary(
    grade: int,
    language: str = Query("en", description="Language for text"),
):
    """
    Get a summary of all subjects and topics for a grade.
    """
    manager = get_curriculum_manager()
    summary = manager.get_grade_curriculum_summary(
        grade=grade,
        language=language,
    )
    return summary


@router.get("/stats")
async def get_curriculum_stats(
    subject_id: Optional[str] = Query(None, description="Filter by subject"),
    grade: Optional[int] = Query(None, description="Filter by grade"),
):
    """
    Get curriculum statistics.
    """
    manager = get_curriculum_manager()
    stats = manager.get_curriculum_stats(
        subject_id=subject_id,
        grade=grade,
    )
    return stats


# ============================================================================
# Grade & Board Info
# ============================================================================

@router.get("/grades")
async def get_grades():
    """
    Get available grade levels.
    """
    return {
        "grades": list(range(1, 13)),
        "primary": list(range(1, 6)),
        "middle": list(range(6, 9)),
        "secondary": list(range(9, 11)),
        "higher_secondary": list(range(11, 13)),
    }


@router.get("/boards")
async def get_boards():
    """
    Get available curriculum boards.
    """
    return {
        "boards": [
            {"id": "national", "name": "National Curriculum", "name_ur": "قومی نصاب"},
            {"id": "punjab", "name": "Punjab (PCTB)", "name_ur": "پنجاب"},
            {"id": "sindh", "name": "Sindh", "name_ur": "سندھ"},
            {"id": "kpk", "name": "KPK", "name_ur": "خیبر پختونخوا"},
            {"id": "balochistan", "name": "Balochistan", "name_ur": "بلوچستان"},
            {"id": "federal", "name": "Federal", "name_ur": "وفاقی"},
        ]
    }


# ============================================================================
# Topic Learning Content Generation
# ============================================================================

class TopicLearningRequest(BaseModel):
    topic_id: str
    language: str = "en"  # "en" or "ur"
    grade: int = 9


@router.post("/topics/{topic_id}/learn")
async def generate_topic_learning_content(
    topic_id: str,
    language: str = Query("en", description="Language: 'en' or 'ur'"),
    difficulty: str = Query("medium", description="Difficulty: 'easy', 'medium', or 'hard'"),
):
    """
    Generate learning content for a specific topic using LLM.
    Returns a streaming response with the generated content.
    """
    from src.services.llm import stream as llm_stream, complete as llm_complete
    import json
    
    manager = get_curriculum_manager()
    topic = manager.get_topic(topic_id)
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get topic name based on language
    topic_name = topic.get("name_ur", topic.get("name")) if language == "ur" else topic.get("name")
    subject_id = topic.get("subject_id", "")
    grade = topic.get("grade", 9)
    
    # Difficulty level descriptions
    difficulty_levels = {
        "easy": {
            "en": "Use very simple language, basic examples, and focus on fundamental understanding. Avoid complex terms.",
            "ur": "بہت آسان زبان استعمال کریں، بنیادی مثالیں دیں، اور بنیادی سمجھ پر توجہ دیں۔ مشکل الفاظ سے پرہیز کریں۔"
        },
        "medium": {
            "en": "Use moderate complexity with balanced examples. Include some challenging concepts but explain clearly.",
            "ur": "درمیانی پیچیدگی کے ساتھ متوازن مثالیں استعمال کریں۔ کچھ مشکل تصورات شامل کریں لیکن واضح طور پر سمجھائیں۔"
        },
        "hard": {
            "en": "Use advanced concepts, challenging examples, and include competitive exam style questions. Push the student's understanding.",
            "ur": "اعلی تصورات، مشکل مثالیں، اور مقابلے کے امتحان کے انداز کے سوالات شامل کریں۔ طالب علم کی سمجھ کو آگے بڑھائیں۔"
        }
    }
    
    difficulty_instruction = difficulty_levels.get(difficulty, difficulty_levels["medium"])[language]
    
    # Build the prompt based on language
    if language == "ur":
        system_prompt = "آپ ایک ماہر پاکستانی نصابی استاد ہیں۔ طلباء کے لیے آسان اور واضح زبان میں تعلیمی مواد تیار کریں۔"
        prompt = f"""براہ کرم "{topic_name}" کے موضوع پر PCTB پاکستانی نصاب (گریڈ {grade}) کے مطابق ایک تفصیلی سبق لکھیں۔

سطح کی ہدایت: {difficulty_instruction}

اس میں شامل کریں:

## 1. تعارف اور اہمیت
اس موضوع کا تعارف اور یہ کیوں اہم ہے۔

## 2. بنیادی تصورات
اہم تصورات اور ان کی تعریفیں۔

## 3. اہم نکات اور فارمولے
یاد رکھنے کے لیے اہم نکات۔

## 4. حل شدہ مثالیں
قدم بہ قدم حل شدہ سوالات۔

## 5. مشق کے سوالات
طلباء کی مشق کے لیے سوالات۔

براہ کرم آسان زبان استعمال کریں تاکہ طلباء آسانی سے سمجھ سکیں۔ ریاضی کے فارمولوں کے لیے LaTeX استعمال کریں۔"""
    else:
        system_prompt = "You are an expert Pakistani curriculum teacher. Create educational content that is clear, engaging, and aligned with PCTB standards."
        prompt = f"""Please write a detailed lesson on the topic "{topic_name}" aligned with PCTB Pakistani curriculum for Grade {grade}.

Difficulty Level Instruction: {difficulty_instruction}

Include the following sections:

## 1. Introduction and Importance
Introduce the topic and explain why it's important.

## 2. Core Concepts
Key concepts and their definitions.

## 3. Key Points and Formulas
Important points to remember, formulas if applicable.

## 4. Solved Examples
Step-by-step solved examples.

## 5. Practice Questions
Questions for students to practice.

Please use simple language so students can easily understand. Use LaTeX for any mathematical formulas."""

    async def generate_stream():
        """Generate content stream from LLM."""
        try:
            # Use streaming LLM function
            async for chunk in llm_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=4000
            ):
                if chunk:
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            yield "data: {\"done\": true}\n\n"
            
        except Exception as e:
            # If streaming fails, try non-streaming
            try:
                response = await llm_complete(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=4000
                )
                if response:
                    # Send in chunks for smoother UI
                    chunk_size = 100
                    for i in range(0, len(response), chunk_size):
                        yield f"data: {json.dumps({'content': response[i:i+chunk_size]})}\n\n"
                        await asyncio.sleep(0.01)
                yield "data: {\"done\": true}\n\n"
            except Exception as inner_e:
                yield f"data: {json.dumps({'error': str(inner_e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/topics/{topic_id}/learn-simple")
async def generate_topic_learning_simple(
    topic_id: str,
    language: str = Query("en", description="Language: 'en' or 'ur'"),
    difficulty: str = Query("medium", description="Difficulty: 'easy', 'medium', or 'hard'"),
):
    """
    Generate learning content for a topic (non-streaming version).
    Returns the complete content in one response.
    """
    from src.services.llm import complete as llm_complete
    
    manager = get_curriculum_manager()
    topic = manager.get_topic(topic_id)
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic_name = topic.get("name_ur", topic.get("name")) if language == "ur" else topic.get("name")
    grade = topic.get("grade", 9)
    
    # Difficulty level descriptions
    difficulty_levels = {
        "easy": {
            "en": "Use very simple language, basic examples, and focus on fundamental understanding.",
            "ur": "بہت آسان زبان، بنیادی مثالیں، بنیادی سمجھ پر توجہ۔"
        },
        "medium": {
            "en": "Use moderate complexity with balanced examples.",
            "ur": "درمیانی پیچیدگی، متوازن مثالیں۔"
        },
        "hard": {
            "en": "Use advanced concepts and challenging examples.",
            "ur": "اعلی تصورات اور مشکل مثالیں۔"
        }
    }
    
    difficulty_instruction = difficulty_levels.get(difficulty, difficulty_levels["medium"])[language]
    
    if language == "ur":
        system_prompt = "آپ ایک ماہر پاکستانی نصابی استاد ہیں۔"
        prompt = f"""براہ کرم "{topic_name}" کے موضوع پر PCTB نصاب (گریڈ {grade}) کے مطابق ایک مختصر سبق لکھیں۔

سطح: {difficulty_instruction}

شامل کریں:
1. تعارف
2. بنیادی تصورات  
3. مثالیں
4. مشق کے سوالات

آسان زبان استعمال کریں۔"""
    else:
        system_prompt = "You are an expert Pakistani curriculum teacher."
        prompt = f"""Please write a lesson on "{topic_name}" for PCTB curriculum Grade {grade}.

Difficulty: {difficulty_instruction}

Include:
1. Introduction
2. Core concepts
3. Examples
4. Practice questions

Use simple language."""

    try:
        response = await llm_complete(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        return {
            "topic_id": topic_id,
            "topic_name": topic_name,
            "content": response,
            "language": language,
            "difficulty": difficulty
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
