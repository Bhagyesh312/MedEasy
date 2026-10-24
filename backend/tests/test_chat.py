#!/usr/bin/env python3
"""
Test suite for Phase 4: Conversational Chat System
Tests conversation management, context handling, and chat engine
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chat.schemas import (
    ConversationMessage, Conversation, ConversationContext,
    MessageRole, MessageType, ChatRequest, ChatResponse
)
from chat.context_manager import ConversationContextManager


def test_conversation_schemas():
    """Test conversation data schemas"""
    print("\n=== Testing Conversation Schemas ===")
    
    # Test ConversationMessage
    message = ConversationMessage(
        message_id="msg-1",
        role=MessageRole.USER,
        content="What is my hemoglobin level?",
        message_type=MessageType.TEXT,
        references_report_id=123
    )
    print(f"✓ ConversationMessage: {message.role.value}, type={message.message_type.value}")
    assert message.role == MessageRole.USER
    assert message.content == "What is my hemoglobin level?"
    
    # Test Conversation
    context = ConversationContext(
        user_id=1,
        report_id=123,
        report_summary="Lab results from 2024-01-15",
        key_findings=["Low hemoglobin", "Normal glucose"]
    )
    
    conversation = Conversation(
        conversation_id="conv-1",
        user_id=1,
        context=context
    )
    print(f"✓ Conversation created: {conversation.conversation_id}")
    assert conversation.user_id == 1
    assert conversation.is_active
    
    # Test adding messages
    conversation.add_message(message)
    print(f"✓ Message added: {len(conversation.messages)} messages")
    assert len(conversation.messages) == 1
    
    # Test get_recent_messages
    for i in range(15):
        conversation.add_message(ConversationMessage(
            message_id=f"msg-{i+2}",
            role=MessageRole.ASSISTANT if i % 2 else MessageRole.USER,
            content=f"Message {i+2}",
            message_type=MessageType.TEXT
        ))
    
    recent = conversation.get_recent_messages(n=5)
    print(f"✓ Recent messages: {len(recent)} (expected: 5)")
    assert len(recent) == 5
    
    return True


def test_context_manager():
    """Test conversation context manager"""
    print("\n=== Testing Context Manager ===")
    
    manager = ConversationContextManager(db_connection=None)
    
    # Test create conversation
    conversation = manager.create_conversation(
        user_id=1,
        report_id=123,
        report_summary="Test report"
    )
    print(f"✓ Conversation created: {conversation.conversation_id}")
    assert conversation.user_id == 1
    assert len(conversation.messages) == 1  # System message
    assert conversation.messages[0].role == MessageRole.SYSTEM
    
    # Test get conversation
    retrieved = manager.get_conversation(conversation.conversation_id)
    print(f"✓ Conversation retrieved: {retrieved.conversation_id}")
    assert retrieved is not None
    assert retrieved.conversation_id == conversation.conversation_id
    
    # Test add message
    user_msg = manager.add_message(
        conversation_id=conversation.conversation_id,
        role=MessageRole.USER,
        content="What is hemoglobin?",
        message_type=MessageType.TEXT
    )
    print(f"✓ Message added: {user_msg.message_id}")
    assert user_msg.content == "What is hemoglobin?"
    
    assistant_msg = manager.add_message(
        conversation_id=conversation.conversation_id,
        role=MessageRole.ASSISTANT,
        content="Hemoglobin is a protein in red blood cells.",
        message_type=MessageType.TEXT,
        verification_score=0.95,
        tokens_used=20
    )
    print(f"✓ Assistant message added with verification: {assistant_msg.verification_score}")
    assert assistant_msg.verification_score == 0.95
    
    # Test get context for generation
    context_data = manager.get_context_for_generation(conversation.conversation_id)
    print(f"✓ Context for generation: {len(context_data['messages'])} messages")
    assert 'messages' in context_data
    assert 'conversation_context' in context_data
    assert len(context_data['messages']) == 3  # System + user + assistant
    
    # Test update context
    manager.update_context(
        conversation_id=conversation.conversation_id,
        topic="Hemoglobin Understanding",
        medical_terms_discussed=["hemoglobin", "red blood cells"]
    )
    updated = manager.get_conversation(conversation.conversation_id)
    print(f"✓ Context updated: topic={updated.context.topic}")
    assert updated.context.topic == "Hemoglobin Understanding"
    assert "hemoglobin" in updated.context.medical_terms_discussed
    
    # Test close conversation
    manager.close_conversation(conversation.conversation_id, summary="Discussed hemoglobin basics")
    closed = manager.get_conversation(conversation.conversation_id)
    print(f"✓ Conversation closed: active={closed.is_active}")
    assert not closed.is_active
    assert closed.summary == "Discussed hemoglobin basics"
    
    return True


def test_chat_request_response():
    """Test chat request/response schemas"""
    print("\n=== Testing Chat Request/Response ===")
    
    # Test ChatRequest
    request = ChatRequest(
        user_id=1,
        message="What does my low hemoglobin mean?",
        report_id=123,
        use_rag=True,
        include_verification=True,
        temperature=0.3,
        max_tokens=500
    )
    print(f"✓ ChatRequest: use_rag={request.use_rag}, temp={request.temperature}")
    assert request.user_id == 1
    assert request.use_rag
    assert request.temperature == 0.3
    
    # Test ChatResponse
    message = ConversationMessage(
        message_id="msg-1",
        role=MessageRole.ASSISTANT,
        content="Low hemoglobin may indicate anemia.",
        message_type=MessageType.TEXT,
        verification_score=0.92
    )
    
    response = ChatResponse(
        conversation_id="conv-1",
        message=message,
        sources_used=[
            {"title": "Hemoglobin Guide", "source_type": "medlineplus", "snippet": "..."}
        ],
        verification_result={"status": "verified", "confidence": 0.92},
        processing_time_ms=1250.5,
        tokens_used=50,
        follow_up_suggestions=["What can I do to increase hemoglobin?"],
        warnings=[]
    )
    print(f"✓ ChatResponse: {response.processing_time_ms:.1f}ms, {response.tokens_used} tokens")
    print(f"  Verification: {response.verification_result['status']}")
    print(f"  Follow-ups: {len(response.follow_up_suggestions)}")
    assert response.message.verification_score == 0.92
    assert len(response.sources_used) == 1
    assert len(response.follow_up_suggestions) == 1
    
    return True


def test_conversation_context_window():
    """Test conversation context window management"""
    print("\n=== Testing Context Window ===")
    
    conversation = Conversation(
        conversation_id="conv-test",
        user_id=1
    )
    
    # Add many messages
    for i in range(100):
        msg = ConversationMessage(
            message_id=f"msg-{i}",
            role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
            content=f"Message content {i}" * 50,  # Make it longer
            message_type=MessageType.TEXT
        )
        conversation.add_message(msg)
    
    print(f"✓ Added {len(conversation.messages)} messages")
    
    # Test context window
    window = conversation.get_context_window(max_tokens=1000)
    print(f"✓ Context window: {len(window)} messages fit in 1000 tokens")
    assert len(window) < len(conversation.messages)
    assert len(window) > 0
    
    # Verify ordering
    if len(window) > 1:
        assert window[0].message_id < window[-1].message_id
        print(f"✓ Messages ordered correctly: {window[0].message_id} ... {window[-1].message_id}")
    
    return True


def run_all_tests():
    """Run all Phase 4 chat tests"""
    print("=" * 60)
    print("PHASE 4: CONVERSATIONAL CHAT SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Conversation Schemas", test_conversation_schemas),
        ("Context Manager", test_context_manager),
        ("Chat Request/Response", test_chat_request_response),
        ("Context Window Management", test_conversation_context_window),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"\n✅ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name}: FAILED")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"PHASE 4 TEST RESULTS: {passed}/{len(tests)} passed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ Phase 4 Conversational Chat: CORE COMPONENTS READY")
        print("\nNote: Full chat engine test requires Groq API and initialized RAG system.")
    else:
        print(f"\n⚠️  {failed} test(s) failed - review needed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
