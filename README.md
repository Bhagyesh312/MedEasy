# 🩺 MedEasy AI 2.0 — Intelligent Medical Report Analyzer

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge)](https://medeasy-dpe6.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-MedEasy-black?style=for-the-badge&logo=github)](https://github.com/Bhagyesh312/MedEasy)

> **Transform medical lab reports into plain-language insights with AI-powered analysis, personalized health recommendations, and conversational Q&A.**

Upload a PDF lab report and get:
- 🔬 **AI-powered analysis** of 90+ medical tests with normal/critical flags
- 🥗 **7-Day personalized diet plans** based on your results
- 💪 **Custom exercise recommendations** tailored to your health
- 💬 **Chat with your report** — ask questions in natural language
- 🌍 **Multilingual support** — English, हिंदी, ગુજરાતી
- 📊 **Track progress** — compare reports over time
- 📄 **Export PDF reports** — shareable formatted reports

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Local Development Setup](#-local-development-setup)
- [🔌 API Endpoints](#-api-endpoints)
- [📊 Available Datasets](#-available-datasets)
- [🌐 Environment Variables](#-environment-variables)
- [🚢 Deployment](#-deployment)
- [📝 Sample Reports](#-sample-reports)
- [⚠️ Medical Disclaimer](#️-medical-disclaimer)

---

## ✨ Features

### 🔬 Core Analysis Engine
- **AI-Powered Test Analysis** — Groq LLM (GPT-OSS-120B) reads every test value and explains it in simple, non-medical language
- **90+ Medical Tests Supported** — Complete Blood Count (CBC), Thyroid Panel (TSH, T3, T4), Lipid Profile, Liver Function Tests (LFT), Kidney Function Tests (KFT), Blood Sugar (Glucose, HbA1c), Vitamins (D, B12), Hormones, and more
- **Intelligent Categorization** — Each test automatically flagged as:
  - 🟢 **Normal** — Value within healthy reference range
  - 🟡 **Needs Attention** — Slightly out of range, monitor
  - 🔴 **Critical** — Significantly abnormal, seek medical attention
- **Reference Ranges** — Age, gender, and lab-specific reference ranges displayed for every test
- **2-Sentence Summary** — Concise overall health summary of your entire report
- **Doctor Questions** — AI-generated list of questions to ask your physician based on your results
- **PDF Export** — Download a beautifully formatted PDF report with all findings, explanations, and recommendations
- **Report Comparison** — Upload two reports side-by-side to track improvements or deteriorations over time with visual change indicators

### 🧠 GenAI + Medical NLP Features (5 Advanced Phases)

#### **Phase 1: Medical NLP Extraction**
- **Entity Recognition** — Identifies test names, values, units, and reference ranges from unstructured PDF text
- **Knowledge Enrichment** — Automatically adds medical context from curated knowledge base
- **200+ Medical Mappings** — Terminology dictionary covering common test name variations
- **Supports 90+ Test Types** — Comprehensive coverage across major lab test categories

#### **Phase 2: RAG System (Retrieval-Augmented Generation)**
- **Medical Knowledge Base** — Curated database of medical facts with authoritative citations
- **Semantic Search** — FAISS vector store for fast, context-aware information retrieval
- **Context Manager** — Intelligent context windowing ensures LLM stays within token limits
- **Grounded Generation** — All AI responses backed by verified medical knowledge

#### **Phase 3: Hallucination Verification**
- **Citation Validator** — Ensures every AI claim is backed by knowledge base sources
- **Numeric Validator** — Cross-checks all numbers (test values, ranges) against source data
- **Confidence Scoring** — Each AI response rated for reliability
- **Source Transparency** — Citations displayed for user trust

#### **Phase 4: Conversational Chat**
- **Context-Aware Q&A** — Ask questions about your report in natural language
- **Multi-Turn Conversations** — Maintains full conversation history for coherent dialogue
- **Report-Specific Responses** — Answers grounded in YOUR specific lab results
- **Conversation Management** — Create, list, delete conversations per report
- **Chat History** — Full message history stored in database

#### **Phase 5: AI Content Generators**
- **7-Day Diet Plan Generator** 🥗
  - Personalized meal plans based on your specific lab abnormalities
  - Breakfast, Lunch, Dinner, and 2 Snacks for each day
  - Detailed recipes with ingredients and preparation steps
  - Nutritional rationale for each meal choice
  - Foods to avoid based on your results
  - Formatted modal display with proper React rendering
- **Exercise Plan Generator** 💪
  - Custom workout routines tailored to your health markers
  - Cardio, strength, flexibility recommendations
  - Duration, frequency, and intensity guidance
  - Safety precautions based on critical findings
- **Patient Education Generator** 📚
  - Simplified explanations of complex medical terms
  - What your test results mean for daily life
  - When to seek immediate medical attention

### 🔐 Authentication & Security
- **JWT Authentication** — Secure token-based login with `flask-jwt-extended`
- **Email OTP Verification** — Gmail SMTP integration for account activation
- **Password Security** — Hashed passwords with `werkzeug.security`
- **Rate Limiting** 
  - OTP: 5 requests/hour per IP
  - Login: 10 requests/minute per IP
- **Form Validation** — Name, email format, password strength (8+ chars, uppercase, lowercase, digit, special char), confirm password match
- **Protected Routes** — JWT required for all analysis, history, and chat endpoints

### 🌍 Multilingual Support
- **3 Languages** — English, Hindi (हिंदी), Gujarati (ગુજરાતી)
- **Full Translation** — UI, analysis explanations, summaries, and recommendations
- **Language Toggle** — Switch languages anytime via navbar dropdown
- **Persistent Preference** — Language choice saved in localStorage

### 📱 User Experience
- **Drag & Drop Upload** — Intuitive PDF upload interface
- **Real-Time Processing** — Live feedback during analysis with loading spinners
- **Responsive Design** — Works seamlessly on mobile, tablet, and desktop
- **Collapsible Cards** — Each test result in expandable card format
- **Error Handling** — User-friendly error messages for all failure scenarios
- **404 Page** — Custom not-found page with navigation links

---

## 🏗️ Architecture

MedEasy AI 2.0 is built on a 5-phase advanced GenAI + NLP pipeline:

### **Phase 1: Medical NLP Extraction** (`backend/medical_nlp/`)
- **Entity Recognizer** (`extractor.py`) — Identifies test names, values, units, reference ranges using regex patterns and NLP
- **Knowledge Base** (`knowledge_base.py`) — 200+ medical term mappings and test metadata
- **Knowledge Enricher** (`enricher.py`) — Adds medical context (normal ranges, clinical significance) to extracted entities
- **Supports 90+ Tests** — CBC (WBC, RBC, Hemoglobin, Platelets, MCV, MCH, MCHC), Thyroid (TSH, T3, T4), Lipids (Total Cholesterol, LDL, HDL, Triglycerides), Liver (SGOT, SGPT, Bilirubin, Albumin), Kidney (Creatinine, Urea, BUN), Glucose, HbA1c, Vitamins (D, B12), Hormones (Testosterone, Estrogen, Cortisol), and more

### **Phase 2: RAG System** (`backend/rag/`)
- **Medical Knowledge Base** (`knowledge_base.py`) — Curated collection of medical facts with citations from authoritative sources (MedlinePlus, WHO, CDC)
- **Vector Store** (`vector_store.py`) — FAISS index for semantic search using sentence-transformers
- **Context Manager** (`context_manager.py`) — Intelligent context windowing to fit within LLM token limits (8192 tokens for GPT-OSS-120B)
- **Generator** (`generator.py`) — Creates responses grounded in retrieved medical knowledge
- **RAG Pipeline** — Query → Semantic Search → Rerank → Context Window → LLM Generation

### **Phase 3: Hallucination Verification** (`backend/verification/`)
- **Citation Validator** (`citation_validator.py`) — Ensures all AI claims are backed by knowledge base sources
- **Numeric Validator** (`numeric_validator.py`) — Verifies test values, reference ranges, and percentages against source data
- **Verifier** (`verifier.py`) — Main verification orchestrator, assigns confidence scores (0.0-1.0)
- **Verification Workflow** — Generate Response → Validate Citations → Validate Numbers → Assign Confidence → Return Verified Response

### **Phase 4: Conversational Chat** (`backend/chat/`)
- **Context Manager** (`context_manager.py`) — Maintains conversation history with sliding window
- **Chat Engine** (`chat_engine.py`) — Multi-turn dialogue system with report context awareness
- **API Endpoints** (`api_chat.py`) — RESTful chat operations (create conversation, send message, list conversations, delete)
- **Database Integration** — Conversations and messages stored in PostgreSQL for persistence

### **Phase 5: AI Content Generators** (`backend/generators/`)
- **Diet Plan Generator** (`diet_plan_generator.py`) — Creates personalized 7-day meal plans
  - Analyzes all abnormal test results
  - Generates day-by-day breakfast, lunch, dinner, and 2 snacks
  - Includes detailed recipes, ingredients, and preparation steps
  - Provides foods-to-avoid list
  - Structured output with markdown formatting
- **Exercise Plan Generator** (`exercise_plan_generator.py`) — Custom workout routines
  - Cardio, strength, flexibility recommendations
  - Duration, frequency, intensity tailored to health markers
  - Safety precautions for critical findings
- **Patient Education Generator** (`patient_education_generator.py`) — Simplified explanations
  - Plain-language medical term definitions
  - Daily life impact of test results
  - When to seek immediate care
- **All generators use GenAI** — Creative content generation via Groq LLMs, not rigid templates

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.0 | UI library with hooks (useState, useEffect, useContext, useNavigate) |
| **Vite** | 8.0 | Build tool, dev server, HMR (Hot Module Replacement) |
| **React Router** | 7.1 | Client-side routing (BrowserRouter, Routes, Route, Navigate) |
| **Lucide React** | Latest | Modern icon library (Upload, FileText, Clock, TrendingUp, LogOut, etc.) |
| **Plain CSS** | — | Custom styles, no UI frameworks (full design control) |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Flask** | 3.1.0 | Python web framework, REST API |
| **Groq API** | Latest | AI inference (GPT-OSS-120B, Qwen 3.8-27B) |
| **Medical NLP** | Custom | Entity extraction, knowledge enrichment |
| **spaCy** | 3.7+ | NLP tokenization (optional, not required) |
| **sentence-transformers** | 2.2+ | Embeddings for semantic search |
| **FAISS** | 1.7+ | Vector store for RAG retrieval |
| **PostgreSQL** | 14+ | Relational database (reports, users, findings, conversations) |
| **psycopg2** | 2.9+ | PostgreSQL adapter for Python |
| **PyMuPDF (fitz)** | 1.23+ | Primary PDF text extraction |
| **pdfplumber** | 0.10+ | Fallback PDF extraction + table detection |
| **ReportLab** | 4.0+ | PDF generation for exports |
| **flask-jwt-extended** | 4.6+ | JWT authentication |
| **flask-cors** | 4.0+ | Cross-origin resource sharing |
| **flask-limiter** | 3.5+ | Rate limiting (OTP, login) |
| **python-dotenv** | 1.0+ | Environment variable management |
| **NumPy** | 1.26.4 | Numerical operations (pinned for stability) |

### Database Schema
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| **reports** | Stores uploaded reports | `id`, `user_id`, `patient_name`, `extracted_text`, `overall_summary`, `doctor_questions`, `created_at` |
| **findings** | Individual test results | `id`, `report_id`, `test_name`, `value`, `unit`, `reference_range`, `status`, `explanation`, `your_number_context` |
| **users** | User accounts | `id`, `name`, `email`, `password_hash`, `created_at` |
| **otp_verifications** | Email OTP codes | `id`, `email`, `otp_code`, `expires_at`, `is_verified` |
| **conversations** | Chat conversations | `id`, `user_id`, `report_id`, `title`, `created_at` |
| **messages** | Chat messages | `id`, `conversation_id`, `role` (user/assistant), `content`, `timestamp` |

### AI Models
| Model | Provider | Use Case | Token Limit |
|-------|----------|----------|-------------|
| **openai/gpt-oss-120b** | Groq | Primary analysis, chat, generators | 8,192 tokens |
| **qwen/qwen3.8-27b** | Groq | Fallback model | 32,768 tokens |

### Email Service
| Service | Configuration |
|---------|---------------|
| **Gmail SMTP** | Host: `smtp.gmail.com`, Port: `587`, TLS enabled |
| **App Password** | 16-character password from Google Account settings |

---

## 📁 Project Structure

```
MedEasy/
├── backend/
│   ├── app.py                  # Main Flask app, API routes, serves React build in production
│   ├── analyser.py             # Groq AI integration: analysis, summary, comparison, multilingual
│   ├── extractor.py            # PDF text extraction (PyMuPDF + pdfplumber fallback)
│   ├── db.py                   # All PostgreSQL queries (insert, select, update, delete)
│   ├── pdf_export.py           # ReportLab PDF generator for report exports
│   ├── email_service.py        # Gmail SMTP service for OTP emails
│   │
│   ├── api_chat.py             # Phase 4: Chat API endpoints (POST /api/chat/conversations, etc.)
│   ├── api_generators.py       # Phase 5: Generator API endpoints (POST /api/generate/diet-plan, etc.)
│   │
│   ├── medical_nlp/            # Phase 1: Medical NLP Extraction
│   │   ├── extractor.py        # Entity recognition (test names, values, units, ranges)
│   │   ├── knowledge_base.py   # Medical terminology dictionary (200+ mappings)
│   │   └── enricher.py         # Context enrichment (add normal ranges, significance)
│   │
│   ├── rag/                    # Phase 2: RAG System
│   │   ├── knowledge_base.py   # Medical facts with citations (MedlinePlus, WHO, CDC)
│   │   ├── vector_store.py     # FAISS semantic search (sentence-transformers embeddings)
│   │   ├── context_manager.py  # Context windowing (fit within 8192 tokens)
│   │   └── generator.py        # RAG-enhanced generation
│   │
│   ├── verification/           # Phase 3: Hallucination Verification
│   │   ├── citation_validator.py   # Citation checking against knowledge base
│   │   ├── numeric_validator.py    # Number validation (test values, ranges)
│   │   └── verifier.py             # Main verification orchestrator
│   │
│   ├── chat/                   # Phase 4: Chat System
│   │   ├── context_manager.py  # Conversation memory (sliding window)
│   │   └── chat_engine.py      # Multi-turn chat with report context
│   │
│   ├── generators/             # Phase 5: AI Content Generators
│   │   ├── diet_plan_generator.py       # 7-day meal plans (breakfast, lunch, dinner, snacks)
│   │   ├── exercise_plan_generator.py   # Workout routines (cardio, strength, flexibility)
│   │   └── patient_education_generator.py   # Simplified medical explanations
│   │
│   ├── data/                   # Optional external datasets
│   │   ├── README.md           # Dataset documentation
│   │   ├── who_reference_ranges.json       # WHO lab test standards (included)
│   │   ├── medical_conditions.json         # Common conditions with dietary advice (included)
│   │   ├── integrate_loinc.py              # LOINC database integration script
│   │   ├── integrate_rxnorm.py             # RxNorm medication database script
│   │   └── integrate_usda_food.py          # USDA FoodData Central script
│   │
│   ├── .env                    # Your secrets (NEVER committed to git)
│   ├── .env.example            # Template — copy to .env and fill in values
│   ├── Procfile                # For Render/Heroku deployment
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AuthPage.jsx        # Login / Register / OTP verification UI
│   │   │   ├── UploadPage.jsx      # PDF upload with drag & drop interface
│   │   │   ├── ResultPage.jsx      # Analysis results + Diet Plan + Chat + PDF export
│   │   │   ├── HistoryPage.jsx     # Past reports list with search and filter
│   │   │   ├── ComparePage.jsx     # Side-by-side report comparison with change indicators
│   │   │   └── NotFoundPage.jsx    # Custom 404 page
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Sticky navbar with language toggle + user menu
│   │   │   ├── FindingCard.jsx     # Collapsible test result card (color-coded status)
│   │   │   ├── DietPlanModal.jsx   # Modal for 7-day diet plan display (proper formatting)
│   │   │   ├── DietPlanModal.css   # Styles for diet plan modal
│   │   │   ├── Spinner.jsx         # Loading spinner component
│   │   │   └── Spinner.css         # Spinner styles
│   │   ├── context/
│   │   │   ├── AuthContext.jsx     # JWT auth state (login, logout, token management)
│   │   │   └── LangContext.jsx     # Language state (EN / HI / GU translations)
│   │   ├── api.js                  # All API calls with error handling and token refresh
│   │   ├── App.jsx                 # Main app component with routing
│   │   ├── App.css                 # Global app styles
│   │   ├── main.jsx                # React entry point (ReactDOM.render)
│   │   └── index.css               # CSS reset and base styles
│   ├── public/
│   │   └── favicon.svg             # Medical cross icon
│   ├── dist/                       # Production build output (generated by Vite)
│   ├── .env.example                # Template for frontend env vars
│   ├── package.json                # Node dependencies
│   ├── vite.config.js              # Vite config (dev proxy to Flask, build settings)
│   └── index.html                  # HTML entry point
│
├── database/
│   ├── 01_create_tables.sql        # Core schema — run FIRST
│   ├── 02_sample_data.sql          # Optional test data
│   ├── 03_add_users.sql            # Users and authentication tables
│   ├── 04_add_otp.sql              # OTP verification table
│   ├── 05_add_finding_details.sql  # Additional finding columns
│   └── 06_add_conversations.sql    # Chat system tables (Phase 4)
│
├── start.bat                        # Windows batch script to start both servers
├── stop.bat                         # Windows batch script to stop all servers
├── .gitignore                       # Git ignore rules (secrets, dependencies, builds)
├── README.md                        # This file
├── FEATURES.md                      # Detailed feature documentation
├── CHANGELOG.md                     # Version history
├── DATASETS.md                      # Dataset documentation
├── TESTING_CHECKLIST.md             # QA checklist
├── PROJECT_STATUS.md                # Current project status
├── sterling-accuris-pathology-sample-report-unlocked.pdf    # Sample CBC report
└── sample_thyroid_lipid_report.pdf  # Sample thyroid + lipid report (14 flagged values)
```

---

## 🚀 Local Development Setup

### Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **PostgreSQL 14+** — [Download](https://www.postgresql.org/download/) or use [pgAdmin4](https://www.pgadmin.org/)
- **Groq API Key** — Free at [console.groq.com](https://console.groq.com) (no credit card required)
- **Gmail Account with App Password** — [Enable here](https://myaccount.google.com/apppasswords)

### Step 1: Clone Repository

```bash
git clone https://github.com/Bhagyesh312/MedEasy.git
cd MedEasy
```

### Step 2: Database Setup (pgAdmin4)

1. **Create Database**
   - Open pgAdmin4
   - Right-click "Databases" → "Create" → "Database"
   - Name: `medical_report_db` (or any name you prefer)

2. **Run SQL Migrations** — Open Query Tool and run these files **IN ORDER**:

```sql
-- Run each file separately in the Query Tool (Right-click database → Query Tool)
database/01_create_tables.sql       -- Core schema (reports, findings)
database/03_add_users.sql          -- Users and authentication
database/04_add_otp.sql            -- OTP verification
database/05_add_finding_details.sql -- Enhanced finding columns
database/06_add_conversations.sql   -- Chat system (Phase 4)
```

3. **Optional: Load Sample Data**

```sql
database/02_sample_data.sql        -- Sample reports for testing
```

**⚠️ Important:** Run migrations in the exact order shown above. Skipping files will cause foreign key constraint errors.

### Step 3: Backend Setup

```bash
cd backend

# Copy environment template
cp .env.example .env

# Edit .env and fill in ALL required values (see Environment Variables section)
# Use Notepad, VS Code, or any text editor

# Install Python dependencies
pip install -r requirements.txt

# Start Flask server
python app.py
```

Backend runs at **http://localhost:5000**

### Step 4: Frontend Setup

```bash
# Open a NEW terminal window/tab
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```

Frontend runs at **http://localhost:5173**

The Vite dev server automatically proxies `/api/*` requests to Flask at port 5000 — no CORS issues in development.

### Step 5: Test the Application

1. Open **http://localhost:5173** in your browser
2. Register a new account (you'll receive an OTP email)
3. Verify OTP and login
4. Upload one of the sample PDF reports
5. View analysis, generate diet plan, chat with report

---

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/register` | Register new user | ❌ |
| `POST` | `/api/auth/verify-otp` | Verify email OTP | ❌ |
| `POST` | `/api/auth/resend-otp` | Resend OTP email | ❌ |
| `POST` | `/api/auth/login` | Login user | ❌ |
| `GET` | `/api/auth/me` | Get current user | ✅ JWT |

**Request/Response Examples:**

```javascript
// POST /api/auth/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
// Response: { "message": "Registration successful. OTP sent to email." }

// POST /api/auth/verify-otp
{
  "email": "john@example.com",
  "otp_code": "123456"
}
// Response: { "message": "Email verified successfully. You can now log in." }

// POST /api/auth/login
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
// Response: { "access_token": "eyJ0eXAiOiJKV1QiLC...", "user": { "id": 1, "name": "John Doe", "email": "john@example.com" } }
```

### Core Analysis

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/analyse` | Analyze medical report PDF | ✅ JWT |
| `POST` | `/api/compare` | Compare two reports | ✅ JWT |
| `GET` | `/api/history` | Get user's report history | ✅ JWT |
| `GET` | `/api/export-pdf/<report_id>` | Export report as PDF | ✅ JWT |

**Request/Response Examples:**

```javascript
// POST /api/analyse
// Content-Type: multipart/form-data
FormData {
  "file": <PDF file>,
  "patient_name": "John Doe",
  "language": "en"  // Optional: en, hi, gu
}
// Response: { "report_id": 42, "findings": [...], "overall_summary": "...", "doctor_questions": [...] }

// POST /api/compare
// Content-Type: multipart/form-data
FormData {
  "old_report": <PDF file 1>,
  "new_report": <PDF file 2>,
  "patient_name": "John Doe",
  "language": "en"
}
// Response: { "comparison": [...], "overall_change_summary": "..." }
```

### 🆕 Chat System (Phase 4)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/chat/conversations` | Create new conversation | ✅ JWT |
| `GET` | `/api/chat/conversations` | List user's conversations | ✅ JWT |
| `GET` | `/api/chat/conversations/<id>` | Get conversation details | ✅ JWT |
| `POST` | `/api/chat/conversations/<id>/messages` | Send message | ✅ JWT |
| `DELETE` | `/api/chat/conversations/<id>` | Delete conversation | ✅ JWT |

**Request/Response Examples:**

```javascript
// POST /api/chat/conversations
{
  "report_id": 42,
  "title": "Questions about my thyroid results"
}
// Response: { "conversation_id": 10, "title": "...", "created_at": "..." }

// POST /api/chat/conversations/10/messages
{
  "message": "Why is my TSH level high?"
}
// Response: { "response": "High TSH indicates...", "conversation_id": 10, "timestamp": "..." }
```

### 🆕 AI Content Generators (Phase 5)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/generate/diet-plan` | Generate 7-day diet plan | ✅ JWT |
| `POST` | `/api/generate/exercise-plan` | Generate exercise routine | ✅ JWT |
| `POST` | `/api/generate/patient-education` | Generate simplified explanation | ✅ JWT |

**Request/Response Examples:**

```javascript
// POST /api/generate/diet-plan
{
  "report_id": 42
}
// Response: {
//   "diet_plan": "## 7-Day Personalized Diet Plan\n\n### Day 1\n**Breakfast:**...",
//   "report_id": 42,
//   "generated_at": "2024-01-15T10:30:00Z"
// }

// POST /api/generate/exercise-plan
{
  "report_id": 42,
  "fitness_level": "beginner"  // Optional: beginner, intermediate, advanced
}

// POST /api/generate/patient-education
{
  "report_id": 42,
  "topic": "thyroid function"  // Optional: specific topic to explain
}
```

---

## 📊 Available Datasets

MedEasy can be enhanced with additional medical datasets for more accurate analysis. See `backend/data/README.md` for detailed integration instructions.

### ✅ Included Datasets (Ready to Use)

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| **WHO Reference Ranges** | WHO | 50+ tests | International lab test standards |
| **Medical Conditions Database** | Curated | 7 conditions | Dietary advice for common conditions |
| **Medical Terminology Dictionary** | MedlinePlus | 200+ mappings | Test name variations and aliases |

### 🔵 External Integrations (Optional)

| Dataset | Source | Size | Purpose | Setup |
|---------|--------|------|---------|-------|
| **LOINC** | Regenstrief Institute | 90,000+ codes | Standardized lab test codes | Run `backend/data/integrate_loinc.py` |
| **RxNorm** | U.S. NLM | 400,000+ names | Medication database | Run `backend/data/integrate_rxnorm.py` |
| **USDA FoodData Central** | USDA | 350,000+ foods | Nutrition data for diet plans | Run `backend/data/integrate_usda_food.py` |

**To integrate external datasets:**

```bash
cd backend/data

# LOINC (requires download from https://loinc.org)
python integrate_loinc.py

# RxNorm (auto-downloads from NLM)
python integrate_rxnorm.py

# USDA FoodData Central (requires API key in .env)
python integrate_usda_food.py
```

---

## 🌐 Environment Variables

### Backend (`.env`)

Copy `backend/.env.example` to `backend/.env` and fill in ALL values:

```env
# ── Groq AI API ────────────────────────────────────────────────────────────────
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Get free key at https://console.groq.com (no credit card required)

# ── Database ───────────────────────────────────────────────────────────────────
DB_HOST=localhost
DB_PORT=5432
DB_NAME=medical_report_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password

# ── JWT Secret ─────────────────────────────────────────────────────────────────
JWT_SECRET_KEY=your_long_random_secret_key_here_at_least_32_chars
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# ── Flask Environment ──────────────────────────────────────────────────────────
FLASK_ENV=development
# Use "production" when deploying

# ── Email Service (Gmail SMTP) ─────────────────────────────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
# Get App Password at https://myaccount.google.com/apppasswords
# Format: xxxx xxxx xxxx xxxx (remove spaces when pasting)
SMTP_FROM=MedEasy <your-email@gmail.com>

# ── Server Port ────────────────────────────────────────────────────────────────
PORT=5000

# ── Optional: USDA API (for enhanced diet plans) ───────────────────────────────
USDA_API_KEY=your_usda_api_key
# Get free key at https://fdc.nal.usda.gov/api-key-signup.html
```

### Frontend (`.env` - optional)

```env
VITE_API_URL=http://localhost:5000
# Only needed if deploying frontend separately
```

---

## 🚢 Deployment

**Current Live Deployment:** https://medeasy-dpe6.onrender.com

### Architecture
- **Backend:** Render Web Service (Flask)
- **Database:** Neon Serverless PostgreSQL (Singapore region)
- **Frontend:** Served by Flask from `frontend/dist/` build

### Deploy to Render (Free Tier)

#### 1. Build Frontend

```bash
cd frontend
npm run build
# Creates frontend/dist/ folder
```

#### 2. Create Render Web Service

1. Go to [render.com](https://render.com) and create account
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** `medeasy`
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`

#### 3. Environment Variables

Add all variables from `backend/.env.example` in Render dashboard:

```
GROQ_API_KEY=gsk_...
DB_HOST=your-neon-db-host.neon.tech
DB_PORT=5432
DB_NAME=medical_report_db
DB_USER=your_neon_user
DB_PASSWORD=your_neon_password
JWT_SECRET_KEY=generate_new_secret_for_production
FLASK_ENV=production
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=MedEasy <your-email@gmail.com>
```

#### 4. Database Setup (Neon)

1. Go to [neon.tech](https://neon.tech) and create account
2. Create new project → Choose region
3. Copy connection string
4. Use pgAdmin or psql to connect and run SQL migrations:

```bash
# Connect via psql
psql "postgresql://user:password@host/database?sslmode=require"

# Or use Neon SQL Editor in dashboard
```

Run migrations in order (same as local setup).

#### 5. Deploy

- Push code to GitHub
- Render auto-deploys on push to `main` branch
- View logs in Render dashboard
- Access at `https://your-app-name.onrender.com`

### Alternative: Deploy to Heroku

```bash
# Install Heroku CLI
heroku login
heroku create medeasy

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set GROQ_API_KEY=gsk_...
# ... (set all env vars)

# Deploy
git push heroku main

# Run migrations
heroku pg:psql < database/01_create_tables.sql
# ... (run all migrations)
```

---

## 📝 Sample Reports

Two sample PDF reports are included for testing:

| File | Test Types | Flagged Values | Use Case |
|------|------------|----------------|----------|
| `sterling-accuris-pathology-sample-report-unlocked.pdf` | Complete Blood Count (CBC) | 3 abnormal | Test basic analysis |
| `sample_thyroid_lipid_report.pdf` | Thyroid, Lipid, Liver, Glucose, Vitamins | 14 abnormal | Test comprehensive analysis + diet plan |

**Recommended Test Flow:**

1. Upload `sample_thyroid_lipid_report.pdf`
2. View analysis (should show 14 flagged tests)
3. Click "Generate 7-Day Diet Plan" button
4. View formatted diet plan modal
5. Start a conversation in chat
6. Ask: "Why is my cholesterol high?"
7. Export PDF report
8. Upload another report and use Compare feature

---

## 🧪 Testing Checklist

See `TESTING_CHECKLIST.md` for full QA checklist covering:
- ✅ Authentication flow (register, OTP, login)
- ✅ PDF upload and analysis
- ✅ All 90+ test types recognized
- ✅ Color-coded status (normal, attention, critical)
- ✅ Multilingual support (EN, HI, GU)
- ✅ Chat functionality (create, send, delete)
- ✅ Diet plan generation (formatting)
- ✅ Exercise plan generation
- ✅ PDF export
- ✅ Report comparison
- ✅ Rate limiting
- ✅ Error handling

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `README.md` | This file — complete project overview |
| `FEATURES.md` | Detailed feature documentation with screenshots |
| `CHANGELOG.md` | Version history and release notes |
| `DATASETS.md` | Dataset documentation and integration guides |
| `TESTING_CHECKLIST.md` | QA checklist for testing all features |
| `PROJECT_STATUS.md` | Current project status and known issues |
| `backend/data/README.md` | External dataset integration instructions |

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

## ⚠️ Medical Disclaimer

**IMPORTANT:** MedEasy AI 2.0 is an educational tool that explains lab reports in plain language. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment.

- ❌ **Do NOT** use for medical diagnoses
- ❌ **Do NOT** make medical decisions based solely on this tool
- ❌ **Do NOT** delay seeking medical advice
- ✅ **Always** consult a qualified healthcare professional for medical concerns
- ✅ **Always** bring your original lab report to your doctor

The AI-generated explanations, diet plans, and exercise recommendations are for informational purposes only. Your doctor has access to your complete medical history and is the only person qualified to interpret your results in context.

---

## 👨‍💻 Author

**Bhagyesh Patel**
- GitHub: [@Bhagyesh312](https://github.com/Bhagyesh312)
- Email: bhagyeshpatel312@gmail.com

---

## 🙏 Acknowledgments

- **Groq** — Ultra-fast AI inference API
- **MedlinePlus** — Medical knowledge base (NIH)
- **WHO** — Lab test reference ranges
- **React** — UI library
- **Flask** — Backend framework
- **PostgreSQL** — Database

---

## 📞 Support

For issues, questions, or feature requests:
1. Check existing [GitHub Issues](https://github.com/Bhagyesh312/MedEasy/issues)
2. Create a new issue with detailed description
3. For bugs, include error messages and reproduction steps

---

<div align="center">

**Made with ❤️ for better healthcare accessibility**

⭐ Star this repo if you find it helpful!

[Live Demo](https://medeasy-dpe6.onrender.com) • [Report Bug](https://github.com/Bhagyesh312/MedEasy/issues) • [Request Feature](https://github.com/Bhagyesh312/MedEasy/issues)

</div>
