"""
RAG (Retrieval-Augmented Generation) System for MedEasy AI 2.0

Provides evidence-grounded medical explanations with source attribution.
"""

from .schemas import (
    SourceDocument, 
    DocumentChunk, 
    RetrievalResult,
    GenerationContext,
    GeneratedResponse,
    SourceType,
    LicenseType
)
from .knowledge_ingestion import MedicalKnowledgeIngester
from .vector_store import VectorStore
from .retriever import MedicalRetriever
from .generator import GroundedGenerator

__all__ = [
    'SourceDocument',
    'DocumentChunk',
    'RetrievalResult',
    'GenerationContext',
    'GeneratedResponse',
    'SourceType',
    'LicenseType',
    'MedicalKnowledgeIngester',
    'VectorStore',
    'MedicalRetriever',
    'GroundedGenerator',
]
