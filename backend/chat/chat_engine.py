"""
Main chat engine - integrates RAG, verification, and conversation management.
"""

import time
from typing import Optional, List, Dict, Any
from groq import Groq

from .schemas import (
    ChatRequest, ChatResponse, ConversationMessage,
    MessageRole, MessageType
)
from .context_manager import ConversationContextManager
from rag.retriever import MedicalRetriever
from rag.generator import GroundedGenerator
from verification.verifier import ResponseVerifier


class MedicalChatEngine:
    """Main conversational chat engine for medical Q&A."""
    
    def __init__(
        self,
        groq_api_key: str,
        db_connection=None,
        retriever: Optional[MedicalRetriever] = None,
        generator: Optional[GroundedGenerator] = None,
        verifier: Optional[ResponseVerifier] = None
    ):
        """
        Initialize chat engine.
        
        Args:
            groq_api_key: Groq API key
            db_connection: Database connection for persistence
            retriever: Optional RAG retriever (will create if not provided)
            generator: Optional grounded generator (will create if not provided)
            verifier: Optional response verifier (will create if not provided)
        """
        self.groq_client = Groq(api_key=groq_api_key)
        self.context_manager = ConversationContextManager(db_connection)
        
        # RAG and verification components
        self.retriever = retriever
        self.generator = generator or GroundedGenerator(groq_api_key)
        self.verifier = verifier or ResponseVerifier()
        
        self.model_name = "openai/gpt-oss-120b"
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request and generate response.
        
        Args:
            request: ChatRequest object
            
        Returns:
            ChatResponse with generated answer
        """
        start_time = time.time()
        
        # Get or create conversation
        if request.conversation_id:
            conversation = self.context_manager.get_conversation(request.conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {request.conversation_id} not found")
            conversation_id = request.conversation_id
        else:
            # Create new conversation
            report_summary = self._get_report_summary(request.report_id) if request.report_id else None
            conversation = self.context_manager.create_conversation(
                user_id=request.user_id,
                report_id=request.report_id,
                report_summary=report_summary
            )
            conversation_id = conversation.conversation_id
        
        # Add user message
        user_message = self.context_manager.add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=request.message,
            message_type=MessageType.TEXT,
            references_report_id=request.report_id
        )
        
        # Generate response
        try:
            response_data = self._generate_response(
                conversation_id=conversation_id,
                user_query=request.message,
                use_rag=request.use_rag,
                include_verification=request.include_verification,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # Add assistant message
            assistant_message = self.context_manager.add_message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=response_data['content'],
                message_type=response_data.get('message_type', MessageType.TEXT),
                sources=response_data.get('sources', []),
                verification_score=response_data.get('verification_score'),
                tokens_used=response_data.get('tokens_used'),
                model_name=self.model_name,
                references_messages=[user_message.message_id]
            )
            
            # Update context with discussed terms
            if 'medical_terms' in response_data:
                self._update_conversation_context(conversation_id, response_data['medical_terms'])
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            return ChatResponse(
                conversation_id=conversation_id,
                message=assistant_message,
                sources_used=response_data.get('sources', []),
                verification_result=response_data.get('verification_result'),
                processing_time_ms=processing_time_ms,
                tokens_used=response_data.get('tokens_used', 0),
                follow_up_suggestions=response_data.get('follow_ups', []),
                warnings=response_data.get('warnings', [])
            )
            
        except Exception as e:
            # Add error message
            error_message = self.context_manager.add_message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question.",
                message_type=MessageType.ERROR
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return ChatResponse(
                conversation_id=conversation_id,
                message=error_message,
                processing_time_ms=processing_time_ms,
                tokens_used=0,
                warnings=[str(e)]
            )
    
    def _generate_response(
        self,
        conversation_id: str,
        user_query: str,
        use_rag: bool,
        include_verification: bool,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """
        Generate a response using RAG and LLM.
        
        Args:
            conversation_id: ID of the conversation
            user_query: User's question
            use_rag: Whether to use RAG
            include_verification: Whether to verify response
            temperature: Generation temperature
            max_tokens: Maximum tokens
            
        Returns:
            Dictionary with response data
        """
        # Get conversation context
        context_data = self.context_manager.get_context_for_generation(conversation_id)
        
        # Use RAG if requested and available
        sources = []
        grounded_response = None
        
        if use_rag and self.retriever and self.generator:
            try:
                # Build enhanced query with conversation context
                enhanced_query = self._build_contextual_query(user_query, context_data)
                
                # Generate grounded response
                grounded_response = self.generator.generate(
                    query=enhanced_query,
                    conversation_history=context_data['messages'][-6:],  # Last 3 exchanges
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                response_text = grounded_response.text
                sources = [self._format_source(src) for src in grounded_response.sources]
                
                # Verify if requested
                verification_result = None
                verification_score = None
                
                if include_verification and self.verifier:
                    verification = self.verifier.verify(grounded_response)
                    verification_result = verification.model_dump()
                    verification_score = verification.confidence
                
                return {
                    'content': response_text,
                    'sources': sources,
                    'verification_result': verification_result,
                    'verification_score': verification_score,
                    'tokens_used': len(response_text.split()),  # Rough estimate
                    'message_type': MessageType.TEXT,
                    'medical_terms': self._extract_medical_terms(response_text),
                    'follow_ups': self._generate_follow_ups(user_query, response_text),
                    'warnings': verification_result.get('recommendations', []) if verification_result else []
                }
                
            except Exception as e:
                print(f"RAG generation failed: {e}. Falling back to direct LLM.")
        
        # Fallback: Direct LLM without RAG
        response_text = self._direct_llm_response(
            context_data['messages'],
            user_query,
            temperature,
            max_tokens
        )
        
        return {
            'content': response_text,
            'sources': [],
            'tokens_used': len(response_text.split()),
            'message_type': MessageType.TEXT,
            'medical_terms': self._extract_medical_terms(response_text),
            'follow_ups': self._generate_follow_ups(user_query, response_text)
        }
    
    def _build_contextual_query(self, query: str, context_data: Dict[str, Any]) -> str:
        """Build query enriched with conversation context."""
        context_info = context_data['conversation_context']
        
        # Add report context if available
        if context_info.get('report_summary'):
            query = f"Based on the report: {context_info['report_summary']}\n\nUser question: {query}"
        
        # Add key findings if available
        if context_info.get('key_findings'):
            findings_text = ", ".join(context_info['key_findings'][:3])
            query = f"{query}\n\nKey findings from report: {findings_text}"
        
        return query
    
    def _direct_llm_response(
        self,
        conversation_history: List[Dict[str, str]],
        user_query: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate response using direct LLM without RAG."""
        # Build messages for LLM
        messages = conversation_history.copy()
        
        # Add medical assistant system prompt if not present
        if not any(msg['role'] == 'system' for msg in messages):
            messages.insert(0, {
                'role': 'system',
                'content': (
                    "You are a helpful medical AI assistant. Provide clear, accurate information "
                    "about medical test results and health topics. Always encourage users to consult "
                    "with healthcare professionals for personalized medical advice."
                )
            })
        
        # Call Groq API
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    def _get_report_summary(self, report_id: int) -> Optional[str]:
        """Get summary of a report from database."""
        # Placeholder - would query database
        return f"Medical report #{report_id}"
    
    def _format_source(self, source) -> Dict[str, Any]:
        """Format a SourceDocument for response."""
        return {
            'title': source.title,
            'source_type': source.source_type,
            'url': source.url if source.url else None,
            'snippet': source.content[:200] + "..." if len(source.content) > 200 else source.content
        }
    
    def _extract_medical_terms(self, text: str) -> List[str]:
        """Extract medical terms from text (simple version)."""
        # Placeholder - could use medical_nlp terminology normalizer
        common_terms = ['hemoglobin', 'glucose', 'cholesterol', 'anemia', 'diabetes', 'hypertension']
        found_terms = []
        text_lower = text.lower()
        
        for term in common_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _generate_follow_ups(self, query: str, response: str) -> List[str]:
        """Generate follow-up question suggestions."""
        # Simple heuristic-based suggestions
        follow_ups = []
        
        if 'low' in response.lower() or 'high' in response.lower():
            follow_ups.append("What can I do to improve this value?")
            follow_ups.append("What are the potential health risks?")
        
        if 'normal' in response.lower():
            follow_ups.append("How can I maintain these healthy levels?")
        
        if 'test' in response.lower() or 'result' in response.lower():
            follow_ups.append("When should I get tested again?")
        
        return follow_ups[:3]  # Limit to 3 suggestions
    
    def _update_conversation_context(self, conversation_id: str, medical_terms: List[str]):
        """Update conversation context with new medical terms."""
        conversation = self.context_manager.get_conversation(conversation_id)
        if conversation:
            existing_terms = set(conversation.context.medical_terms_discussed)
            existing_terms.update(medical_terms)
            self.context_manager.update_context(
                conversation_id,
                medical_terms_discussed=list(existing_terms)
            )
    
    def get_conversation_history(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full conversation history.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary with conversation data or None
        """
        conversation = self.context_manager.get_conversation(conversation_id)
        if not conversation:
            return None
        
        return {
            'conversation_id': conversation.conversation_id,
            'user_id': conversation.user_id,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'is_active': conversation.is_active,
            'messages': [
                {
                    'message_id': msg.message_id,
                    'role': msg.role.value,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'sources': msg.sources,
                    'verification_score': msg.verification_score
                }
                for msg in conversation.messages
            ],
            'context': {
                'report_id': conversation.context.report_id,
                'topic': conversation.context.topic,
                'medical_terms': conversation.context.medical_terms_discussed
            },
            'metrics': {
                'total_tokens': conversation.total_tokens,
                'average_verification_score': conversation.average_verification_score,
                'message_count': len(conversation.messages)
            }
        }
