# Changelog

All notable changes to MedEasy AI 2.0 will be documented in this file.

## [2.0.0] - 2026-10-11

### 🎉 Major Release: GenAI + NLP Features

This release transforms MedEasy from a simple report analyzer into a comprehensive AI-powered medical intelligence platform.

### Added - Phase 1: Medical NLP Extraction
- **Advanced Entity Recognition** - Identifies 90+ medical test types automatically
- **Medical Knowledge Base** - Curated knowledge base with test information
- **Context Enrichment** - Adds medical context to extracted entities
- **Support for Complex Reports** - Handles multi-page, complex medical PDFs

### Added - Phase 2: RAG System
- **Semantic Search** - FAISS vector store for knowledge retrieval
- **Context Manager** - Intelligent context windowing for LLM
- **Citation-backed Responses** - All AI responses grounded in medical knowledge
- **RAG Generator** - Retrieval-Augmented Generation for accurate responses

### Added - Phase 3: Hallucination Verification
- **Citation Validator** - Ensures all claims are backed by knowledge base
- **Numeric Validator** - Verifies numerical accuracy against source data
- **Confidence Scoring** - Assigns verification scores to AI responses
- **Error Detection** - Identifies and flags potential hallucinations

### Added - Phase 4: Conversational Chat
- **Context-Aware Chat** - Multi-turn conversations about medical reports
- **Conversation Management** - Save, retrieve, and manage chat history
- **API Endpoints** - RESTful chat APIs for frontend integration
- **Database Schema** - Conversations and summaries tables

### Added - Phase 5: AI Content Generators
- **7-Day Diet Plan Generator** - Personalized meal plans based on lab results
  - Nutritional targeting based on deficiencies
  - Vegetarian/vegan/non-vegetarian options
  - Shopping lists and cooking tips
  - Foods to avoid recommendations
- **Exercise Plan Generator** - Custom workout routines
- **Patient Education Generator** - Simplified medical explanations

### Changed
- **Report Summary** - Shortened from 3-4 sentences to 2 sentences for brevity
- **AI Model** - Updated from Llama 3.3 70B to GPT-OSS-120B and Qwen 3.8 (Groq)
- **Model Fallback** - Automatic fallback to alternate models on rate limits
- **Analysis Prompt** - Simplified for better response quality

### Fixed
- **Database Schema** - Fixed `your_number_context` column in findings INSERT
- **Function Name** - Standardized to `get_connection` across all files
- **JSON Parsing** - Added robust error handling for malformed AI responses
- **Diet Plan Display** - Fixed modal to show raw AI content when structured parsing fails
- **Model Availability** - Updated to use working Groq models only
- **SQL Syntax** - Fixed INDEX creation in conversations table migration

### Database Migrations
- **05_add_finding_details.sql** - Added enhanced finding columns
- **06_add_conversations.sql** - Added chat system tables

### Dependencies Added
```
pydantic>=2.0.0
numpy<2.0
sentence-transformers>=2.0.0
qdrant-client>=1.7.0
beautifulsoup4>=4.12.0
scikit-learn>=1.3.0
transformers>=4.30.0
torch>=2.0.0
faiss-cpu>=1.7.4
pytest>=7.4.0
pytest-cov>=4.1.0
```

### Frontend Enhancements
- **Diet Plan Modal** - Beautiful, scrollable modal with formatted content
- **Markdown Rendering** - Proper formatting for AI-generated content
- **Loading States** - Better UX for long-running AI operations
- **Error Handling** - Improved error messages and fallbacks

### Backend Architecture
```
backend/
├── medical_nlp/         - Phase 1: Entity extraction
├── rag/                 - Phase 2: Knowledge retrieval
├── verification/        - Phase 3: Hallucination detection
├── chat/                - Phase 4: Conversational AI
└── generators/          - Phase 5: Content generation
```

### Documentation
- **FEATURES.md** - Complete feature documentation
- **README.md** - Updated with all new features and architecture
- **start.bat** - Enhanced startup script with feature highlights
- **CHANGELOG.md** - This file

### Known Issues
- Shopping list parsing may fail for some diet plan formats (raw content shown as fallback)
- Rate limiting may occur on Groq free tier (automatic model fallback implemented)

---

## [1.0.0] - 2024-12-15

### Initial Release
- Basic medical report analysis
- PDF extraction
- AI-powered explanations
- Color-coded results
- PDF export
- Report comparison
- Multilingual support (EN, HI, GU)
- Authentication with OTP
- PostgreSQL database
- React frontend with Vite
- Flask backend
