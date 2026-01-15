#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Question Extractor for RAG-based exam processing

Extracts questions from PDF text using LLM.
Works with plain text from PyPDF2 (no MinerU dependency).
"""

import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Any, Optional

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI

from src.services.config import get_agent_params
from src.services.llm import get_llm_config


SYSTEM_PROMPT = """You are a professional document analysis assistant. Your task is to extract all questions, challenges, tasks, or problems from the provided document.

This document could be:
- An exam paper with numbered questions
- A hackathon challenge document with tasks/challenges
- A problem set or assignment
- Any document containing questions or tasks to be solved

Please carefully analyze the content and extract ALL questions, challenges, or tasks. For each item, extract:
1. Number or identifier (e.g., "1.", "Challenge 1", "Task A", "Problem 1", etc.)
2. Complete text content describing the question/challenge/task

Please return results in JSON format as follows:
```json
{
    "questions": [
        {
            "question_number": "1",
            "question_text": "Complete content of the question/challenge/task...",
            "images": []
        },
        {
            "question_number": "2", 
            "question_text": "Complete content of another question/challenge/task...",
            "images": []
        }
    ]
}
```

Important Notes:
1. Extract ALL questions, challenges, tasks, or problems - do not miss any
2. Keep the original text, do not modify or summarize
3. For multiple choice questions, include all options in question_text
4. Set images field to empty array []
5. Return valid JSON format
6. Look for patterns like: numbered items, "Challenge X", "Task X", "Problem X", "Question X", bullet points, etc.
7. If the document has sections with challenges/problems, extract each one as a separate question
8. Even if there's only one question/challenge, still return it in the questions array
"""

def extract_questions_from_text(
    text_content: str,
    api_key: str = None,
    base_url: str = None,
    model: str = None,
) -> list[dict[str, Any]]:
    """
    Use LLM to analyze text content and extract questions.
    
    Args:
        text_content: Plain text content from PDF
        api_key: OpenAI API key (optional, uses config if not provided)
        base_url: API endpoint URL (optional)
        model: Model name (optional)
        
    Returns:
        List of questions with question_number, question_text, images
    """
    # Get LLM config if not provided
    if not api_key or not base_url or not model:
        llm_config = get_llm_config()
        api_key = api_key or llm_config.api_key
        base_url = base_url or llm_config.base_url
        model = model or llm_config.model
    
    print(f"📡 Using LLM: {model} at {base_url}")
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # Limit text length for API
    max_chars = 15000
    truncated_text = text_content[:max_chars]
    if len(text_content) > max_chars:
        truncated_text += "\n\n[... remaining content truncated ...]"
    
    user_prompt = f"""Exam paper content:

{truncated_text}

Please analyze the above exam paper content, extract all question information, and return in JSON format.
"""
    
    try:
        print("🔄 Calling LLM for question extraction...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        
        result_text = response.choices[0].message.content
        print(f"📝 LLM response length: {len(result_text)} chars")
        
        # Try to extract JSON from the response
        # Handle markdown code blocks
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
        elif "```" in result_text:
            json_start = result_text.find("```") + 3
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
        
        # Try to find JSON object if not wrapped in code blocks
        if not result_text.startswith("{"):
            # Try to find { ... } pattern
            brace_start = result_text.find("{")
            if brace_start != -1:
                # Find matching closing brace
                brace_count = 0
                for i, c in enumerate(result_text[brace_start:]):
                    if c == "{":
                        brace_count += 1
                    elif c == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            result_text = result_text[brace_start:brace_start + i + 1]
                            break
        
        result_data = json.loads(result_text)
        questions = result_data.get("questions", [])
        
        print(f"✓ Extracted {len(questions)} questions")
        
        # Debug: show first question if any
        if questions:
            print(f"   First question: {questions[0].get('question_text', 'N/A')[:80]}...")
        else:
            print(f"⚠️ No questions found in response. Raw response preview:")
            print(f"   {response.choices[0].message.content[:500]}...")
        
        return questions
        
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse LLM response as JSON: {e}")
        print(f"   Response text: {result_text[:500]}...")
        return []
    except Exception as e:
        print(f"✗ LLM extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_questions_from_paper_rag(
    paper_dir: str = None,
    pdf_path: str = None,
    output_dir: str = None
) -> bool:
    """
    Extract questions from a parsed paper directory or PDF.
    
    Args:
        paper_dir: Path to parsed paper directory (with auto/markdown file)
        pdf_path: Path to PDF file (will be extracted directly)
        output_dir: Output directory (defaults to paper_dir)
        
    Returns:
        True if successful
    """
    text_content = None
    output_path = None
    paper_name = None
    
    # Option 1: Use already parsed paper directory
    if paper_dir:
        paper_dir = Path(paper_dir)
        auto_dir = paper_dir / "auto"
        
        if not auto_dir.exists():
            auto_dir = paper_dir
        
        # Find markdown file
        md_files = list(auto_dir.glob("*.md"))
        if md_files:
            md_file = md_files[0]
            print(f"📄 Reading markdown file: {md_file.name}")
            with open(md_file, encoding='utf-8') as f:
                text_content = f.read()
            paper_name = paper_dir.name
            output_path = paper_dir if output_dir is None else Path(output_dir)
        else:
            print(f"✗ No markdown file found in {auto_dir}")
            return False
    
    # Option 2: Extract directly from PDF
    elif pdf_path:
        from src.agents.question.tools.pdf_parser_rag import extract_pdf_text
        
        pdf_path = Path(pdf_path)
        print(f"📄 Extracting text from PDF: {pdf_path.name}")
        
        try:
            text_content, _ = extract_pdf_text(str(pdf_path))
            paper_name = pdf_path.stem
            
            if output_dir:
                output_path = Path(output_dir)
            else:
                # Create temp output directory
                project_root = Path(__file__).parent.parent.parent.parent.parent
                output_path = project_root / "data" / "user" / "question" / "mimic_papers" / paper_name
            
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"✗ Failed to extract PDF text: {e}")
            return False
    else:
        print("✗ Either paper_dir or pdf_path must be provided")
        return False
    
    if not text_content or not text_content.strip():
        print("✗ No text content to analyze")
        return False
    
    # Extract questions using LLM
    questions = extract_questions_from_text(text_content)
    
    if not questions:
        print("✗ No questions extracted")
        return False
    
    # Save results
    output_data = {
        "paper_name": paper_name,
        "extraction_method": "rag_pypdf2",
        "extracted_at": datetime.now().isoformat(),
        "questions": questions
    }
    
    output_file = output_path / f"{paper_name}_questions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Questions saved to: {output_file}")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract questions from exam PDF")
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--paper", type=str, help="Path to parsed paper directory")
    input_group.add_argument("--pdf", type=str, help="Path to PDF file")
    
    parser.add_argument("-o", "--output", type=str, help="Output directory")
    
    args = parser.parse_args()
    
    success = extract_questions_from_paper_rag(
        paper_dir=args.paper,
        pdf_path=args.pdf,
        output_dir=args.output
    )
    
    sys.exit(0 if success else 1)
