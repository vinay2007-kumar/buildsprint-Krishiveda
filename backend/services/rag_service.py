"""
RAG service for government scheme PDFs.

Pipeline: PDF -> text (pypdf) -> chunk (500 chars overlap 50) ->
embeddings (sentence-transformers if available, else TF-IDF-ish keyword search) ->
retrieval -> answer with source citation.

CRITICAL: answers clearly distinguish doc-found vs not-found info.
"""

import os
import re
import structlog
from typing import Optional

logger = structlog.get_logger()

# In-memory store: {doc_id: {"title": str, "chunks": [str], "meta": dict}}
_STORE: dict = {}
_EMBED_MODEL = None


def _get_embedder():
    global _EMBED_MODEL
    if _EMBED_MODEL is not None:
        return _EMBED_MODEL
    try:
        from sentence_transformers import SentenceTransformer
        from backend.config import settings
        _EMBED_MODEL = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded")
    except Exception as e:
        logger.warning("Embeddings unavailable, keyword search fallback", error=str(e))
        _EMBED_MODEL = False
    return _EMBED_MODEL


def extract_pdf_text(path: str) -> str:
    """Extract text with pypdf, fallback pdfplumber."""
    text = ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    except Exception as e:
        logger.warning("pypdf failed", error=str(e))
    if len(text.strip()) < 50:
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
        except Exception as e:
            logger.warning("pdfplumber failed", error=str(e))
    return text.strip()


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list:
    """Simple char-window chunking (robust for Hindi/Gujarati)."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i + size])
        i += size - overlap
    return chunks


def ingest_document(doc_id: str, title: str, text: str, meta: Optional[dict] = None) -> dict:
    chunks = chunk_text(text)
    _STORE[doc_id] = {"title": title, "chunks": chunks, "meta": meta or {}}
    # Precompute embeddings lazily at query time (keeps upload fast)
    return {"doc_id": doc_id, "title": title, "chunks": len(chunks)}


STOPWORDS = {"who", "what", "when", "where", "how", "is", "are", "the", "a", "an",
             "kaun", "kya", "hai", "ke", "ki", "ka", "me", "men", "ko", "se",
             "shu", "chhe", "ma", "na", "ni", "no", "to", "do", "does", "in", "of", "for"}


def _keyword_search(chunks: list, question: str, top_k: int = 3) -> list:
    """Fallback retrieval: stem-prefix overlap scoring (works offline, multilingual-safe).

    Matches on 6-char stem prefixes so 'eligible' hits 'eligibility',
    and ignores stopwords so 'who is ...?' still matches content words.
    """
    qtok = [t for t in re.findall(r"\w+", question.lower()) if t not in STOPWORDS and len(t) > 2]
    if not qtok:
        qtok = re.findall(r"\w+", question.lower())
    stems = {t[:6] for t in qtok}
    scored = []
    for c in chunks:
        cl = c.lower()
        ctok_stems = {t[:6] for t in re.findall(r"\w+", cl)}
        overlap = len(stems & ctok_stems)
        # Bonus for exact phrase hits
        if overlap:
            scored.append((overlap, c))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for _, c in scored[:top_k]]


def query(doc_id: str, question: str, top_k: int = 3) -> dict:
    """Answer question from ingested doc. Always cites source chunks."""
    doc = _STORE.get(str(doc_id))
    if not doc:
        return {"answer": "Document not found. Please upload the scheme PDF first.",
                "source_chunks": [], "confidence": 0.0, "found": False}
    chunks = doc["chunks"]
    # Try semantic search, fallback keyword
    top = []
    try:
        model = _get_embedder()
        if model and model is not False:
            import numpy as np
            q_emb = model.encode([question], normalize_embeddings=True)[0]
            c_emb = model.encode(chunks, normalize_embeddings=True)
            sims = (c_emb @ q_emb)
            idx = np.argsort(sims)[::-1][:top_k]
            top = [chunks[i] for i in idx if sims[i] > 0.15]
    except Exception as e:
        logger.warning("semantic search failed", error=str(e))
    if not top:
        top = _keyword_search(chunks, question, top_k)

    if not top:
        return {
            "answer": ("This information was NOT found in the uploaded document "
                       f"'{doc['title']}'. Please check the official scheme website or helpline. "
                       "I cannot confirm eligibility/benefits beyond the document."),
            "source_chunks": [], "confidence": 0.15, "found": False}

    # Extractive answer: join top chunks (honest RAG for prototype; LLM rewrite optional)
    answer = (
        f"According to the uploaded document '{doc['title']}':\n\n"
        + "\n---\n".join(t[:600] for t in top)
        + "\n\nNote: verify with official sources before applying."
    )
    return {"answer": answer, "source_chunks": top, "confidence": 0.75, "found": True}
