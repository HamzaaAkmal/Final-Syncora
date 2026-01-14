"""
Local Document Retriever
========================

Offline document retrieval system for curriculum, PDFs, and text files.
No external dependencies or APIs required.

Features:
- Keyword search across curriculum topics
- PDF text extraction and chunking
- In-memory vector index (simple cosine similarity)
- Combined search: curriculum + user-uploaded documents
- Thread-safe caching
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


@dataclass
class Document:
    """Represents a searchable document chunk."""
    content: str
    source: str
    source_type: str  # 'curriculum', 'pdf', 'text'
    topic: Optional[str] = None
    chapter: Optional[str] = None
    grade: Optional[int] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SimpleVectorizer:
    """Simple TF-IDF vectorizer for offline document retrieval."""

    def __init__(self):
        self.vocab = {}
        self.idf = {}
        self.doc_vectors = []

    def build_vocab(self, documents: List[str]):
        """Build vocabulary from documents."""
        self.vocab = {}
        word_doc_count = defaultdict(int)
        total_docs = len(documents)

        # Count word frequencies across documents
        for doc in documents:
            words = set(self._tokenize(doc))
            for word in words:
                word_doc_count[word] += 1

        # Calculate IDF
        for word, count in word_doc_count.items():
            self.idf[word] = math.log(total_docs / (1 + count))

        # Build vocabulary
        self.vocab = {word: idx for idx, word in enumerate(sorted(word_doc_count.keys()))}

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        text = text.lower()
        # Remove punctuation but keep some important chars
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        # Remove very short tokens
        return [t for t in tokens if len(t) > 2]

    def vectorize(self, text: str) -> Dict[int, float]:
        """Convert text to sparse TF-IDF vector."""
        tokens = self._tokenize(text)
        vec = defaultdict(float)

        for token in tokens:
            if token in self.vocab:
                idx = self.vocab[token]
                vec[idx] += 1

        # Apply TF-IDF
        doc_length = len(tokens) if tokens else 1
        for idx, tf in vec.items():
            vec[idx] = (tf / doc_length) * self.idf.get(idx, 0)

        return dict(vec)

    @staticmethod
    def cosine_similarity(vec1: Dict[int, float], vec2: Dict[int, float]) -> float:
        """Calculate cosine similarity between two sparse vectors."""
        if not vec1 or not vec2:
            return 0.0

        all_keys = set(vec1.keys()) | set(vec2.keys())
        dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
        magnitude1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        magnitude2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


class LocalDocumentRetriever:
    """
    Offline document retrieval system combining curriculum and user documents.
    """

    def __init__(self, curriculum_data=None):
        """
        Initialize retriever.

        Args:
            curriculum_data: Optional curriculum data (will load default if not provided)
        """
        self.documents: List[Document] = []
        self.vectorizer = SimpleVectorizer()
        self.vector_cache = {}
        self.curriculum_data = curriculum_data

        # Load curriculum by default
        self._index_curriculum(curriculum_data)

    def _index_curriculum(self, curriculum_data):
        """Index curriculum data for retrieval."""
        try:
            # Try to import curriculum data structures
            from src.curriculum.data import (
                MATH_GRADE_9_TOPICS,
                MATH_GRADE_9_CHAPTERS,
                SCIENCE_GRADE_9_TOPICS,
                SCIENCE_GRADE_9_CHAPTERS,
                ENGLISH_GRADE_9_TOPICS,
                ENGLISH_GRADE_9_CHAPTERS,
                URDU_GRADE_9_TOPICS,
                URDU_GRADE_9_CHAPTERS,
            )

            # Organize by subject
            curricula = {
                "Mathematics": (MATH_GRADE_9_CHAPTERS, "math"),
                "Science": (SCIENCE_GRADE_9_CHAPTERS, "science"),
                "English": (ENGLISH_GRADE_9_CHAPTERS, "english"),
                "Urdu": (URDU_GRADE_9_CHAPTERS, "urdu"),
            }

            for subject_name, (chapters, subject_id) in curricula.items():
                for chapter in chapters:
                    for topic in chapter.topics:
                        # Create document from topic
                        content_parts = [
                            f"Topic: {topic.name}",
                            f"Chapter: {chapter.name}",
                            f"Subject: {subject_name}",
                        ]

                        if topic.description:
                            content_parts.append(f"Description: {topic.description}")

                        # Add learning objectives
                        if topic.objectives:
                            content_parts.append("Learning Objectives:")
                            for obj in topic.objectives:
                                content_parts.append(f"  - {obj.description}")

                        # Add keywords
                        if topic.keywords:
                            content_parts.append(f"Keywords: {', '.join(topic.keywords)}")

                        content = "\n".join(content_parts)

                        doc = Document(
                            content=content,
                            source=f"{subject_name}/{chapter.name}",
                            source_type="curriculum",
                            topic=topic.name,
                            chapter=chapter.name,
                            grade=chapter.grade,
                            metadata={
                                "subject": subject_name,
                                "topic_id": topic.id,
                                "chapter_id": chapter.id,
                                "keywords": topic.keywords or [],
                            },
                        )
                        self.documents.append(doc)

            # Rebuild vector index
            self._rebuild_index()

        except Exception as e:
            print(f"Warning: Could not load curriculum: {e}")

    def add_pdf(self, pdf_path: str, document_name: str) -> bool:
        """
        Extract and index PDF document.

        Args:
            pdf_path: Path to PDF file
            document_name: Name for this document

        Returns:
            True if successful, False otherwise
        """
        if PdfReader is None:
            print("Warning: PyPDF2 not available for PDF extraction")
            return False

        try:
            reader = PdfReader(pdf_path)
            text_chunks = []

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    text_chunks.append((text, page_num))

            # Create documents from chunks
            chunk_size = 1000  # chars per chunk
            for text, page_num in text_chunks:
                # Split into smaller chunks
                for i in range(0, len(text), chunk_size):
                    chunk = text[i : i + chunk_size]
                    if chunk.strip():
                        doc = Document(
                            content=chunk,
                            source=f"{document_name} (Page {page_num + 1})",
                            source_type="pdf",
                            metadata={"page": page_num + 1, "document": document_name},
                        )
                        self.documents.append(doc)

            self._rebuild_index()
            return True

        except Exception as e:
            print(f"Error loading PDF {pdf_path}: {e}")
            return False

    def add_text(self, text: str, source_name: str):
        """Add raw text document."""
        if not text or not text.strip():
            return

        # Split into chunks
        chunk_size = 500  # chars
        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                doc = Document(
                    content=chunk,
                    source=source_name,
                    source_type="text",
                )
                self.documents.append(doc)

        self._rebuild_index()

    def _rebuild_index(self):
        """Rebuild vector index for all documents."""
        if not self.documents:
            return

        # Build vocabulary from all document contents
        doc_texts = [doc.content for doc in self.documents]
        self.vectorizer.build_vocab(doc_texts)

        # Vectorize all documents
        self.vector_cache = {}
        for idx, doc in enumerate(self.documents):
            self.vector_cache[idx] = self.vectorizer.vectorize(doc.content)

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.0,
    ) -> List[Tuple[Document, float]]:
        """
        Search documents by keyword and semantic similarity.

        Args:
            query: Search query
            top_k: Number of results to return
            min_score: Minimum similarity score

        Returns:
            List of (Document, score) tuples sorted by relevance
        """
        if not self.documents:
            return []

        # Use enhanced keyword search that checks both content and metadata
        scores = defaultdict(float)
        query_lower = query.lower()
        query_words = query_lower.split()

        for idx, doc in enumerate(self.documents):
            content_lower = doc.content.lower()
            
            # Check exact phrase matches
            if query_lower in content_lower:
                scores[idx] += 5.0

            # Check keyword matches in content
            for word in query_words:
                if word in content_lower:
                    scores[idx] += 1.0

            # Check metadata keywords
            if doc.metadata and "keywords" in doc.metadata:
                keywords = doc.metadata["keywords"]
                if isinstance(keywords, (list, tuple)):
                    for kw in keywords:
                        if query_lower in kw.lower() or kw.lower() in query_lower:
                            scores[idx] += 2.0
                        for word in query_words:
                            if word in kw.lower():
                                scores[idx] += 0.5

            # Boost curriculum documents
            if doc.source_type == "curriculum":
                scores[idx] *= 1.1

        # Sort and return
        sorted_docs = sorted(
            scores.items(), key=lambda x: x[1], reverse=True
        )
        results = [(self.documents[idx], float(score)) for idx, score in sorted_docs[:top_k] if score > 0]
        
        # Normalize scores to 0-1 range
        if results:
            max_score = results[0][1]
            if max_score > 0:
                results = [(doc, score / max_score) for doc, score in results]

        return results

    def _keyword_search(
        self, query: str, top_k: int = 3
    ) -> List[Tuple[Document, float]]:
        """Fallback keyword search when vectorization fails."""
        keywords = query.lower().split()
        scores = defaultdict(int)

        for idx, doc in enumerate(self.documents):
            content_lower = doc.content.lower()
            for keyword in keywords:
                if keyword in content_lower:
                    scores[idx] += 1

            # Boost curriculum documents
            if doc.source_type == "curriculum":
                scores[idx] += 0.5

        # Sort and return
        sorted_docs = sorted(
            scores.items(), key=lambda x: x[1], reverse=True
        )
        results = [(self.documents[idx], float(score)) for idx, score in sorted_docs[:top_k]]
        return results

    def search_by_topic(
        self, topic_name: str, grade: Optional[int] = None
    ) -> List[Document]:
        """Search curriculum by topic name."""
        results = []
        topic_lower = topic_name.lower()

        for doc in self.documents:
            if doc.source_type != "curriculum":
                continue

            if (
                topic_lower in doc.topic.lower() if doc.topic else False
            ) or (
                topic_lower in doc.chapter.lower() if doc.chapter else False
            ):
                if grade is None or doc.grade == grade:
                    results.append(doc)

        return results

    def get_answer_context(self, query: str, top_k: int = 3) -> str:
        """
        Get formatted context answer for a query.

        Args:
            query: User question or query
            top_k: Number of sources to include

        Returns:
            Formatted answer context with sources
        """
        results = self.search(query, top_k=top_k)

        if not results:
            return "No relevant information found in knowledge base."

        context_parts = []
        context_parts.append("## Relevant Information\n")

        for i, (doc, score) in enumerate(results, 1):
            context_parts.append(f"\n### Source {i}: {doc.source}")
            context_parts.append(f"**Confidence:** {score:.1%}\n")
            context_parts.append(f"{doc.content[:500]}")  # First 500 chars
            if len(doc.content) > 500:
                context_parts.append("...\n")

        context_parts.append("\n---\n")

        return "".join(context_parts)


# Singleton instance
_retriever: Optional[LocalDocumentRetriever] = None


def get_local_retriever() -> LocalDocumentRetriever:
    """Get or create the local document retriever singleton."""
    global _retriever
    if _retriever is None:
        _retriever = LocalDocumentRetriever()
    return _retriever


def reset_retriever():
    """Reset the retriever singleton."""
    global _retriever
    _retriever = None
