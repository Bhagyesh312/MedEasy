"""
Flask API endpoints for Phase 4 conversational chat system.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import os

from chat.chat_engine import MedicalChatEngine
from chat.schemas import ChatRequest

# Gracefully handle missing RAG dependencies
try:
    from rag.retriever import MedicalRetriever
    from rag.generator import GroundedGenerator
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  RAG modules not available: {e}")
    RAG_AVAILABLE = False
    MedicalRetriever = None
    GroundedGenerator = None

from verification.verifier import ResponseVerifier
from db import get_connection

# Create blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize chat engine (singleton pattern)
_chat_engine = None

def get_chat_engine():
    """Get or create chat engine instance."""
    global _chat_engine
    if _chat_engine is None:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        db_conn = get_connection()
        
        # Initialize RAG components (lazy loading) - optional
        retriever = None
        generator = None
        verifier = None
        
        if RAG_AVAILABLE:
            try:
                retriever = MedicalRetriever()
                generator = GroundedGenerator(groq_api_key, retriever=retriever)
                verifier = ResponseVerifier()
                print("✅ Chat engine initialized with RAG support")
            except Exception as e:
                print(f"⚠️  RAG components not fully initialized: {e}")
                print("   Chat will work without RAG (Groq API only)")
        else:
            print("⚠️  RAG modules not available - using Groq API only")
        
        # Create chat engine (works with or without RAG)
        _chat_engine = MedicalChatEngine(
            groq_api_key=groq_api_key,
            db_connection=db_conn,
            retriever=retriever,
            generator=generator,
            verifier=verifier
        )
    
    return _chat_engine


def auth_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get user_id from session/token
        # For now, simplified - would integrate with existing auth
        user_id = request.json.get('user_id') if request.json else None
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


@chat_bp.route('/message', methods=['POST'])
@auth_required
def send_message():
    """
    Send a message in a conversation.
    
    Request body:
    {
        "user_id": 1,
        "message": "What is my hemoglobin level?",
        "conversation_id": "optional-uuid",
        "report_id": 123,  // optional
        "use_rag": true,
        "include_verification": true,
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    Returns:
    {
        "conversation_id": "uuid",
        "message": {...},
        "sources_used": [...],
        "verification_result": {...},
        "processing_time_ms": 1234.5,
        "follow_up_suggestions": [...]
    }
    """
    try:
        data = request.get_json()
        
        # Validate request
        if not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        
        # Create ChatRequest
        chat_request = ChatRequest(
            conversation_id=data.get('conversation_id'),
            user_id=data['user_id'],
            message=data['message'],
            report_id=data.get('report_id'),
            use_rag=data.get('use_rag', True),
            include_verification=data.get('include_verification', True),
            temperature=data.get('temperature', 0.3),
            max_tokens=data.get('max_tokens', 500)
        )
        
        # Get chat engine and process request
        engine = get_chat_engine()
        response = engine.chat(chat_request)
        
        # Format response
        return jsonify({
            'conversation_id': response.conversation_id,
            'message': {
                'id': response.message.message_id,
                'content': response.message.content,
                'role': response.message.role.value,
                'type': response.message.message_type.value,
                'timestamp': response.message.timestamp.isoformat(),
                'verification_score': response.message.verification_score
            },
            'sources_used': response.sources_used,
            'verification_result': response.verification_result,
            'processing_time_ms': response.processing_time_ms,
            'tokens_used': response.tokens_used,
            'follow_up_suggestions': response.follow_up_suggestions,
            'warnings': response.warnings
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error in send_message: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@chat_bp.route('/conversation/<conversation_id>', methods=['GET'])
@auth_required
def get_conversation(conversation_id):
    """
    Get full conversation history.
    
    Returns:
    {
        "conversation_id": "uuid",
        "user_id": 1,
        "created_at": "2024-01-15T10:30:00",
        "messages": [...],
        "context": {...},
        "metrics": {...}
    }
    """
    try:
        user_id = request.args.get('user_id') or request.json.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        engine = get_chat_engine()
        conversation_data = engine.get_conversation_history(conversation_id)
        
        if not conversation_data:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Verify user ownership
        if conversation_data['user_id'] != int(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(conversation_data), 200
        
    except Exception as e:
        print(f"Error in get_conversation: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@chat_bp.route('/conversations', methods=['GET'])
@auth_required
def list_conversations():
    """
    List all conversations for a user.
    
    Query params:
    - user_id: required
    - active_only: optional (default: false)
    - limit: optional (default: 20)
    
    Returns:
    {
        "conversations": [
            {
                "conversation_id": "uuid",
                "created_at": "...",
                "last_message": "...",
                "message_count": 5,
                "is_active": true
            }
        ]
    }
    """
    try:
        user_id = request.args.get('user_id') or (request.json.get('user_id') if request.json else None)
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 20))
        
        # Query database
        db = get_connection()
        cursor = db.cursor()
        
        query = """
            SELECT conversation_id, created_at, updated_at, is_active,
                   (data->>'summary') as summary,
                   jsonb_array_length(data->'messages') as message_count
            FROM conversations
            WHERE user_id = %s
        """
        params = [user_id]
        
        if active_only:
            query += " AND is_active = TRUE"
        
        query += " ORDER BY updated_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conversations = []
        for row in rows:
            conversations.append({
                'conversation_id': row[0],
                'created_at': row[1].isoformat(),
                'updated_at': row[2].isoformat(),
                'is_active': row[3],
                'summary': row[4],
                'message_count': row[5]
            })
        
        return jsonify({'conversations': conversations}), 200
        
    except Exception as e:
        print(f"Error in list_conversations: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@chat_bp.route('/conversation/<conversation_id>/close', methods=['POST'])
@auth_required
def close_conversation(conversation_id):
    """
    Close (archive) a conversation.
    
    Request body:
    {
        "user_id": 1,
        "summary": "optional summary"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        summary = data.get('summary')
        
        engine = get_chat_engine()
        
        # Verify ownership
        conversation_data = engine.get_conversation_history(conversation_id)
        if not conversation_data:
            return jsonify({'error': 'Conversation not found'}), 404
        
        if conversation_data['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Close conversation
        engine.context_manager.close_conversation(conversation_id, summary)
        
        return jsonify({
            'message': 'Conversation closed successfully',
            'conversation_id': conversation_id
        }), 200
        
    except Exception as e:
        print(f"Error in close_conversation: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Check if chat service is available."""
    try:
        engine = get_chat_engine()
        return jsonify({
            'status': 'healthy',
            'rag_enabled': engine.retriever is not None,
            'verification_enabled': engine.verifier is not None
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
