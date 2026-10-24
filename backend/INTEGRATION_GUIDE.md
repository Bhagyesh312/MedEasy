# MedEasy AI 2.0 - Quick Integration Guide

## 🚀 5-Minute Integration Steps

### Step 1: Database Migration (2 minutes)

```bash
# Connect to your Neon PostgreSQL database
psql $DATABASE_URL -f database/06_add_conversations.sql

# Or if using environment variable:
psql $NEON_DATABASE_URL -f database/06_add_conversations.sql
```

This creates the `conversations` table for Phase 4 chat persistence.

### Step 2: Initialize RAG System (2 minutes)

```bash
cd backend

# Initialize vector store (one-time setup)
python -m rag.initialize_rag
```

Expected output:
```
Initializing RAG system...
✓ Loading sentence transformer model
✓ Creating knowledge base
✓ Building vector store
✓ Saving to disk
RAG system initialized successfully!
```

**Note:** First run downloads ~80MB model. Subsequent runs are instant.

### Step 3: Integrate Chat API into Flask (1 minute)

Edit `backend/app.py`:

```python
# Add import at top
from api_chat import chat_bp

# Register blueprint (after existing blueprints)
app.register_blueprint(chat_bp)

print("✓ Chat API registered at /api/chat/*")
```

### Step 4: Test the Integration

**Start server:**
```bash
python app.py
```

**Test health endpoint:**
```bash
curl http://localhost:5000/api/chat/health
```

Expected response:
```json
{
  "status": "healthy",
  "rag_enabled": true,
  "verification_enabled": true
}
```

**Test chat message:**
```bash
curl -X POST http://localhost:5000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "What is hemoglobin?",
    "use_rag": true,
    "include_verification": true
  }'
```

Expected response structure:
```json
{
  "conversation_id": "uuid-here",
  "message": {
    "content": "Hemoglobin is a protein...",
    "verification_score": 0.95
  },
  "sources_used": [...],
  "verification_result": {...},
  "follow_up_suggestions": [...]
}
```

---

## 📁 File Structure Summary

```
backend/
├── chat/                          # Phase 4: Chat System
│   ├── __init__.py
│   ├── schemas.py                 # Message, Conversation, Request/Response
│   ├── context_manager.py         # Conversation management
│   └── chat_engine.py             # Main chat processor
│
├── verification/                  # Phase 3: Verification
│   ├── __init__.py
│   ├── schemas.py                 # Verification results
│   ├── citation_validator.py     # Citation checking
│   ├── numeric_validator.py      # Number consistency
│   └── verifier.py                # Main orchestrator
│
├── rag/                           # Phase 2: RAG System
│   ├── schemas.py
│   ├── knowledge_ingestion.py
│   ├── vector_store.py
│   ├── retriever.py
│   └── generator.py
│
├── medical_nlp/                   # Phase 1: Medical NLP
│   ├── schemas.py
│   ├── terminology.py
│   └── extractor.py
│
├── api_chat.py                    # NEW: Chat REST API
├── app.py                         # MODIFY: Register chat_bp
└── requirements.txt               # Already updated

database/
└── 06_add_conversations.sql       # NEW: Conversations table

tests/
├── test_chat.py
├── quick_chat_test.py
├── test_verification.py
└── quick_verification_test.py
```

---

## 🔧 Environment Variables

Ensure these are set in `.env`:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=your_neon_postgres_url

# Optional (for full RAG features)
QDRANT_URL=http://localhost:6333  # If using Qdrant Cloud
QDRANT_API_KEY=your_key            # If using Qdrant Cloud
```

---

## 🧪 Verification Steps

### 1. Test Phase 3 Verification
```bash
cd backend
python tests/quick_verification_test.py
```

Expected: ✅ All tests pass

### 2. Test Phase 4 Chat
```bash
python tests/quick_chat_test.py
```

Expected: ✅ All tests pass

### 3. Test Full Pipeline
```bash
# Start server
python app.py

# In another terminal
curl http://localhost:5000/api/chat/health

# Should return: {"status": "healthy", "rag_enabled": true, ...}
```

---

## 🎯 API Endpoints Reference

### Chat Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/chat/health` | GET | Health check | No |
| `/api/chat/message` | POST | Send message | Yes |
| `/api/chat/conversation/<id>` | GET | Get history | Yes |
| `/api/chat/conversations` | GET | List conversations | Yes |
| `/api/chat/conversation/<id>/close` | POST | Close conversation | Yes |

### Example: Send Message

**Request:**
```json
POST /api/chat/message
{
  "user_id": 1,
  "message": "What does low hemoglobin mean?",
  "conversation_id": null,  // Create new conversation
  "report_id": 123,         // Optional: link to report
  "use_rag": true,
  "include_verification": true,
  "temperature": 0.3,
  "max_tokens": 500
}
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "id": "msg-uuid",
    "content": "Low hemoglobin indicates anemia [1]...",
    "role": "assistant",
    "type": "text",
    "timestamp": "2026-10-11T00:30:00Z",
    "verification_score": 0.95
  },
  "sources_used": [
    {
      "title": "Hemoglobin Guide",
      "source_type": "medlineplus",
      "url": "https://medlineplus.gov/...",
      "snippet": "Hemoglobin is a protein..."
    }
  ],
  "verification_result": {
    "overall_status": "passed",
    "passed": true,
    "confidence": 0.95,
    "citations_valid": 1.0,
    "numeric_consistent": 1.0
  },
  "processing_time_ms": 1234.5,
  "tokens_used": 42,
  "follow_up_suggestions": [
    "What foods increase hemoglobin?",
    "When should I get tested again?"
  ],
  "warnings": []
}
```

---

## ⚠️ Troubleshooting

### Issue: TensorFlow initialization timeout
**Solution:** First request may take 20-30s. Wait for completion. Subsequent requests are fast.

### Issue: RAG system not found
**Solution:** Run `python -m rag.initialize_rag` to create vector store.

### Issue: Database error on conversation creation
**Solution:** Run migration: `psql $DATABASE_URL -f database/06_add_conversations.sql`

### Issue: Import errors
**Solution:** Ensure all dependencies installed: `pip install -r requirements.txt`

### Issue: NumPy version conflict
**Solution:** Downgrade NumPy: `pip install "numpy<2.0"`

---

## 📊 Performance Tips

1. **Warm-up request:** Send a test message on server start to initialize TensorFlow
2. **Connection pooling:** Use PostgreSQL connection pooling for conversations
3. **Caching:** Cache frequently asked questions
4. **Async generation:** Consider background jobs for long conversations
5. **Rate limiting:** Add rate limits to prevent API abuse

---

## 🎉 You're Ready!

All phases (1-4) are now integrated and ready for production use. The MedEasy AI 2.0 platform now features:

✅ Advanced Medical NLP extraction  
✅ Evidence-grounded RAG with citations  
✅ Multi-layer hallucination verification  
✅ Conversational AI chat with context  

**Next:** Deploy to Render and start testing with real users! 🚀
