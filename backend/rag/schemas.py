"""
RAG system data schemas for source documents, chunks, and retrieval results.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class SourceType(str, Enum):
    """Type of medical knowledge source."""
    MEDLINEPLUS = "medlineplus"
    CDC = "cdc"
    WHO = "who"
    NIH = "nih"
    EDUCATIONAL = "educational"
    CLINICAL_GUIDELINE = "clinical_guideline"
    RESEARCH = "research"
    MANUAL = "manual"


class LicenseType(str, Enum):
    """Content license type."""
    PUBLIC_DOMAIN = "public_domain"
    CC_BY = "cc_by"
    CC_BY_SA = "cc_by_sa"
    CC_BY_NC = "cc_by_nc"
    CC_BY_NC_SA = "cc_by_nc_sa"
    EDUCATIONAL_USE = "educational_use"
    UNKNOWN = "unknown"


class SourceDocument(BaseModel):
    """Represents a medical knowledge source document."""
    
    source_id: str = Field(..., description="Unique identifier for this source")
    title: str = Field(..., description="Document title")
    url: str = Field(..., description="Source URL")
    source_type: SourceType = Field(..., description="Type of source")
    publisher: str = Field(..., description="Publishing organization")
    license: LicenseType = Field(default=LicenseType.UNKNOWN, description="Content license")
    
    # Content
    full_text: str = Field(..., description="Complete document text")
    summary: Optional[str] = Field(None, description="Brief summary of content")
    
    # Metadata
    published_date: Optional[date] = Field(None, description="Publication date if known")
    last_updated: Optional[date] = Field(None, description="Last update date if known")
    language: str = Field(default="en", description="Content language")
    
    # Medical categorization
    topics: List[str] = Field(default_factory=list, description="Medical topics covered")
    test_names: List[str] = Field(default_factory=list, description="Laboratory tests mentioned")
    conditions: List[str] = Field(default_factory=list, description="Medical conditions discussed")
    
    # Quality indicators
    is_peer_reviewed: bool = Field(default=False)
    credibility_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Source credibility (0-1)")
    
    # Processing metadata
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    ingestion_version: str = Field(default="1.0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = self.model_dump()
        # Convert dates to ISO format
        if self.published_date:
            data["published_date"] = self.published_date.isoformat()
        if self.last_updated:
            data["last_updated"] = self.last_updated.isoformat()
        if self.ingested_at:
            data["ingested_at"] = self.ingested_at.isoformat()
        return data


class DocumentChunk(BaseModel):
    """Represents a semantically chunked passage from a source document."""
    
    chunk_id: str = Field(..., description="Unique chunk identifier")
    source_id: str = Field(..., description="Parent source document ID")
    
    # Content
    text: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., ge=0, description="Position in source document")
    
    # Source attribution
    source_title: str = Field(..., description="Parent document title")
    source_url: str = Field(..., description="Parent document URL")
    source_type: SourceType
    publisher: str
    
    # Embedding
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    
    # Metadata for filtering
    topics: List[str] = Field(default_factory=list)
    test_names: List[str] = Field(default_factory=list)
    conditions: List[str] = Field(default_factory=list)
    
    # License for attribution
    license: LicenseType = Field(default=LicenseType.UNKNOWN)
    
    # Quality
    credibility_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding embedding for readability."""
        data = self.model_dump(exclude={"embedding"})
        return data
    
    def get_citation(self) -> str:
        """Generate a formatted citation for this chunk."""
        return f"{self.source_title}. {self.publisher}. {self.source_url}"


class RetrievalResult(BaseModel):
    """Result from a semantic retrieval query."""
    
    chunk: DocumentChunk
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity or relevance score")
    rank: int = Field(..., ge=1, description="Rank in retrieval results")
    
    def get_formatted_passage(self) -> str:
        """Get formatted passage with citation."""
        return f"{self.chunk.text}\n\nSource: {self.chunk.get_citation()}"


class GenerationContext(BaseModel):
    """Context provided to the LLM for grounded generation."""
    
    # User query
    question: str = Field(..., description="User's question")
    
    # Report-specific context
    test_name: Optional[str] = Field(None, description="Specific test being asked about")
    test_value: Optional[str] = Field(None, description="Test value from report")
    reference_range: Optional[str] = Field(None, description="Reference range from report")
    abnormal_flag: Optional[bool] = Field(None, description="Whether value is flagged")
    
    # Retrieved evidence
    retrieved_passages: List[RetrievalResult] = Field(default_factory=list)
    
    # Conversation history (optional)
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous Q&A pairs for context"
    )
    
    # Language
    language: str = Field(default="en", description="Response language")
    
    def format_for_llm(self) -> str:
        """Format context as a prompt for the LLM."""
        parts = []
        
        # Add test context if available
        if self.test_name:
            parts.append(f"Test: {self.test_name}")
            if self.test_value:
                parts.append(f"Value: {self.test_value}")
            if self.reference_range:
                parts.append(f"Reference Range: {self.reference_range}")
            if self.abnormal_flag is not None:
                status = "Abnormal" if self.abnormal_flag else "Normal"
                parts.append(f"Status: {status}")
            parts.append("")
        
        # Add retrieved passages with source numbers
        if self.retrieved_passages:
            parts.append("Retrieved Medical Information:")
            for i, result in enumerate(self.retrieved_passages, 1):
                parts.append(f"\n[{i}] {result.chunk.text}")
                parts.append(f"    Source: {result.chunk.source_title} ({result.chunk.publisher})")
            parts.append("")
        
        # Add conversation history if available
        if self.conversation_history:
            parts.append("Previous Conversation:")
            for turn in self.conversation_history[-3:]:  # Last 3 turns
                parts.append(f"User: {turn.get('user', '')}")
                parts.append(f"Assistant: {turn.get('assistant', '')}")
            parts.append("")
        
        # Add the question
        parts.append(f"Question: {self.question}")
        
        return "\n".join(parts)


class GeneratedResponse(BaseModel):
    """Response generated by the grounded generator."""
    
    answer: str = Field(..., description="Generated answer")
    citations: List[int] = Field(
        default_factory=list,
        description="Source indices cited in the answer ([1], [2], etc.)"
    )
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Response confidence")
    
    # Source attribution
    sources: List[DocumentChunk] = Field(
        default_factory=list,
        description="Full source chunks for cited passages"
    )
    
    # Limitations and caveats
    limitations: Optional[str] = Field(None, description="Any limitations or caveats")
    requires_clarification: bool = Field(
        default=False,
        description="Whether the question needs clarification"
    )
    
    def format_with_sources(self) -> Dict[str, Any]:
        """Format response with full source information."""
        return {
            "answer": self.answer,
            "citations": [
                {
                    "index": i+1,
                    "text": chunk.text,
                    "source_title": chunk.source_title,
                    "source_url": chunk.source_url,
                    "publisher": chunk.publisher,
                }
                for i, chunk in enumerate(self.sources)
            ],
            "confidence": self.confidence,
            "limitations": self.limitations,
            "requires_clarification": self.requires_clarification,
        }
