"""
Schemas for conversational chat system.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Role of message sender."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageType(str, Enum):
    """Type of message content."""
    TEXT = "text"
    REPORT_ANALYSIS = "report_analysis"
    CLARIFICATION = "clarification"
    RECOMMENDATION = "recommendation"
    ERROR = "error"


class ConversationMessage(BaseModel):
    """Single message in a conversation."""
    
    message_id: str
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    sources: List[Dict[str, Any]] = Field(default_factory=list)  # RAG sources if applicable
    verification_score: Optional[float] = None  # From verification system
    tokens_used: Optional[int] = None
    model_name: Optional[str] = None
    
    # Context references
    references_report_id: Optional[int] = None
    references_messages: List[str] = Field(default_factory=list)  # IDs of referenced messages


class ConversationContext(BaseModel):
    """Context information for conversation."""
    
    # User and report context
    user_id: Optional[int] = None
    report_id: Optional[int] = None
    report_summary: Optional[str] = None
    key_findings: List[str] = Field(default_factory=list)
    
    # Conversation metadata
    topic: Optional[str] = None
    intent: Optional[str] = None  # e.g., "clarification", "recommendation", "comparison"
    
    # RAG and knowledge context
    relevant_knowledge: List[str] = Field(default_factory=list)
    medical_terms_discussed: List[str] = Field(default_factory=list)


class Conversation(BaseModel):
    """Complete conversation thread."""
    
    conversation_id: str
    user_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Messages
    messages: List[ConversationMessage] = Field(default_factory=list)
    
    # Context
    context: ConversationContext = Field(default_factory=ConversationContext)
    
    # Status
    is_active: bool = True
    summary: Optional[str] = None
    
    # Metrics
    total_tokens: int = 0
    average_verification_score: float = 0.0
    
    def add_message(self, message: ConversationMessage):
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        if message.tokens_used:
            self.total_tokens += message.tokens_used
        self._update_verification_average(message)
    
    def _update_verification_average(self, message: ConversationMessage):
        """Update average verification score."""
        if message.verification_score is not None:
            scores = [m.verification_score for m in self.messages if m.verification_score is not None]
            if scores:
                self.average_verification_score = sum(scores) / len(scores)
    
    def get_recent_messages(self, n: int = 10) -> List[ConversationMessage]:
        """Get the N most recent messages."""
        return self.messages[-n:] if len(self.messages) > n else self.messages
    
    def get_context_window(self, max_tokens: int = 4000) -> List[ConversationMessage]:
        """Get messages that fit within token limit."""
        # Estimate tokens (rough: 1 token ≈ 4 chars)
        messages_in_window = []
        current_tokens = 0
        
        for message in reversed(self.messages):
            estimated_tokens = len(message.content) // 4
            if current_tokens + estimated_tokens > max_tokens:
                break
            messages_in_window.insert(0, message)
            current_tokens += estimated_tokens
        
        return messages_in_window


class ChatRequest(BaseModel):
    """Request for chat completion."""
    
    conversation_id: Optional[str] = None  # None for new conversation
    user_id: int
    message: str
    
    # Optional context
    report_id: Optional[int] = None
    use_rag: bool = True  # Whether to use RAG for grounding
    include_verification: bool = True
    
    # Generation parameters
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=1, le=2000)


class ChatResponse(BaseModel):
    """Response from chat system."""
    
    conversation_id: str
    message: ConversationMessage
    
    # Context used
    sources_used: List[Dict[str, Any]] = Field(default_factory=list)
    verification_result: Optional[Dict[str, Any]] = None
    
    # Metadata
    processing_time_ms: float
    tokens_used: int
    
    # Recommendations
    follow_up_suggestions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
