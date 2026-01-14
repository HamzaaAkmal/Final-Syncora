#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tools Package - Unified tool collection

Includes:
- rag_tool: RAG retrieval tool
- web_search: Web search tool
- query_item_tool: Query item tool
- paper_search_tool: Paper search tool
- tex_downloader: LaTeX source download tool
- tex_chunker: LaTeX text chunking tool
"""

# Note: lightrag dependency has been removed.
# Using local document retriever instead (src.knowledge.local_retriever)

from .code_executor import run_code, run_code_sync
from .query_item_tool import query_numbered_item
from .rag_tool import rag_search
from .web_search import web_search

# Paper research related tools
try:
    from .paper_search_tool import PaperSearchTool
    from .tex_chunker import TexChunker
    from .tex_downloader import TexDownloader, read_tex_file

    __all__ = [
        "PaperSearchTool",
        "TexChunker",
        "TexDownloader",
        "query_numbered_item",
        "rag_search",
        "read_tex_file",
        "run_code",
        "run_code_sync",
        "web_search",
    ]
except ImportError as e:
    # If import fails (e.g., missing tiktoken), only export basic tools
    print(f"⚠️  Some paper tools import failed: {e}")
    __all__ = [
        "query_numbered_item",
        "rag_search",
        "run_code",
        "run_code_sync",
        "web_search",
    ]
