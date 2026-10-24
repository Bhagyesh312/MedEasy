"""
Context manager for conversations - handles conversation history and context retrieval.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from .schemas import (
    Conversation, ConversationMessage, ConversationContext,
    MessageRole, MessageType
)


class ConversationContextManager:
    """Manages conversation context and history."""
    
    def __init__(self, db_connection=None):
        """
        Initialize context manager.
        
        Args:
            db_connection: Optional database connection for persistence
        """
        self.db = db_connection
        self._active_conversations: Dict[str, Conversation] = {}
    
    def create_conversation(
        self,
        user_id: int,
        report_id: Optional[int] = None,
        report_summary: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            user_id: ID of the user
            report_id: Optional report ID for context
            report_summary: Optional summary of the report
            
        Returns:
            New Conversation object
        """
        conversation_id = str(uuid.uuid4())
        
        context = ConversationContext(
            user_id=user_id,
            report_id=report_id,
            report_summary=report_summary
        )
        
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            context=context
        )
        
        # Add system message
        system_message = self._create_system_message(conversation_id, report_summary)
        conversation.add_message(system_message)
        
        # Cache in memory
        self._active_conversations[conversation_id] = conversation
        
        # Persist to database if available
        if self.db:
            self._save_conversation_to_db(conversation)
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation object or None if not found
        """
        # Check memory cache first
        if conversation_id in self._active_conversations:
            return self._active_conversations[conversation_id]
        
        # Load from database if available
        if self.db:
            conversation = self._load_conversation_from_db(conversation_id)
            if conversation:
                self._active_conversations[conversation_id] = conversation
                return conversation
        
        return None
    
    def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        **kwargs
    ) -> ConversationMessage:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            role: Role of the message sender
            content: Message content
            message_type: Type of message
            **kwargs: Additional message fields
            
        Returns:
            Created ConversationMessage
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message_id = str(uuid.uuid4())
        message = ConversationMessage(
            message_id=message_id,
            role=role,
            content=content,
            message_type=message_type,
            **kwargs
        )
        
        conversation.add_message(message)
        
        # Persist to database
        if self.db:
            self._save_message_to_db(conversation_id, message)
        
        return message
    
    def get_context_for_generation(
        self,
        conversation_id: str,
        max_messages: int = 10,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Get formatted context for LLM generation.
        
        Args:
            conversation_id: ID of the conversation
            max_messages: Maximum number of recent messages
            max_tokens: Maximum tokens in context window
            
        Returns:
            Dictionary with formatted context
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Get messages within token limit
        messages = conversation.get_context_window(max_tokens)
        
        # Limit to max_messages
        if len(messages) > max_messages:
            messages = messages[-max_messages:]
        
        # Format for LLM
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Add conversation context
        context_info = {
            "messages": formatted_messages,
            "conversation_context": {
                "report_id": conversation.context.report_id,
                "report_summary": conversation.context.report_summary,
                "key_findings": conversation.context.key_findings,
                "topic": conversation.context.topic,
                "medical_terms": conversation.context.medical_terms_discussed
            }
        }
        
        return context_info
    
    def update_context(
        self,
        conversation_id: str,
        **context_updates
    ):
        """
        Update conversation context.
        
        Args:
            conversation_id: ID of the conversation
            **context_updates: Context fields to update
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Update context fields
        for key, value in context_updates.items():
            if hasattr(conversation.context, key):
                setattr(conversation.context, key, value)
        
        conversation.updated_at = datetime.utcnow()
        
        if self.db:
            self._save_conversation_to_db(conversation)
    
    def close_conversation(self, conversation_id: str, summary: Optional[str] = None):
        """
        Mark a conversation as inactive.
        
        Args:
            conversation_id: ID of the conversation
            summary: Optional summary of the conversation
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.is_active = False
            conversation.summary = summary
            conversation.updated_at = datetime.utcnow()
            
            if self.db:
                self._save_conversation_to_db(conversation)
    
    def _create_system_message(
        self,
        conversation_id: str,
        report_summary: Optional[str]
    ) -> ConversationMessage:
        """Create initial system message."""
        system_content = (
            "I'm your medical AI assistant. I can help you understand your medical reports, "
            "answer questions about your test results, and provide evidence-based health information. "
        )
        
        if report_summary:
            system_content += f"\n\nI have access to your report: {report_summary}"
        
        system_content += (
            "\n\nMy responses are grounded in medical knowledge and verified for accuracy. "
            "However, I cannot replace professional medical advice. Please consult with your healthcare provider "
            "for personalized medical guidance."
        )
        
        return ConversationMessage(
            message_id=str(uuid.uuid4()),
            role=MessageRole.SYSTEM,
            content=system_content,
            message_type=MessageType.TEXT
        )
    
    # Database persistence methods (placeholder implementations)
    
    def _save_conversation_to_db(self, conversation: Conversation):
        """Save conversation to database."""
        if not self.db:
            return
        
        try:
            # Note: Actual implementation would depend on database schema
            # For now, we'll store as JSON in a conversations table
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO conversations (conversation_id, user_id, data, created_at, updated_at, is_active)
                VALUES (%s, %s, %s::jsonb, %s, %s, %s)
                ON CONFLICT (conversation_id) DO UPDATE 
                SET data = EXCLUDED.data, updated_at = EXCLUDED.updated_at, is_active = EXCLUDED.is_active
            """, (
                conversation.conversation_id,
                conversation.user_id,
                conversation.model_dump_json(),
                conversation.created_at,
                conversation.updated_at,
                conversation.is_active
            ))
            self.db.commit()
        except Exception as e:
            print(f"Error saving conversation to DB: {e}")
            self.db.rollback()
    
    def _load_conversation_from_db(self, conversation_id: str) -> Optional[Conversation]:
        """Load conversation from database."""
        if not self.db:
            return None
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT data FROM conversations WHERE conversation_id = %s
            """, (conversation_id,))
            
            result = cursor.fetchone()
            if result:
                return Conversation.model_validate_json(result[0])
        except Exception as e:
            print(f"Error loading conversation from DB: {e}")
        
        return None
    
    def _save_message_to_db(self, conversation_id: str, message: ConversationMessage):
        """Save individual message to database."""
        # In current implementation, messages are part of conversation JSON
        # For better performance, could have separate messages table
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self._save_conversation_to_db(conversation)
