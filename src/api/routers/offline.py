"""
Offline Pack API Router - LLM-Powered Content Generation

Provides endpoints for generating and downloading offline learning packs
with AI-generated educational content.
"""

import json
import os
import asyncio
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import shutil
import zipfile
import html

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Import LLM service
try:
    from src.services.llm import complete, get_llm_config
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("[Offline] LLM service not available, using fallback content")


router = APIRouter(tags=["offline"])

# Data directory for offline packs
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "offline_packs"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Pre-generated packs info file
PACKS_INFO_FILE = DATA_DIR / "packs_info.json"


class OfflinePackInfo(BaseModel):
    pack_id: str
    grade: int
    subject: str
    language: str
    topics: List[str]
    created_at: str
    file_path: str
    size_bytes: int
    download_url: str


class GeneratePackRequest(BaseModel):
    grade: int = 9
    subject: str = "mathematics"
    language: str = "both"
    custom_topics: Optional[List[str]] = None  # User can specify custom topics


def _load_packs_info() -> dict:
    """Load packs info from file"""
    if PACKS_INFO_FILE.exists():
        with open(PACKS_INFO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"packs": []}


def _save_packs_info(info: dict):
    """Save packs info to file"""
    with open(PACKS_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)


async def _generate_topic_content_with_llm(
    topic: str, 
    grade: int, 
    subject: str, 
    language: str
) -> dict:
    """
    Generate educational content for a topic using LLM.
    """
    if not LLM_AVAILABLE:
        return _generate_fallback_content(topic, grade, subject, language)
    
    # System prompt for educational content generation
    system_prompt = """You are an expert educational content creator for Pakistani students following the PCTB (Punjab Curriculum and Textbook Board) curriculum.

Create comprehensive educational content that:
1. Is age-appropriate for the specified grade level
2. Follows the Pakistani education standards
3. Includes clear explanations with examples
4. Has practice problems with solutions
5. Uses simple language suitable for students

Format your response as JSON with this EXACT structure:
{
    "title_en": "Topic Title in English",
    "title_ur": "عنوان اردو میں",
    "introduction_en": "Brief introduction explaining what this topic covers and why it's important...",
    "introduction_ur": "مختصر تعارف جو بتائے کہ یہ موضوع کیا ہے اور کیوں اہم ہے...",
    "important_concepts": [
        {
            "concept_en": "Concept 1 Name",
            "concept_ur": "تصور 1 کا نام",
            "definition_en": "Clear definition of the concept",
            "definition_ur": "تصور کی واضح تعریف",
            "explanation_en": "Detailed explanation with why this concept matters",
            "explanation_ur": "تفصیلی وضاحت کہ یہ تصور کیوں اہم ہے",
            "formula_or_rule": "Any formula or rule if applicable (use LaTeX format like $x^2$)",
            "real_life_example_en": "Real life application example",
            "real_life_example_ur": "حقیقی زندگی کی مثال"
        }
    ],
    "worked_examples": [
        {
            "problem_en": "Example problem statement",
            "problem_ur": "مثال کا بیان",
            "solution_en": "Step 1: First step explanation\\nStep 2: Second step\\nStep 3: Final calculation\\nAnswer: Final answer",
            "solution_ur": "مرحلہ 1: پہلا قدم\\nمرحلہ 2: دوسرا قدم\\nمرحلہ 3: آخری حساب\\nجواب: حتمی جواب"
        }
    ],
    "mcqs": [
        {
            "question_en": "MCQ question text?",
            "question_ur": "MCQ سوال کا متن؟",
            "options": {
                "A": {"en": "Option A text", "ur": "آپشن A متن"},
                "B": {"en": "Option B text", "ur": "آپشن B متن"},
                "C": {"en": "Option C text", "ur": "آپشن C متن"},
                "D": {"en": "Option D text", "ur": "آپشن D متن"}
            },
            "correct_answer": "A",
            "explanation_en": "Why A is correct",
            "explanation_ur": "A صحیح کیوں ہے"
        }
    ],
    "short_questions": [
        {
            "question_en": "Short question (2-3 marks level)?",
            "question_ur": "مختصر سوال (2-3 نمبر)?",
            "answer_en": "Concise answer in 2-4 sentences covering the key points.",
            "answer_ur": "2-4 جملوں میں مختصر جواب جو اہم نکات کا احاطہ کرے۔",
            "marks": 3
        }
    ],
    "long_questions": [
        {
            "question_en": "Long question (5-8 marks level)?",
            "question_ur": "طویل سوال (5-8 نمبر)?",
            "answer_en": "Detailed answer with:\\n1. Introduction/Definition\\n2. Explanation of key points\\n3. Examples if applicable\\n4. Conclusion or summary",
            "answer_ur": "تفصیلی جواب:\\n1. تعارف/تعریف\\n2. اہم نکات کی وضاحت\\n3. مثالیں اگر لاگو ہوں\\n4. نتیجہ یا خلاصہ",
            "marks": 5
        }
    ],
    "key_formulas": [
        {
            "name_en": "Formula name",
            "name_ur": "فارمولے کا نام",
            "formula": "$formula in LaTeX$",
            "usage_en": "When and how to use this formula",
            "usage_ur": "یہ فارمولا کب اور کیسے استعمال کریں"
        }
    ],
    "tips_and_tricks": [
        {
            "tip_en": "Helpful tip for students",
            "tip_ur": "طلباء کے لیے مفید ٹِپ"
        }
    ],
    "summary_en": "Key points summary - what students should remember",
    "summary_ur": "اہم نکات کا خلاصہ - طلباء کو کیا یاد رکھنا چاہیے"
}"""

    user_prompt = f"""Create COMPREHENSIVE educational content for:
- Topic: {topic}
- Grade: {grade}
- Subject: {subject}
- Target: Pakistani students (PCTB curriculum)

REQUIREMENTS:
1. Generate 4-5 IMPORTANT CONCEPTS with clear definitions, explanations, formulas (if any), and real-life examples
2. Create 3-4 WORKED EXAMPLES with detailed step-by-step solutions
3. Generate 5-6 MCQs with 4 options each, correct answer marked, and explanation for why it's correct
4. Create 5-6 SHORT QUESTIONS (2-3 marks level) with complete answers
5. Create 3-4 LONG QUESTIONS (5-8 marks level) with detailed comprehensive answers
6. List KEY FORMULAS/RULES related to the topic
7. Add 3-4 TIPS AND TRICKS for students to remember
8. Make sure ALL content is in BOTH English and Urdu

The content should be:
- Exam-focused and practical for students
- Clear and easy to understand
- Complete with all necessary details
- Following PCTB examination patterns

Return ONLY valid JSON, no additional text or explanation outside the JSON."""

    try:
        response = await complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4000,
        )
        
        # Parse JSON response
        # Handle potential markdown code blocks
        content = response.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        parsed = json.loads(content.strip())
        
        # Ensure backward compatibility - map new fields to old if needed
        if "important_concepts" in parsed and "key_concepts" not in parsed:
            parsed["key_concepts"] = parsed["important_concepts"]
        if "worked_examples" in parsed and "examples" not in parsed:
            parsed["examples"] = parsed["worked_examples"]
        if "short_questions" in parsed and "practice_problems" not in parsed:
            parsed["practice_problems"] = parsed["short_questions"]
            
        return parsed
        
    except json.JSONDecodeError as e:
        print(f"[Offline] JSON parse error for topic '{topic}': {e}")
        return _generate_fallback_content(topic, grade, subject, language)
    except Exception as e:
        print(f"[Offline] LLM error for topic '{topic}': {e}")
        return _generate_fallback_content(topic, grade, subject, language)


def _generate_fallback_content(topic: str, grade: int, subject: str, language: str) -> dict:
    """Generate fallback content when LLM is not available."""
    return {
        "title_en": topic,
        "title_ur": topic,
        "introduction_en": f"This lesson covers {topic} for Grade {grade} {subject}. Study the concepts below carefully.",
        "introduction_ur": f"یہ سبق جماعت {grade} کے {subject} کے لیے {topic} کا احاطہ کرتا ہے۔",
        "important_concepts": [
            {
                "concept_en": f"Understanding {topic}",
                "concept_ur": f"{topic} کو سمجھنا",
                "definition_en": f"The fundamental definition of {topic}.",
                "definition_ur": f"{topic} کی بنیادی تعریف۔",
                "explanation_en": f"This concept is fundamental to understanding {topic} in {subject}.",
                "explanation_ur": f"یہ تصور {subject} میں {topic} کو سمجھنے کے لیے بنیادی ہے۔",
                "formula_or_rule": "",
                "real_life_example_en": f"This concept is used in everyday applications of {subject}.",
                "real_life_example_ur": f"یہ تصور {subject} کی روزمرہ ایپلیکیشنز میں استعمال ہوتا ہے۔"
            }
        ],
        "key_concepts": [
            {
                "concept_en": f"Understanding {topic}",
                "concept_ur": f"{topic} کو سمجھنا",
                "explanation_en": f"This concept is fundamental to understanding {topic} in {subject}.",
                "explanation_ur": f"یہ تصور {subject} میں {topic} کو سمجھنے کے لیے بنیادی ہے۔"
            }
        ],
        "worked_examples": [
            {
                "problem_en": f"Example problem for {topic}",
                "problem_ur": f"{topic} کے لیے مثالی مسئلہ",
                "solution_en": "Step 1: Understand the problem\nStep 2: Apply the concept\nStep 3: Calculate the answer",
                "solution_ur": "مرحلہ 1: مسئلہ سمجھیں\nمرحلہ 2: تصور لاگو کریں\nمرحلہ 3: جواب نکالیں"
            }
        ],
        "examples": [
            {
                "problem_en": f"Example problem for {topic}",
                "problem_ur": f"{topic} کے لیے مثالی مسئلہ",
                "solution_en": "Step 1: Understand the problem\nStep 2: Apply the concept\nStep 3: Calculate the answer",
                "solution_ur": "مرحلہ 1: مسئلہ سمجھیں\nمرحلہ 2: تصور لاگو کریں\nمرحلہ 3: جواب نکالیں"
            }
        ],
        "mcqs": [
            {
                "question_en": f"Which of the following best describes {topic}?",
                "question_ur": f"مندرجہ ذیل میں سے کون سا {topic} کو بہترین طریقے سے بیان کرتا ہے؟",
                "options": {
                    "A": {"en": "Option A", "ur": "آپشن A"},
                    "B": {"en": "Option B (Correct)", "ur": "آپشن B (صحیح)"},
                    "C": {"en": "Option C", "ur": "آپشن C"},
                    "D": {"en": "Option D", "ur": "آپشن D"}
                },
                "correct_answer": "B",
                "explanation_en": "Option B is correct because it accurately defines the concept.",
                "explanation_ur": "آپشن B صحیح ہے کیونکہ یہ تصور کو درست طریقے سے بیان کرتا ہے۔"
            }
        ],
        "short_questions": [
            {
                "question_en": f"Define {topic} in your own words.",
                "question_ur": f"اپنے الفاظ میں {topic} کی تعریف کریں۔",
                "answer_en": f"{topic} refers to a fundamental concept in {subject} that helps students understand core principles.",
                "answer_ur": f"{topic} {subject} میں ایک بنیادی تصور ہے جو طلباء کو بنیادی اصولوں کو سمجھنے میں مدد کرتا ہے۔",
                "marks": 3
            }
        ],
        "long_questions": [
            {
                "question_en": f"Explain {topic} in detail with examples.",
                "question_ur": f"مثالوں کے ساتھ {topic} کی تفصیل سے وضاحت کریں۔",
                "answer_en": f"1. Introduction: {topic} is an important concept in {subject}.\n2. Definition: It refers to...\n3. Key Points: The main aspects include...\n4. Examples: For instance...\n5. Conclusion: Understanding this concept is essential for mastering {subject}.",
                "answer_ur": f"1. تعارف: {topic} {subject} میں ایک اہم تصور ہے۔\n2. تعریف: اس سے مراد...\n3. اہم نکات: اہم پہلوؤں میں شامل ہیں...\n4. مثالیں: مثال کے طور پر...\n5. نتیجہ: {subject} میں مہارت حاصل کرنے کے لیے اس تصور کو سمجھنا ضروری ہے۔",
                "marks": 5
            }
        ],
        "practice_problems": [
            {
                "question_en": f"Practice: Solve a problem related to {topic}",
                "question_ur": f"مشق: {topic} سے متعلق مسئلہ حل کریں",
                "answer_en": "Try solving this on your own first!",
                "answer_ur": "پہلے خود حل کرنے کی کوشش کریں!"
            }
        ],
        "key_formulas": [],
        "tips_and_tricks": [
            {
                "tip_en": f"Practice regularly to master {topic}.",
                "tip_ur": f"{topic} میں مہارت حاصل کرنے کے لیے باقاعدگی سے مشق کریں۔"
            }
        ],
        "summary_en": f"In this lesson, you learned about {topic}. Practice regularly to master these concepts.",
        "summary_ur": f"اس سبق میں آپ نے {topic} کے بارے میں سیکھا۔ ان تصورات میں مہارت حاصل کرنے کے لیے باقاعدگی سے مشق کریں۔"
    }


def _content_to_html(content: dict, language: str) -> str:
    """Convert LLM-generated content to HTML format."""
    
    is_urdu = language in ["ur", "both"]
    is_english = language in ["en", "both"]
    
    html_parts = []
    
    # Title
    title = content.get("title_ur" if is_urdu else "title_en", "Topic")
    html_parts.append(f'<div class="topic-content">')
    html_parts.append(f'<h1>{html.escape(str(title))}</h1>')
    
    # Introduction
    if is_english and is_urdu:
        html_parts.append('<div class="bilingual">')
        html_parts.append(f'<p>{html.escape(str(content.get("introduction_en", "")))}</p>')
        html_parts.append(f'<p class="urdu-text">{html.escape(str(content.get("introduction_ur", "")))}</p>')
        html_parts.append('</div>')
    elif is_urdu:
        html_parts.append(f'<p class="urdu-text">{html.escape(str(content.get("introduction_ur", "")))}</p>')
    else:
        html_parts.append(f'<p>{html.escape(str(content.get("introduction_en", "")))}</p>')
    
    # Important Concepts / Key Concepts
    concepts = content.get("important_concepts", content.get("key_concepts", []))
    if concepts:
        html_parts.append('<div class="section">')
        html_parts.append(f'<h2>{"📚 اہم تصورات" if is_urdu else "📚 Important Concepts"}</h2>')
        
        for concept in concepts:
            html_parts.append('<div class="concept-card">')
            if is_english:
                html_parts.append(f'<h3>{html.escape(str(concept.get("concept_en", "")))}</h3>')
                if concept.get("definition_en"):
                    html_parts.append(f'<p><strong>Definition:</strong> {html.escape(str(concept.get("definition_en", "")))}</p>')
                html_parts.append(f'<p>{html.escape(str(concept.get("explanation_en", "")))}</p>')
                if concept.get("formula_or_rule"):
                    html_parts.append(f'<p class="formula"><strong>Formula:</strong> {html.escape(str(concept.get("formula_or_rule", "")))}</p>')
                if concept.get("real_life_example_en"):
                    html_parts.append(f'<p><em>Real-life Example: {html.escape(str(concept.get("real_life_example_en", "")))}</em></p>')
            if is_urdu:
                html_parts.append(f'<h3 class="urdu-text">{html.escape(str(concept.get("concept_ur", "")))}</h3>')
                if concept.get("definition_ur"):
                    html_parts.append(f'<p class="urdu-text"><strong>تعریف:</strong> {html.escape(str(concept.get("definition_ur", "")))}</p>')
                html_parts.append(f'<p class="urdu-text">{html.escape(str(concept.get("explanation_ur", "")))}</p>')
                if concept.get("real_life_example_ur"):
                    html_parts.append(f'<p class="urdu-text"><em>حقیقی زندگی کی مثال: {html.escape(str(concept.get("real_life_example_ur", "")))}</em></p>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    
    # Key Formulas Section
    formulas = content.get("key_formulas", [])
    if formulas:
        html_parts.append('<div class="section formulas-section">')
        html_parts.append(f'<h2>{"📐 اہم فارمولے" if is_urdu else "📐 Key Formulas"}</h2>')
        html_parts.append('<div class="formulas-grid">')
        for formula in formulas:
            html_parts.append('<div class="formula-card">')
            if is_english:
                html_parts.append(f'<h4>{html.escape(str(formula.get("name_en", "")))}</h4>')
            if is_urdu:
                html_parts.append(f'<h4 class="urdu-text">{html.escape(str(formula.get("name_ur", "")))}</h4>')
            html_parts.append(f'<p class="formula-text">{html.escape(str(formula.get("formula", "")))}</p>')
            if is_english and formula.get("usage_en"):
                html_parts.append(f'<p><small>{html.escape(str(formula.get("usage_en", "")))}</small></p>')
            if is_urdu and formula.get("usage_ur"):
                html_parts.append(f'<p class="urdu-text"><small>{html.escape(str(formula.get("usage_ur", "")))}</small></p>')
            html_parts.append('</div>')
        html_parts.append('</div>')
        html_parts.append('</div>')
    
    # Worked Examples
    examples = content.get("worked_examples", content.get("examples", []))
    if examples:
        html_parts.append('<div class="section">')
        html_parts.append(f'<h2>{"✏️ حل شدہ مثالیں" if is_urdu else "✏️ Worked Examples"}</h2>')
        
        for i, example in enumerate(examples, 1):
            html_parts.append('<div class="example-box">')
            html_parts.append(f'<h4>{"مثال" if is_urdu else "Example"} {i}</h4>')
            if is_english:
                html_parts.append(f'<p><strong>Problem:</strong> {html.escape(str(example.get("problem_en", "")))}</p>')
                solution = str(example.get("solution_en", "")).replace("\\n", "<br>").replace("\n", "<br>")
                html_parts.append(f'<div class="solution"><strong>Solution:</strong><br>{solution}</div>')
            if is_urdu:
                html_parts.append(f'<p class="urdu-text"><strong>مسئلہ:</strong> {html.escape(str(example.get("problem_ur", "")))}</p>')
                solution_ur = str(example.get("solution_ur", "")).replace("\\n", "<br>").replace("\n", "<br>")
                html_parts.append(f'<div class="solution urdu-text"><strong>حل:</strong><br>{solution_ur}</div>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    
    # MCQs Section
    mcqs = content.get("mcqs", [])
    if mcqs:
        html_parts.append('<div class="section mcqs-section">')
        html_parts.append(f'<h2>{"🔘 کثیر الانتخابی سوالات (MCQs)" if is_urdu else "🔘 Multiple Choice Questions (MCQs)"}</h2>')
        
        for i, mcq in enumerate(mcqs, 1):
            html_parts.append('<div class="mcq-card">')
            html_parts.append(f'<h4>Q{i}.</h4>')
            if is_english:
                html_parts.append(f'<p class="mcq-question">{html.escape(str(mcq.get("question_en", "")))}</p>')
            if is_urdu:
                html_parts.append(f'<p class="mcq-question urdu-text">{html.escape(str(mcq.get("question_ur", "")))}</p>')
            
            html_parts.append('<div class="mcq-options">')
            options = mcq.get("options", {})
            for opt_key in ["A", "B", "C", "D"]:
                opt = options.get(opt_key, {})
                is_correct = mcq.get("correct_answer", "").upper() == opt_key
                correct_class = "correct-option" if is_correct else ""
                if is_english:
                    opt_text = opt.get("en", "") if isinstance(opt, dict) else str(opt)
                    html_parts.append(f'<div class="option {correct_class}"><strong>{opt_key})</strong> {html.escape(str(opt_text))}</div>')
                elif is_urdu:
                    opt_text = opt.get("ur", "") if isinstance(opt, dict) else str(opt)
                    html_parts.append(f'<div class="option {correct_class} urdu-text"><strong>{opt_key})</strong> {html.escape(str(opt_text))}</div>')
            html_parts.append('</div>')
            
            html_parts.append(f'<div class="mcq-answer"><strong>{"صحیح جواب" if is_urdu else "Correct Answer"}:</strong> {mcq.get("correct_answer", "")}</div>')
            if is_english and mcq.get("explanation_en"):
                html_parts.append(f'<div class="mcq-explanation"><strong>Explanation:</strong> {html.escape(str(mcq.get("explanation_en", "")))}</div>')
            if is_urdu and mcq.get("explanation_ur"):
                html_parts.append(f'<div class="mcq-explanation urdu-text"><strong>وضاحت:</strong> {html.escape(str(mcq.get("explanation_ur", "")))}</div>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    
    # Short Questions Section
    short_qs = content.get("short_questions", content.get("practice_problems", []))
    if short_qs:
        html_parts.append('<div class="section short-questions-section">')
        html_parts.append(f'<h2>{"📝 مختصر سوالات" if is_urdu else "📝 Short Questions"}</h2>')
        
        for i, sq in enumerate(short_qs, 1):
            marks = sq.get("marks", 3)
            html_parts.append('<div class="short-question-card">')
            html_parts.append(f'<div class="question-header"><span class="q-number">Q{i}.</span><span class="marks-badge">{marks} {"نمبر" if is_urdu else "marks"}</span></div>')
            if is_english:
                html_parts.append(f'<p class="question-text">{html.escape(str(sq.get("question_en", "")))}</p>')
                html_parts.append(f'<div class="answer-box"><strong>Answer:</strong><br>{html.escape(str(sq.get("answer_en", "")))}</div>')
            if is_urdu:
                html_parts.append(f'<p class="question-text urdu-text">{html.escape(str(sq.get("question_ur", "")))}</p>')
                html_parts.append(f'<div class="answer-box urdu-text"><strong>جواب:</strong><br>{html.escape(str(sq.get("answer_ur", "")))}</div>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    
    # Long Questions Section
    long_qs = content.get("long_questions", [])
    if long_qs:
        html_parts.append('<div class="section long-questions-section">')
        html_parts.append(f'<h2>{"📖 طویل سوالات" if is_urdu else "📖 Long Questions"}</h2>')
        
        for i, lq in enumerate(long_qs, 1):
            marks = lq.get("marks", 5)
            html_parts.append('<div class="long-question-card">')
            html_parts.append(f'<div class="question-header"><span class="q-number">Q{i}.</span><span class="marks-badge">{marks} {"نمبر" if is_urdu else "marks"}</span></div>')
            if is_english:
                html_parts.append(f'<p class="question-text">{html.escape(str(lq.get("question_en", "")))}</p>')
                answer = str(lq.get("answer_en", "")).replace("\\n", "<br>").replace("\n", "<br>")
                html_parts.append(f'<div class="answer-box long-answer"><strong>Answer:</strong><br>{answer}</div>')
            if is_urdu:
                html_parts.append(f'<p class="question-text urdu-text">{html.escape(str(lq.get("question_ur", "")))}</p>')
                answer_ur = str(lq.get("answer_ur", "")).replace("\\n", "<br>").replace("\n", "<br>")
                html_parts.append(f'<div class="answer-box long-answer urdu-text"><strong>جواب:</strong><br>{answer_ur}</div>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    
    # Tips and Tricks Section
    tips = content.get("tips_and_tricks", [])
    if tips:
        html_parts.append('<div class="section tips-section">')
        html_parts.append(f'<h2>{"💡 ٹِپس اور ٹرکس" if is_urdu else "💡 Tips & Tricks"}</h2>')
        html_parts.append('<ul class="tips-list">')
        for tip in tips:
            if is_english:
                html_parts.append(f'<li>{html.escape(str(tip.get("tip_en", "")))}</li>')
            if is_urdu:
                html_parts.append(f'<li class="urdu-text">{html.escape(str(tip.get("tip_ur", "")))}</li>')
        html_parts.append('</ul>')
        html_parts.append('</div>')
    
    # Summary
    html_parts.append('<div class="summary-box">')
    html_parts.append(f'<h2>{"📌 خلاصہ" if is_urdu else "📌 Summary"}</h2>')
    if is_english:
        html_parts.append(f'<p>{html.escape(str(content.get("summary_en", "")))}</p>')
    if is_urdu:
        html_parts.append(f'<p class="urdu-text">{html.escape(str(content.get("summary_ur", "")))}</p>')
    html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)


async def _generate_pack_with_llm(
    output_dir: Path,
    grade: int,
    subject: str,
    language: str,
    custom_topics: Optional[List[str]] = None
) -> List[str]:
    """
    Generate a complete offline learning pack using LLM.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "topics").mkdir(exist_ok=True)
    
    # Default topics if none provided
    DEFAULT_TOPICS = {
        "mathematics": [
            "Linear Equations", "Quadratic Equations", "Matrices",
            "Trigonometry", "Geometry Basics"
        ],
        "science": [
            "Motion and Force", "Energy and Work", "Atoms and Molecules",
            "Chemical Reactions", "Human Body Systems"
        ],
        "english": [
            "Grammar Basics", "Sentence Structure", "Vocabulary Building",
            "Reading Comprehension", "Essay Writing"
        ],
        "urdu": [
            "قواعد", "اردو ادب", "نظم و نثر",
            "مضمون نویسی", "تلفظ"
        ],
        "all": [
            "Mathematics: Quadratic Equations",
            "Science: Motion and Force",
            "English: Grammar Basics",
            "Urdu: قواعد"
        ]
    }
    
    topics = custom_topics or DEFAULT_TOPICS.get(subject, DEFAULT_TOPICS["mathematics"])
    
    # Generate content for each topic
    topic_files = []
    
    for i, topic in enumerate(topics):
        print(f"[Offline] Generating content for: {topic} ({i+1}/{len(topics)})")
        
        # Generate content using LLM
        content = await _generate_topic_content_with_llm(topic, grade, subject, language)
        
        # Convert to HTML
        topic_html = _content_to_html(content, language)
        
        # Create topic HTML file
        topic_id = f"topic_{i+1}"
        topic_file = output_dir / "topics" / f"{topic_id}.html"
        
        full_html = f"""<!DOCTYPE html>
<html lang="{'ur' if language == 'ur' else 'en'}" dir="{'rtl' if language == 'ur' else 'ltr'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(str(content.get('title_en', topic)))} - DeepTutor Offline</title>
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
    <nav class="nav-bar">
        <a href="../index.html" class="back-link">← Back to Topics</a>
        <span class="grade-badge">Grade {grade}</span>
    </nav>
    {topic_html}
    <footer class="footer">
        <p>DeepTutor - Offline Learning Pack | PCTB Aligned</p>
        <p class="urdu-text">ڈیپ ٹیوٹر - آف لائن لرننگ پیک</p>
    </footer>
    <script src="../progress.js"></script>
</body>
</html>"""
        
        with open(topic_file, "w", encoding="utf-8") as f:
            f.write(full_html)
        
        topic_files.append({
            "id": topic_id,
            "title_en": content.get("title_en", topic),
            "title_ur": content.get("title_ur", topic),
            "file": f"topics/{topic_id}.html"
        })
    
    # Create main index.html
    _create_index_html(output_dir, grade, subject, language, topic_files)
    
    # Create styles.css
    _create_styles_css(output_dir)
    
    # Create progress tracker
    _create_progress_tracker(output_dir)
    
    return [t["title_en"] for t in topic_files]


def _create_index_html(output_dir: Path, grade: int, subject: str, language: str, topics: list):
    """Create the main index.html file."""
    
    is_urdu = language in ["ur", "both"]
    
    topic_cards = []
    for t in topics:
        title = t.get("title_ur" if is_urdu else "title_en", "Topic")
        topic_cards.append(f'''
        <a href="{t['file']}" class="topic-card" data-topic-id="{t['id']}">
            <div class="topic-icon">📖</div>
            <div class="topic-info">
                <h3>{html.escape(str(title))}</h3>
                <span class="progress-badge">Ready to Learn</span>
            </div>
        </a>''')
    
    index_html = f'''<!DOCTYPE html>
<html lang="{'ur' if language == 'ur' else 'en'}" dir="{'rtl' if language == 'ur' else 'ltr'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeepTutor - Offline Learning Pack</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <div class="logo">📚 DeepTutor</div>
        <div class="pack-info">
            <span class="grade-badge">Grade {grade}</span>
            <span class="subject-badge">{subject.title()}</span>
            <span class="offline-badge">🔌 Offline Ready</span>
        </div>
    </header>
    
    <main class="main-content">
        <h1>{"آف لائن لرننگ پیک" if is_urdu else "1-Day Offline Learning Pack"}</h1>
        <p class="subtitle">
            {"بغیر انٹرنیٹ کے سیکھیں - AI سے تیار کردہ مواد" if is_urdu else "Learn without internet - AI Generated Content"}
        </p>
        
        <div class="topics-grid">
            {''.join(topic_cards)}
        </div>
        
        <div class="study-tips">
            <h2>{"سیکھنے کے طریقے" if is_urdu else "Study Tips"}</h2>
            <ul>
                <li>{"ہر عنوان کو غور سے پڑھیں" if is_urdu else "Read each topic carefully"}</li>
                <li>{"مثالیں حل کریں" if is_urdu else "Work through the examples"}</li>
                <li>{"مشق کے سوالات خود حل کریں" if is_urdu else "Try practice problems on your own"}</li>
                <li>{"خلاصہ دوبارہ پڑھیں" if is_urdu else "Review the summary"}</li>
            </ul>
        </div>
    </main>
    
    <footer class="footer">
        <p>DeepTutor - Your Personal AI Tutor | PCTB Curriculum Aligned</p>
        <p class="urdu-text">ڈیپ ٹیوٹر - آپ کا ذاتی AI استاد | PCTB نصاب کے مطابق</p>
        <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Powered by AI</p>
    </footer>
    
    <script src="progress.js"></script>
</body>
</html>'''
    
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)


def _create_styles_css(output_dir: Path):
    """Create the main CSS file."""
    
    css = '''
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); min-height: 100vh; color: #1f2937; }
.urdu-text { font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', serif; direction: rtl; text-align: right; }
.header { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
.logo { font-size: 24px; font-weight: bold; }
.pack-info { display: flex; gap: 10px; flex-wrap: wrap; }
.grade-badge, .subject-badge, .offline-badge { background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; font-size: 14px; }
.main-content { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
h1 { font-size: 32px; color: #059669; margin-bottom: 10px; }
.subtitle { color: #6b7280; margin-bottom: 30px; font-size: 18px; }
.topics-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin: 30px 0; }
.topic-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 15px; text-decoration: none; color: inherit; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s ease; }
.topic-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
.topic-card.completed { border: 2px solid #059669; }
.topic-icon { font-size: 40px; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; background: #ecfdf5; border-radius: 12px; }
.topic-info h3 { color: #1f2937; margin-bottom: 5px; }
.progress-badge { font-size: 12px; color: #059669; background: #ecfdf5; padding: 4px 8px; border-radius: 4px; }
.study-tips { background: white; border-radius: 16px; padding: 25px; margin-top: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.study-tips h2 { color: #059669; margin-bottom: 15px; }
.study-tips ul { padding-left: 25px; }
.study-tips li { margin: 10px 0; color: #4b5563; }
.nav-bar { background: #059669; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
.back-link { color: white; text-decoration: none; }
.back-link:hover { text-decoration: underline; }
.footer { text-align: center; padding: 30px; color: #6b7280; font-size: 14px; }
.footer .urdu-text { margin-top: 5px; }
.timestamp { margin-top: 10px; font-size: 12px; color: #9ca3af; }
.topic-content { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.8; }
.bilingual { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0; }
.section { margin: 25px 0; padding: 20px; background: #f8fafc; border-radius: 12px; border-left: 4px solid #059669; }
.section h2 { color: #059669; margin-bottom: 15px; }
.concept-card { background: white; padding: 15px; border-radius: 8px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.concept-card h4 { color: #059669; margin-bottom: 8px; font-size: 16px; }
.concept-card .definition { color: #374151; margin-bottom: 8px; line-height: 1.6; }
.concept-card .formula { background: #ecfdf5; padding: 10px; border-radius: 6px; font-family: 'Courier New', monospace; font-weight: bold; color: #047857; margin: 8px 0; text-align: center; }
.concept-card .real-life { color: #6b7280; font-style: italic; font-size: 14px; padding-left: 10px; border-left: 2px solid #059669; }
.example-box { background: #ecfdf5; padding: 15px; border-radius: 8px; margin: 10px 0; }
.example-box h4 { color: #047857; }
.practice-item { background: #fffbeb; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 3px solid #f59e0b; }
.answer { margin-top: 10px; padding: 10px; background: #f0fdf4; border-radius: 4px; }
.summary-box { background: linear-gradient(135deg, #059669, #047857); color: white; padding: 20px; border-radius: 12px; margin-top: 30px; }

/* MCQs Section Styles */
.mcqs-section { margin: 30px 0; }
.mcqs-section h2 { color: #059669; margin-bottom: 20px; font-size: 22px; display: flex; align-items: center; gap: 10px; }
.mcqs-section h2::before { content: "📝"; }
.mcq-card { background: white; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 3px 10px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; transition: all 0.3s ease; }
.mcq-card:hover { box-shadow: 0 5px 15px rgba(0,0,0,0.15); }
.mcq-card h4 { color: #1f2937; font-size: 16px; margin-bottom: 15px; line-height: 1.5; }
.mcq-card h4 .q-num { background: #059669; color: white; padding: 2px 10px; border-radius: 20px; font-size: 13px; margin-right: 10px; }
.mcq-options { list-style: none; padding: 0; margin: 0 0 15px 0; }
.mcq-options li { padding: 12px 15px; margin: 8px 0; background: #f8fafc; border-radius: 8px; border: 2px solid transparent; cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; gap: 10px; }
.mcq-options li:hover { background: #ecfdf5; border-color: #059669; }
.mcq-options li .option-letter { background: #e5e7eb; color: #374151; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
.mcq-options li.correct-option { background: #d1fae5; border-color: #059669; }
.mcq-options li.correct-option .option-letter { background: #059669; color: white; }
.mcq-answer { background: #ecfdf5; padding: 12px 15px; border-radius: 8px; margin-top: 10px; display: flex; align-items: center; gap: 10px; }
.mcq-answer .answer-label { color: #047857; font-weight: bold; }
.mcq-explanation { background: #fffbeb; padding: 12px 15px; border-radius: 8px; margin-top: 10px; border-left: 3px solid #f59e0b; }
.mcq-explanation .explanation-label { color: #92400e; font-weight: bold; margin-bottom: 5px; }
.mcq-explanation p { color: #78350f; font-size: 14px; line-height: 1.5; }

/* Short Questions Section Styles */
.short-questions-section { margin: 30px 0; }
.short-questions-section h2 { color: #059669; margin-bottom: 20px; font-size: 22px; display: flex; align-items: center; gap: 10px; }
.short-questions-section h2::before { content: "✏️"; }
.short-question-card { background: white; border-radius: 12px; padding: 20px; margin: 15px 0; box-shadow: 0 3px 10px rgba(0,0,0,0.1); border-left: 4px solid #3b82f6; }
.short-question-card .question-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
.short-question-card .question-header h4 { color: #1f2937; font-size: 16px; line-height: 1.5; flex: 1; }
.marks-badge { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; white-space: nowrap; margin-left: 10px; }
.short-question-card .answer { background: #eff6ff; border: 1px solid #bfdbfe; padding: 15px; border-radius: 8px; margin-top: 10px; }
.short-question-card .answer .answer-label { color: #1d4ed8; font-weight: bold; margin-bottom: 8px; display: block; }
.short-question-card .answer p { color: #1e40af; line-height: 1.6; }

/* Long Questions Section Styles */
.long-questions-section { margin: 30px 0; }
.long-questions-section h2 { color: #059669; margin-bottom: 20px; font-size: 22px; display: flex; align-items: center; gap: 10px; }
.long-questions-section h2::before { content: "📄"; }
.long-question-card { background: white; border-radius: 12px; padding: 25px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #8b5cf6; }
.long-question-card .question-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px dashed #e5e7eb; }
.long-question-card .question-header h4 { color: #1f2937; font-size: 17px; line-height: 1.5; flex: 1; }
.long-question-card .marks-badge { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.long-question-card .long-answer { background: #f5f3ff; border: 1px solid #ddd6fe; padding: 20px; border-radius: 10px; }
.long-question-card .long-answer .answer-label { color: #6d28d9; font-weight: bold; margin-bottom: 12px; display: block; font-size: 15px; }
.long-question-card .long-answer p { color: #4c1d95; line-height: 1.7; margin-bottom: 10px; }
.long-question-card .long-answer ul, .long-question-card .long-answer ol { margin: 10px 0 10px 20px; color: #4c1d95; }
.long-question-card .long-answer li { margin: 8px 0; line-height: 1.6; }

/* Formulas Section Styles */
.formulas-section { margin: 30px 0; }
.formulas-section h2 { color: #059669; margin-bottom: 20px; font-size: 22px; display: flex; align-items: center; gap: 10px; }
.formulas-section h2::before { content: "🔢"; }
.formulas-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }
.formula-card { background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 3px 8px rgba(0,0,0,0.1); border: 1px solid #fcd34d; }
.formula-card h4 { color: #92400e; font-size: 14px; margin-bottom: 10px; }
.formula-card .formula-text { background: white; padding: 12px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; color: #78350f; }

/* Tips Section Styles */
.tips-section { margin: 30px 0; background: linear-gradient(135deg, #ecfdf5, #d1fae5); border-radius: 12px; padding: 25px; }
.tips-section h2 { color: #047857; margin-bottom: 15px; font-size: 22px; display: flex; align-items: center; gap: 10px; }
.tips-section h2::before { content: "💡"; }
.tips-list { list-style: none; padding: 0; }
.tips-list li { background: white; padding: 12px 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); display: flex; align-items: flex-start; gap: 10px; }
.tips-list li::before { content: "✓"; background: #059669; color: white; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }

.complete-btn { background: #059669; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; cursor: pointer; margin: 20px auto; display: block; }
.complete-btn:hover { background: #047857; }
.complete-btn:disabled { background: #9ca3af; cursor: not-allowed; }
@media (max-width: 768px) { .header { flex-direction: column; text-align: center; } .topics-grid { grid-template-columns: 1fr; } h1 { font-size: 24px; } .bilingual { grid-template-columns: 1fr; } .formulas-grid { grid-template-columns: 1fr; } .short-question-card .question-header, .long-question-card .question-header { flex-direction: column; gap: 10px; } .marks-badge { align-self: flex-start; } }
'''
    
    with open(output_dir / "styles.css", "w", encoding="utf-8") as f:
        f.write(css)


def _create_progress_tracker(output_dir: Path):
    """Create JavaScript for tracking learning progress."""
    
    js = '''
// DeepTutor Offline Progress Tracker
(function() {
    const STORAGE_KEY = 'deeptutor_offline_progress';
    
    function getProgress() {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } 
        catch { return {}; }
    }
    
    function saveProgress(progress) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
    }
    
    function markTopicViewed(topicId) {
        const progress = getProgress();
        if (!progress[topicId]) {
            progress[topicId] = { viewed: true, viewedAt: new Date().toISOString(), completed: false };
            saveProgress(progress);
        }
    }
    
    function markTopicCompleted(topicId) {
        const progress = getProgress();
        progress[topicId] = { ...progress[topicId], completed: true, completedAt: new Date().toISOString() };
        saveProgress(progress);
        updateProgressUI();
    }
    
    function updateProgressUI() {
        const progress = getProgress();
        document.querySelectorAll('.topic-card').forEach(card => {
            const topicId = card.getAttribute('data-topic-id');
            const badge = card.querySelector('.progress-badge');
            if (progress[topicId]?.completed) {
                badge.textContent = '✅ Completed';
                badge.style.background = '#d1fae5';
                badge.style.color = '#047857';
                card.classList.add('completed');
            } else if (progress[topicId]?.viewed) {
                badge.textContent = '📖 In Progress';
                badge.style.background = '#fef3c7';
                badge.style.color = '#92400e';
            }
        });
    }
    
    document.addEventListener('DOMContentLoaded', function() {
        updateProgressUI();
        
        const currentPath = window.location.pathname;
        if (currentPath.includes('/topics/')) {
            const topicId = currentPath.split('/').pop().replace('.html', '');
            markTopicViewed(topicId);
            
            const footer = document.querySelector('.footer');
            if (footer) {
                const btn = document.createElement('button');
                btn.className = 'complete-btn';
                btn.textContent = 'Mark as Completed ✓';
                btn.onclick = function() { markTopicCompleted(topicId); btn.textContent = 'Completed! ✅'; btn.disabled = true; };
                footer.insertBefore(btn, footer.firstChild);
            }
        }
    });
    
    window.DeepTutorProgress = { getProgress, markTopicViewed, markTopicCompleted };
})();
'''
    
    with open(output_dir / "progress.js", "w", encoding="utf-8") as f:
        f.write(js)


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/packs")
async def list_offline_packs():
    """List all available offline packs."""
    return _load_packs_info()


@router.post("/generate")
async def generate_offline_pack(request: GeneratePackRequest):
    """Generate a new offline learning pack with LLM-generated content."""
    pack_id = f"pack_{request.grade}_{request.subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = DATA_DIR / pack_id
    
    try:
        topics = await _generate_pack_with_llm(
            output_dir=output_dir,
            grade=request.grade,
            subject=request.subject,
            language=request.language,
            custom_topics=request.custom_topics
        )
        
        # Create ZIP file
        zip_path = DATA_DIR / f"{pack_id}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(output_dir)
                    zipf.write(file_path, arcname)
        
        size_bytes = zip_path.stat().st_size
        
        pack_info = OfflinePackInfo(
            pack_id=pack_id,
            grade=request.grade,
            subject=request.subject,
            language=request.language,
            topics=topics,
            created_at=datetime.now().isoformat(),
            file_path=str(zip_path),
            size_bytes=size_bytes,
            download_url=f"/api/v1/offline/download/{pack_id}"
        )
        
        packs_info = _load_packs_info()
        packs_info["packs"].append(pack_info.model_dump())
        _save_packs_info(packs_info)
        
        shutil.rmtree(output_dir, ignore_errors=True)
        
        return pack_info.model_dump()
        
    except Exception as e:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate pack: {str(e)}")


@router.get("/download/{pack_id}")
async def download_offline_pack(pack_id: str):
    """Download an offline pack as a ZIP file."""
    zip_path = DATA_DIR / f"{pack_id}.zip"
    
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Pack not found")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"deeptutor_{pack_id}.zip"
    )


@router.get("/prebuilt")
async def get_prebuilt_packs():
    """Get list of available packs."""
    packs_info = _load_packs_info()
    return {"prebuilt": [], "generated": packs_info.get("packs", [])}


@router.delete("/packs/{pack_id}")
async def delete_pack(pack_id: str):
    """Delete an offline pack."""
    zip_path = DATA_DIR / f"{pack_id}.zip"
    
    if zip_path.exists():
        zip_path.unlink()
    
    packs_info = _load_packs_info()
    packs_info["packs"] = [p for p in packs_info.get("packs", []) if p["pack_id"] != pack_id]
    _save_packs_info(packs_info)
    
    return {"status": "deleted", "pack_id": pack_id}
