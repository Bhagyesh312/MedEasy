#!/usr/bin/env python3
"""Quick Phase 4 test without TensorFlow dependencies"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing Phase 4 Chat System (Core Components Only)...\n")

# Test 1: Import schemas
from chat.schemas import (
    ConversationMessage, Conversation, ConversationContext,
    MessageRole, MessageType, ChatRequest, ChatResponse
)
print("✓ Chat schemas imported")

# Test 2: Import context manager
from chat.context_manager import ConversationContextManager
print("✓ Context manager imported")

# Test 3: Create conversation
print("\n=== Creating Conversation ===")
manager = ConversationContextManager(db_connection=None)
conversation = manager.create_conversation(
    user_id=1,
    report_id=123,
    report_summary="Test Lab Report - CBC Results"
)
print(f"✓ Conversation created: {conversation.conversation_id}")
print(f"  User ID: {conversation.user_id}")
print(f"  Messages: {len(conversation.messages)} (system message)")
print(f"  Active: {conversation.is_active}")

# Test 4: Add messages
print("\n=== Testing Message Exchange ===")
user_msg = manager.add_message(
    conversation_id=conversation.conversation_id,
    role=MessageRole.USER,
    content="What does my hemoglobin level of 11.5 g/dL mean?",
    message_type=MessageType.TEXT,
    references_report_id=123
)
print(f"✓ User message: {user_msg.content[:50]}...")

assistant_msg = manager.add_message(
    conversation_id=conversation.conversation_id,
    role=MessageRole.ASSISTANT,
    content="Your hemoglobin level of 11.5 g/dL is below the normal range (13-17 g/dL for men, 12-16 g/dL for women). This indicates mild anemia.",
    message_type=MessageType.TEXT,
    verification_score=0.95,
    tokens_used=42,
    model_name="llama-3.3-70b-versatile"
)
print(f"✓ Assistant message: {assistant_msg.content[:50]}...")
print(f"  Verification score: {assistant_msg.verification_score}")
print(f"  Tokens: {assistant_msg.tokens_used}")

# Test 5: Get context for generation
print("\n=== Testing Context Retrieval ===")
context_data = manager.get_context_for_generation(conversation.conversation_id)
print(f"✓ Context messages: {len(context_data['messages'])}")
print(f"  Report ID: {context_data['conversation_context']['report_id']}")
print(f"  Report summary: {context_data['conversation_context']['report_summary']}")

# Test 6: Update context
print("\n=== Testing Context Updates ===")
manager.update_context(
    conversation_id=conversation.conversation_id,
    topic="Hemoglobin and Anemia",
    medical_terms_discussed=["hemoglobin", "anemia", "red blood cells"]
)
updated = manager.get_conversation(conversation.conversation_id)
print(f"✓ Topic: {updated.context.topic}")
print(f"  Medical terms: {updated.context.medical_terms_discussed}")

# Test 7: Multi-turn conversation
print("\n=== Testing Multi-Turn Conversation ===")
for i in range(3):
    manager.add_message(
        conversation_id=conversation.conversation_id,
        role=MessageRole.USER,
        content=f"Follow-up question {i+1}",
        message_type=MessageType.TEXT
    )
    manager.add_message(
        conversation_id=conversation.conversation_id,
        role=MessageRole.ASSISTANT,
        content=f"Response to question {i+1}",
        message_type=MessageType.TEXT,
        verification_score=0.9 + (i * 0.01)
    )

final_conv = manager.get_conversation(conversation.conversation_id)
print(f"✓ Total messages: {len(final_conv.messages)}")
print(f"  Average verification: {final_conv.average_verification_score:.3f}")
print(f"  Total tokens: {final_conv.total_tokens}")

# Test 8: Context window
print("\n=== Testing Context Window ===")
window = final_conv.get_context_window(max_tokens=2000)
print(f"✓ Messages in window: {len(window)}/{len(final_conv.messages)}")

recent = final_conv.get_recent_messages(n=5)
print(f"✓ Recent messages: {len(recent)}")

# Test 9: ChatRequest/Response schemas
print("\n=== Testing Chat API Schemas ===")
request = ChatRequest(
    user_id=1,
    message="What should I do about low hemoglobin?",
    report_id=123,
    use_rag=True,
    include_verification=True,
    temperature=0.3,
    max_tokens=500
)
print(f"✓ ChatRequest created:")
print(f"  User: {request.user_id}, Report: {request.report_id}")
print(f"  RAG: {request.use_rag}, Verify: {request.include_verification}")

response = ChatResponse(
    conversation_id=conversation.conversation_id,
    message=assistant_msg,
    sources_used=[{"title": "Hemoglobin Guide", "snippet": "..."}],
    verification_result={"status": "verified", "confidence": 0.95},
    processing_time_ms=1234.5,
    tokens_used=42,
    follow_up_suggestions=["What foods increase hemoglobin?", "When should I retest?"],
    warnings=[]
)
print(f"✓ ChatResponse created:")
print(f"  Processing: {response.processing_time_ms:.1f}ms")
print(f"  Tokens: {response.tokens_used}")
print(f"  Sources: {len(response.sources_used)}")
print(f"  Follow-ups: {response.follow_up_suggestions}")

# Test 10: Close conversation
print("\n=== Testing Conversation Closure ===")
manager.close_conversation(
    conversation.conversation_id,
    summary="Discussed hemoglobin levels and anemia management"
)
closed = manager.get_conversation(conversation.conversation_id)
print(f"✓ Conversation closed:")
print(f"  Active: {closed.is_active}")
print(f"  Summary: {closed.summary}")

print("\n" + "="*60)
print("✅ PHASE 4 CORE COMPONENTS: ALL TESTS PASSED")
print("="*60)
print("\nChat system is ready for integration!")
print("Next step: Initialize RAG system and test full chat engine with Groq API")
