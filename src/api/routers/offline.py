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

Format your response as JSON with this structure:
{
    "title_en": "Topic Title in English",
    "title_ur": "عنوان اردو میں",
    "introduction_en": "Brief introduction...",
    "introduction_ur": "مختصر تعارف...",
    "key_concepts": [
        {
            "concept_en": "Concept name",
            "concept_ur": "تصور کا نام",
            "explanation_en": "Detailed explanation...",
            "explanation_ur": "تفصیلی وضاحت..."
        }
    ],
    "examples": [
        {
            "problem_en": "Example problem",
            "problem_ur": "مثال کا مسئلہ",
            "solution_en": "Step by step solution",
            "solution_ur": "قدم بہ قدم حل"
        }
    ],
    "practice_problems": [
        {
            "question_en": "Practice question",
            "question_ur": "مشق کا سوال",
            "answer_en": "Answer",
            "answer_ur": "جواب"
        }
    ],
    "summary_en": "Key points summary",
    "summary_ur": "اہم نکات کا خلاصہ"
}"""

    user_prompt = f"""Create educational content for:
- Topic: {topic}
- Grade: {grade}
- Subject: {subject}
- Target: Pakistani students (PCTB curriculum)

Generate comprehensive learning material with explanations in both English and Urdu.
Include 3-4 key concepts, 2-3 worked examples, and 3-4 practice problems.

Return ONLY valid JSON, no additional text."""

    try:
        response = await complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
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
        
        return json.loads(content.strip())
        
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
        "key_concepts": [
            {
                "concept_en": f"Understanding {topic}",
                "concept_ur": f"{topic} کو سمجھنا",
                "explanation_en": f"This concept is fundamental to understanding {topic} in {subject}.",
                "explanation_ur": f"یہ تصور {subject} میں {topic} کو سمجھنے کے لیے بنیادی ہے۔"
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
        "practice_problems": [
            {
                "question_en": f"Practice: Solve a problem related to {topic}",
                "question_ur": f"مشق: {topic} سے متعلق مسئلہ حل کریں",
                "answer_en": "Try solving this on your own first!",
                "answer_ur": "پہلے خود حل کرنے کی کوشش کریں!"
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
    
    # Key Concepts
    html_parts.append('<div class="section">')
    html_parts.append(f'<h2>{"اہم تصورات" if is_urdu else "Key Concepts"}</h2>')
    
    for concept in content.get("key_concepts", []):
        html_parts.append('<div class="concept-card">')
        if is_english:
            html_parts.append(f'<h3>{html.escape(str(concept.get("concept_en", "")))}</h3>')
            html_parts.append(f'<p>{html.escape(str(concept.get("explanation_en", "")))}</p>')
        if is_urdu:
            html_parts.append(f'<h3 class="urdu-text">{html.escape(str(concept.get("concept_ur", "")))}</h3>')
            html_parts.append(f'<p class="urdu-text">{html.escape(str(concept.get("explanation_ur", "")))}</p>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    # Examples
    html_parts.append('<div class="section">')
    html_parts.append(f'<h2>{"مثالیں" if is_urdu else "Worked Examples"}</h2>')
    
    for i, example in enumerate(content.get("examples", []), 1):
        html_parts.append('<div class="example-box">')
        html_parts.append(f'<h4>{"مثال" if is_urdu else "Example"} {i}</h4>')
        if is_english:
            html_parts.append(f'<p><strong>Problem:</strong> {html.escape(str(example.get("problem_en", "")))}</p>')
            solution = str(example.get("solution_en", "")).replace("\n", "<br>")
            html_parts.append(f'<p><strong>Solution:</strong><br>{solution}</p>')
        if is_urdu:
            html_parts.append(f'<p class="urdu-text"><strong>مسئلہ:</strong> {html.escape(str(example.get("problem_ur", "")))}</p>')
            solution_ur = str(example.get("solution_ur", "")).replace("\n", "<br>")
            html_parts.append(f'<p class="urdu-text"><strong>حل:</strong><br>{solution_ur}</p>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    # Practice Problems
    html_parts.append('<div class="section">')
    html_parts.append(f'<h2>{"مشق کے سوالات" if is_urdu else "Practice Problems"}</h2>')
    
    for i, problem in enumerate(content.get("practice_problems", []), 1):
        html_parts.append('<div class="practice-item">')
        html_parts.append(f'<h4>{"سوال" if is_urdu else "Question"} {i}</h4>')
        if is_english:
            html_parts.append(f'<p>{html.escape(str(problem.get("question_en", "")))}</p>')
            html_parts.append(f'<div class="answer"><strong>Answer:</strong> {html.escape(str(problem.get("answer_en", "")))}</div>')
        if is_urdu:
            html_parts.append(f'<p class="urdu-text">{html.escape(str(problem.get("question_ur", "")))}</p>')
            html_parts.append(f'<div class="answer urdu-text"><strong>جواب:</strong> {html.escape(str(problem.get("answer_ur", "")))}</div>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    # Summary
    html_parts.append('<div class="summary-box">')
    html_parts.append(f'<h2>{"خلاصہ" if is_urdu else "Summary"}</h2>')
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
.example-box { background: #ecfdf5; padding: 15px; border-radius: 8px; margin: 10px 0; }
.example-box h4 { color: #047857; }
.practice-item { background: #fffbeb; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 3px solid #f59e0b; }
.answer { margin-top: 10px; padding: 10px; background: #f0fdf4; border-radius: 4px; }
.summary-box { background: linear-gradient(135deg, #059669, #047857); color: white; padding: 20px; border-radius: 12px; margin-top: 30px; }
.complete-btn { background: #059669; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; cursor: pointer; margin: 20px auto; display: block; }
.complete-btn:hover { background: #047857; }
.complete-btn:disabled { background: #9ca3af; cursor: not-allowed; }
@media (max-width: 768px) { .header { flex-direction: column; text-align: center; } .topics-grid { grid-template-columns: 1fr; } h1 { font-size: 24px; } .bilingual { grid-template-columns: 1fr; } }
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
