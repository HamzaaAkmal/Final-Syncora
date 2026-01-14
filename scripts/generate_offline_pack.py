"""
Offline Learning Pack Generator for DeepTutor

This script generates downloadable offline learning packs for areas with
limited internet connectivity, supporting the EDU TECH Challenge requirements.

Features:
- Curriculum-aligned content packages
- Multi-language support (English, Urdu)
- Lightweight PDFs and HTML files
- Practice questions and solutions
- Progress tracking templates
"""

import json
import os
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.curriculum.data import SUBJECTS, MATH_GRADE_9_TOPICS, SCIENCE_GRADE_9_TOPICS
from src.curriculum.models import Subject, Topic, DifficultyLevel


@dataclass
class OfflinePack:
    """Represents an offline learning pack"""
    pack_id: str
    grade: int
    subject: str
    language: str  # 'en', 'ur', 'both'
    topics: List[str]
    created_at: str
    file_path: str
    size_bytes: int
    
    def to_dict(self) -> dict:
        return {
            "pack_id": self.pack_id,
            "grade": self.grade,
            "subject": self.subject,
            "language": self.language,
            "topics": self.topics,
            "created_at": self.created_at,
            "file_path": self.file_path,
            "size_bytes": self.size_bytes
        }


class OfflinePackGenerator:
    """Generates offline learning packs for download"""
    
    def __init__(self, output_dir: str = "data/offline_packs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = Path(__file__).parent / "templates" / "offline"
        
    def generate_pack(
        self,
        grade: int,
        subject: str,
        language: str = "both",
        topics: Optional[List[str]] = None
    ) -> OfflinePack:
        """
        Generate an offline learning pack.
        
        Args:
            grade: Grade level (9-12)
            subject: Subject name (mathematics, science, english, urdu)
            language: Language preference ('en', 'ur', 'both')
            topics: Specific topics to include (None = all topics)
        
        Returns:
            OfflinePack object with pack details
        """
        # Create pack ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pack_id = f"{subject}_grade{grade}_{language}_{timestamp}"
        
        # Create temporary directory for pack contents
        temp_dir = self.output_dir / f"temp_{pack_id}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get topics for the subject
            subject_topics = self._get_subject_topics(grade, subject)
            
            # Filter topics if specified
            if topics:
                subject_topics = [t for t in subject_topics if t.id in topics or t.name in topics]
            
            # Generate content files
            self._generate_index_html(temp_dir, subject, grade, subject_topics, language)
            self._generate_topic_pages(temp_dir, subject_topics, language)
            self._generate_practice_questions(temp_dir, subject_topics, language)
            self._generate_quick_reference(temp_dir, subject_topics, language)
            self._generate_progress_tracker(temp_dir, subject_topics, language)
            self._generate_styles(temp_dir)
            
            # Create metadata
            self._generate_metadata(temp_dir, pack_id, grade, subject, language, subject_topics)
            
            # Create zip file
            zip_path = self.output_dir / f"{pack_id}.zip"
            self._create_zip(temp_dir, zip_path)
            
            # Get file size
            size_bytes = zip_path.stat().st_size
            
            return OfflinePack(
                pack_id=pack_id,
                grade=grade,
                subject=subject,
                language=language,
                topics=[t.name for t in subject_topics],
                created_at=datetime.now().isoformat(),
                file_path=str(zip_path),
                size_bytes=size_bytes
            )
            
        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _get_subject_topics(self, grade: int, subject: str) -> List[Topic]:
        """Get topics for a subject and grade"""
        if subject == "mathematics" and grade == 9:
            return MATH_GRADE_9_TOPICS
        elif subject == "science" and grade == 9:
            return SCIENCE_GRADE_9_TOPICS
        else:
            # Return empty list for subjects/grades not yet implemented
            return []
    
    def _generate_index_html(
        self,
        output_dir: Path,
        subject: str,
        grade: int,
        topics: List[Topic],
        language: str
    ):
        """Generate main index.html file"""
        
        # Generate topics list
        topics_html = ""
        for topic in topics:
            if language == "ur":
                title = topic.name_ur or topic.name
            elif language == "both":
                title = f"{topic.name} / {topic.name_ur}" if topic.name_ur else topic.name
            else:
                title = topic.name
            
            difficulty_badge = self._get_difficulty_badge(topic.difficulty)
            
            topics_html += f"""
            <div class="topic-card">
                <h3><a href="topics/{topic.id}.html">{title}</a></h3>
                <span class="badge {topic.difficulty.value}">{difficulty_badge}</span>
                <p class="description">{topic.description if language != 'ur' else (topic.description_ur or topic.description)}</p>
            </div>
            """
        
        # Determine title based on language
        if language == "ur":
            title = f"جماعت {grade} - {self._get_subject_name_ur(subject)}"
            subtitle = "آف لائن تعلیمی پیکج"
            nav_topics = "عنوانات"
            nav_practice = "مشق"
            nav_reference = "حوالہ"
            nav_progress = "پیش رفت"
        else:
            title = f"Grade {grade} - {subject.title()}"
            subtitle = "Offline Learning Pack"
            nav_topics = "Topics"
            nav_practice = "Practice"
            nav_reference = "Reference"
            nav_progress = "Progress"
        
        html_content = f"""<!DOCTYPE html>
<html lang="{language}" dir="{'rtl' if language == 'ur' else 'ltr'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Syncora</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <div class="logo">
            <h1>🎓 Syncora</h1>
            <p>{subtitle}</p>
        </div>
        <nav>
            <a href="index.html" class="active">{nav_topics}</a>
            <a href="practice.html">{nav_practice}</a>
            <a href="reference.html">{nav_reference}</a>
            <a href="progress.html">{nav_progress}</a>
        </nav>
    </header>
    
    <main>
        <section class="hero">
            <h2>{title}</h2>
            <p>{len(topics)} topics included</p>
        </section>
        
        <section class="topics-grid">
            {topics_html}
        </section>
    </main>
    
    <footer>
        <p>🇵🇰 Made for Pakistani Students | Punjab Curriculum and Textbook Board (PCTB)</p>
        <p>Generated by Syncora - EDU TECH Challenge 2025</p>
    </footer>
</body>
</html>
"""
        
        (output_dir / "index.html").write_text(html_content, encoding="utf-8")
    
    def _generate_topic_pages(self, output_dir: Path, topics: List[Topic], language: str):
        """Generate individual topic HTML pages"""
        topics_dir = output_dir / "topics"
        topics_dir.mkdir(exist_ok=True)
        
        for topic in topics:
            title = topic.name if language != "ur" else (topic.name_ur or topic.name)
            description = topic.description if language != "ur" else (topic.description_ur or topic.description)
            
            # Generate learning objectives
            objectives_html = "<ul>"
            for obj in topic.learning_objectives:
                obj_text = obj.description if language != "ur" else (obj.description_ur or obj.description)
                objectives_html += f"<li>{obj_text}</li>"
            objectives_html += "</ul>"
            
            # Generate prerequisites
            prereq_html = ""
            if topic.prerequisites:
                prereq_html = f"""
                <section class="prerequisites">
                    <h3>{'پیشگی ضروریات' if language == 'ur' else 'Prerequisites'}</h3>
                    <ul>
                        {''.join(f'<li>{p}</li>' for p in topic.prerequisites)}
                    </ul>
                </section>
                """
            
            html_content = f"""<!DOCTYPE html>
<html lang="{language}" dir="{'rtl' if language == 'ur' else 'ltr'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - DeepTutor</title>
    <link rel="stylesheet" href="../styles.css">
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <header class="header">
        <a href="../index.html" class="back-btn">← {'واپس' if language == 'ur' else 'Back'}</a>
        <h1>{title}</h1>
    </header>
    
    <main class="topic-content">
        <section class="overview">
            <h2>{'جائزہ' if language == 'ur' else 'Overview'}</h2>
            <p>{description}</p>
            <p class="difficulty">
                {'مشکل کی سطح' if language == 'ur' else 'Difficulty'}: 
                <span class="badge {topic.difficulty.value}">{self._get_difficulty_badge(topic.difficulty)}</span>
            </p>
        </section>
        
        <section class="objectives">
            <h2>{'سیکھنے کے مقاصد' if language == 'ur' else 'Learning Objectives'}</h2>
            {objectives_html}
        </section>
        
        {prereq_html}
        
        <section class="content">
            <h2>{'مواد' if language == 'ur' else 'Content'}</h2>
            <div class="placeholder">
                <p>{'تفصیلی مواد جلد آ رہا ہے...' if language == 'ur' else 'Detailed content coming soon...'}</p>
                <p>{'براہ کرم اپنی PCTB نصابی کتاب دیکھیں' if language == 'ur' else 'Please refer to your PCTB textbook'}</p>
            </div>
        </section>
        
        <section class="practice-link">
            <a href="../practice.html#{topic.id}" class="btn-primary">
                {'مشق کے سوالات' if language == 'ur' else 'Practice Questions'} →
            </a>
        </section>
    </main>
    
    <footer>
        <p>🇵🇰 Syncora - PCTB Aligned</p>
    </footer>
</body>
</html>
"""
            
            (topics_dir / f"{topic.id}.html").write_text(html_content, encoding="utf-8")
    
    def _generate_practice_questions(self, output_dir: Path, topics: List[Topic], language: str):
        """Generate practice questions page"""
        
        questions_html = ""
        for i, topic in enumerate(topics):
            title = topic.name if language != "ur" else (topic.name_ur or topic.name)
            
            # Generate sample questions based on difficulty
            sample_questions = self._get_sample_questions(topic, language)
            
            questions_html += f"""
            <section class="topic-questions" id="{topic.id}">
                <h3>{i+1}. {title}</h3>
                {sample_questions}
            </section>
            """
        
        html_content = f"""<!DOCTYPE html>
<html lang="{language}" dir="{'rtl' if language == 'ur' else 'ltr'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{'مشق کے سوالات' if language == 'ur' else 'Practice Questions'} - DeepTutor</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <header class="header">
        <a href="index.html" class="back-btn">← {'واپس' if language == 'ur' else 'Back'}</a>
        <h1>{'مشق کے سوالات' if language == 'ur' else 'Practice Questions'}</h1>
    </header>
    
    <main class="practice-content">
        <div class="instructions">
            <p>{'ہر سوال کو احتیاط سے پڑھیں اور حل کریں۔ جوابات چیک کرنے کے لیے "جواب دیکھیں" پر کلک کریں۔' if language == 'ur' else 'Read each question carefully and solve. Click "Show Answer" to check your solution.'}</p>
        </div>
        
        {questions_html}
    </main>
    
    <script>
        function toggleAnswer(id) {{
            const answer = document.getElementById(id);
            if (answer.style.display === 'none' || answer.style.display === '') {{
                answer.style.display = 'block';
            }} else {{
                answer.style.display = 'none';
            }}
        }}
    </script>
    
    <footer>
        <p>🇵🇰 DeepTutor - Practice makes perfect!</p>
    </footer>
</body>
</html>
"""
        
        (output_dir / "practice.html").write_text(html_content, encoding="utf-8")
    
    def _generate_quick_reference(self, output_dir: Path, topics: List[Topic], language: str):
        """Generate quick reference page with formulas and key concepts"""
        
        reference_html = ""
        for topic in topics:
            title = topic.name if language != "ur" else (topic.name_ur or topic.name)
            
            # Get key formulas/concepts based on topic
            key_concepts = self._get_key_concepts(topic, language)
            
            reference_html += f"""
            <section class="reference-section">
                <h3>{title}</h3>
                {key_concepts}
            </section>
            """
        
        html_content = f"""<!DOCTYPE html>
<html lang="{language}" dir="{'rtl' if language == 'ur' else 'ltr'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{'فوری حوالہ' if language == 'ur' else 'Quick Reference'} - DeepTutor</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <header class="header">
        <a href="index.html" class="back-btn">← {'واپس' if language == 'ur' else 'Back'}</a>
        <h1>{'فوری حوالہ' if language == 'ur' else 'Quick Reference'}</h1>
    </header>
    
    <main class="reference-content">
        <div class="print-btn">
            <button onclick="window.print()">🖨️ {'پرنٹ کریں' if language == 'ur' else 'Print'}</button>
        </div>
        
        {reference_html}
    </main>
    
    <footer>
        <p>🇵🇰 DeepTutor - Your quick reference guide</p>
    </footer>
</body>
</html>
"""
        
        (output_dir / "reference.html").write_text(html_content, encoding="utf-8")
    
    def _generate_progress_tracker(self, output_dir: Path, topics: List[Topic], language: str):
        """Generate progress tracking page"""
        
        topics_rows = ""
        for i, topic in enumerate(topics):
            title = topic.name if language != "ur" else (topic.name_ur or topic.name)
            topics_rows += f"""
            <tr>
                <td>{i+1}</td>
                <td>{title}</td>
                <td><input type="checkbox" id="read_{topic.id}"></td>
                <td><input type="checkbox" id="practice_{topic.id}"></td>
                <td><input type="checkbox" id="mastered_{topic.id}"></td>
                <td><input type="text" placeholder="{'نوٹس' if language == 'ur' else 'Notes'}"></td>
            </tr>
            """
        
        html_content = f"""<!DOCTYPE html>
<html lang="{language}" dir="{'rtl' if language == 'ur' else 'ltr'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{'پیش رفت ٹریکر' if language == 'ur' else 'Progress Tracker'} - DeepTutor</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <a href="index.html" class="back-btn">← {'واپس' if language == 'ur' else 'Back'}</a>
        <h1>{'پیش رفت ٹریکر' if language == 'ur' else 'Progress Tracker'}</h1>
    </header>
    
    <main class="progress-content">
        <div class="stats">
            <div class="stat-card">
                <span id="completed-count">0</span>
                <label>{'مکمل' if language == 'ur' else 'Completed'}</label>
            </div>
            <div class="stat-card">
                <span id="progress-percent">0%</span>
                <label>{'پیش رفت' if language == 'ur' else 'Progress'}</label>
            </div>
        </div>
        
        <table class="progress-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>{'عنوان' if language == 'ur' else 'Topic'}</th>
                    <th>{'پڑھا' if language == 'ur' else 'Read'}</th>
                    <th>{'مشق' if language == 'ur' else 'Practice'}</th>
                    <th>{'مہارت' if language == 'ur' else 'Mastered'}</th>
                    <th>{'نوٹس' if language == 'ur' else 'Notes'}</th>
                </tr>
            </thead>
            <tbody>
                {topics_rows}
            </tbody>
        </table>
        
        <div class="actions">
            <button onclick="saveProgress()" class="btn-primary">
                💾 {'محفوظ کریں' if language == 'ur' else 'Save Progress'}
            </button>
            <button onclick="loadProgress()" class="btn-secondary">
                📂 {'لوڈ کریں' if language == 'ur' else 'Load Progress'}
            </button>
        </div>
    </main>
    
    <script>
        function saveProgress() {{
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            const inputs = document.querySelectorAll('input[type="text"]');
            const data = {{}};
            
            checkboxes.forEach(cb => data[cb.id] = cb.checked);
            inputs.forEach(input => data[input.placeholder] = input.value);
            
            localStorage.setItem('syncora_progress', JSON.stringify(data));
            alert('{'پیش رفت محفوظ ہو گئی!' if language == 'ur' else 'Progress saved!'}');
            updateStats();
        }}
        
        function loadProgress() {{
            const data = JSON.parse(localStorage.getItem('syncora_progress') || '{{}}');
            Object.keys(data).forEach(key => {{
                const element = document.getElementById(key);
                if (element) {{
                    if (element.type === 'checkbox') {{
                        element.checked = data[key];
                    }} else {{
                        element.value = data[key];
                    }}
                }}
            }});
            updateStats();
        }}
        
        function updateStats() {{
            const mastered = document.querySelectorAll('input[id^="mastered_"]:checked').length;
            const total = document.querySelectorAll('input[id^="mastered_"]').length;
            document.getElementById('completed-count').textContent = mastered;
            document.getElementById('progress-percent').textContent = Math.round((mastered / total) * 100) + '%';
        }}
        
        // Load on page load
        document.addEventListener('DOMContentLoaded', loadProgress);
        
        // Update stats on checkbox change
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {{
            cb.addEventListener('change', updateStats);
        }});
    </script>
    
    <footer>
        <p>🇵🇰 DeepTutor - Track your learning journey!</p>
    </footer>
</body>
</html>
"""
        
        (output_dir / "progress.html").write_text(html_content, encoding="utf-8")
    
    def _generate_styles(self, output_dir: Path):
        """Generate CSS stylesheet"""
        
        css_content = """
/* DeepTutor Offline Pack Styles */

:root {
    --primary-color: #01411C;  /* Pakistan Green */
    --secondary-color: #FFFFFF;
    --accent-color: #FFD700;
    --text-color: #333;
    --bg-color: #f5f5f5;
    --card-bg: #ffffff;
    --border-radius: 8px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', 'Jameel Noori Nastaleeq', sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
}

[dir="rtl"] {
    font-family: 'Jameel Noori Nastaleeq', 'Noto Nastaliq Urdu', 'Segoe UI', serif;
}

.header {
    background: linear-gradient(135deg, var(--primary-color), #006400);
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
}

.header h1 {
    font-size: 1.5rem;
}

.header nav a {
    color: white;
    text-decoration: none;
    margin: 0 1rem;
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    transition: background 0.3s;
}

.header nav a:hover,
.header nav a.active {
    background: rgba(255,255,255,0.2);
}

.back-btn {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    background: rgba(255,255,255,0.2);
    border-radius: var(--border-radius);
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.hero {
    text-align: center;
    padding: 2rem;
    background: var(--card-bg);
    border-radius: var(--border-radius);
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.topics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.topic-card {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: var(--border-radius);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.3s, box-shadow 0.3s;
}

.topic-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
}

.topic-card h3 a {
    color: var(--primary-color);
    text-decoration: none;
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
}

.badge.beginner { background: #4CAF50; color: white; }
.badge.intermediate { background: #FF9800; color: white; }
.badge.advanced { background: #f44336; color: white; }

.description {
    margin-top: 0.5rem;
    color: #666;
    font-size: 0.9rem;
}

/* Topic Page Styles */
.topic-content {
    background: var(--card-bg);
    padding: 2rem;
    border-radius: var(--border-radius);
}

.topic-content section {
    margin-bottom: 2rem;
}

.topic-content h2 {
    color: var(--primary-color);
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.placeholder {
    text-align: center;
    padding: 2rem;
    background: var(--bg-color);
    border-radius: var(--border-radius);
}

.btn-primary {
    display: inline-block;
    background: var(--primary-color);
    color: white;
    padding: 1rem 2rem;
    border-radius: var(--border-radius);
    text-decoration: none;
    font-weight: bold;
    transition: background 0.3s;
    border: none;
    cursor: pointer;
}

.btn-primary:hover {
    background: #006400;
}

.btn-secondary {
    display: inline-block;
    background: #666;
    color: white;
    padding: 1rem 2rem;
    border-radius: var(--border-radius);
    text-decoration: none;
    font-weight: bold;
    transition: background 0.3s;
    border: none;
    cursor: pointer;
}

/* Practice Questions */
.practice-content {
    background: var(--card-bg);
    padding: 2rem;
    border-radius: var(--border-radius);
}

.topic-questions {
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #ddd;
}

.question-item {
    background: var(--bg-color);
    padding: 1rem;
    margin: 1rem 0;
    border-radius: var(--border-radius);
}

.answer {
    display: none;
    background: #e8f5e9;
    padding: 1rem;
    margin-top: 0.5rem;
    border-radius: var(--border-radius);
    border-left: 4px solid var(--primary-color);
}

/* Progress Tracker */
.stats {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: var(--card-bg);
    padding: 1.5rem 2rem;
    border-radius: var(--border-radius);
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.stat-card span {
    display: block;
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary-color);
}

.progress-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--card-bg);
}

.progress-table th,
.progress-table td {
    padding: 1rem;
    border: 1px solid #ddd;
    text-align: center;
}

.progress-table th {
    background: var(--primary-color);
    color: white;
}

.progress-table input[type="text"] {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.actions {
    margin-top: 2rem;
    display: flex;
    gap: 1rem;
}

/* Footer */
footer {
    text-align: center;
    padding: 2rem;
    color: #666;
    border-top: 1px solid #ddd;
    margin-top: 2rem;
}

/* Print Styles */
@media print {
    .header nav, .actions, .print-btn, button {
        display: none;
    }
    
    .reference-content {
        padding: 0;
    }
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .header {
        flex-direction: column;
        text-align: center;
    }
    
    .header nav {
        margin-top: 1rem;
    }
    
    .topics-grid {
        grid-template-columns: 1fr;
    }
    
    .stats {
        flex-direction: column;
    }
}
"""
        
        (output_dir / "styles.css").write_text(css_content, encoding="utf-8")
    
    def _generate_metadata(
        self,
        output_dir: Path,
        pack_id: str,
        grade: int,
        subject: str,
        language: str,
        topics: List[Topic]
    ):
        """Generate pack metadata file"""
        
        metadata = {
            "pack_id": pack_id,
            "version": "1.0.0",
            "generator": "DeepTutor Offline Pack Generator",
            "created_at": datetime.now().isoformat(),
            "curriculum_board": "PCTB",
            "grade": grade,
            "subject": subject,
            "language": language,
            "topics_count": len(topics),
            "topics": [
                {
                    "id": t.id,
                    "name": t.name,
                    "name_ur": t.name_ur,
                    "difficulty": t.difficulty.value
                }
                for t in topics
            ]
        }
        
        (output_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def _create_zip(self, source_dir: Path, zip_path: Path):
        """Create zip file from source directory"""
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in source_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(source_dir)
                    zipf.write(file, arcname)
    
    def _get_difficulty_badge(self, difficulty: DifficultyLevel) -> str:
        """Get display text for difficulty level"""
        badges = {
            DifficultyLevel.BEGINNER: "آسان / Easy",
            DifficultyLevel.INTERMEDIATE: "درمیانی / Medium",
            DifficultyLevel.ADVANCED: "مشکل / Hard"
        }
        return badges.get(difficulty, "درمیانی / Medium")
    
    def _get_subject_name_ur(self, subject: str) -> str:
        """Get Urdu name for subject"""
        names = {
            "mathematics": "ریاضی",
            "science": "سائنس",
            "english": "انگریزی",
            "urdu": "اردو"
        }
        return names.get(subject, subject)
    
    def _get_sample_questions(self, topic: Topic, language: str) -> str:
        """Generate sample questions for a topic"""
        # Generate basic questions based on learning objectives
        questions = []
        
        for i, obj in enumerate(topic.learning_objectives[:3]):  # Max 3 questions per topic
            if language == "ur":
                question_text = obj.description_ur or obj.description
            else:
                question_text = obj.description
            
            question_id = f"{topic.id}_q{i+1}"
            questions.append(f"""
            <div class="question-item">
                <p><strong>{'سوال' if language == 'ur' else 'Q'} {i+1}:</strong> {question_text}؟</p>
                <button onclick="toggleAnswer('{question_id}')" class="btn-secondary">
                    {'جواب دیکھیں' if language == 'ur' else 'Show Answer'}
                </button>
                <div class="answer" id="{question_id}">
                    <p>{'جواب جلد آ رہا ہے...' if language == 'ur' else 'Answer coming soon...'}</p>
                </div>
            </div>
            """)
        
        return "".join(questions) if questions else f"<p>{'سوالات جلد آ رہے ہیں...' if language == 'ur' else 'Questions coming soon...'}</p>"
    
    def _get_key_concepts(self, topic: Topic, language: str) -> str:
        """Generate key concepts/formulas for a topic"""
        concepts = []
        
        for obj in topic.learning_objectives:
            if language == "ur":
                concept = obj.description_ur or obj.description
            else:
                concept = obj.description
            
            concepts.append(f"<li>{concept}</li>")
        
        if concepts:
            return f"<ul>{''.join(concepts)}</ul>"
        else:
            return f"<p>{'کلیدی تصورات جلد آ رہے ہیں...' if language == 'ur' else 'Key concepts coming soon...'}</p>"
    
    def list_available_packs(self) -> List[dict]:
        """List all available offline packs"""
        packs = []
        
        for zip_file in self.output_dir.glob("*.zip"):
            try:
                with zipfile.ZipFile(zip_file, 'r') as zipf:
                    if 'metadata.json' in zipf.namelist():
                        metadata = json.loads(zipf.read('metadata.json').decode('utf-8'))
                        metadata['file_path'] = str(zip_file)
                        metadata['size_bytes'] = zip_file.stat().st_size
                        packs.append(metadata)
            except Exception:
                continue
        
        return packs


def main():
    """CLI for generating offline packs"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate DeepTutor Offline Learning Packs")
    parser.add_argument("--grade", type=int, default=9, help="Grade level (9-12)")
    parser.add_argument("--subject", type=str, default="mathematics", 
                       choices=["mathematics", "science", "english", "urdu"])
    parser.add_argument("--language", type=str, default="both",
                       choices=["en", "ur", "both"])
    parser.add_argument("--output", type=str, default="data/offline_packs",
                       help="Output directory")
    parser.add_argument("--list", action="store_true", help="List available packs")
    
    args = parser.parse_args()
    
    generator = OfflinePackGenerator(args.output)
    
    if args.list:
        packs = generator.list_available_packs()
        if packs:
            print("\n📦 Available Offline Packs:")
            for pack in packs:
                size_mb = pack['size_bytes'] / (1024 * 1024)
                print(f"  - {pack['pack_id']}: Grade {pack['grade']} {pack['subject']} ({size_mb:.2f} MB)")
        else:
            print("No offline packs found.")
        return
    
    print(f"🎓 Generating offline pack for Grade {args.grade} {args.subject}...")
    
    pack = generator.generate_pack(
        grade=args.grade,
        subject=args.subject,
        language=args.language
    )
    
    size_mb = pack.size_bytes / (1024 * 1024)
    print(f"✅ Pack generated successfully!")
    print(f"   📁 File: {pack.file_path}")
    print(f"   📊 Size: {size_mb:.2f} MB")
    print(f"   📚 Topics: {len(pack.topics)}")


if __name__ == "__main__":
    main()
