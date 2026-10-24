# 🚀 MedEasy AI 2.0 - Quick Start Guide

## ⚡ Super Quick Start (One Command!)

### **Windows:**
```cmd
start.bat
```

That's it! The script will:
- ✅ Start backend server (Flask)
- ✅ Start frontend server (React)  
- ✅ Open your browser automatically
- ✅ Show you the localhost URL

---

## 🔗 **Your Application URLs:**

Once started, your application will be available at:

### **Main Application** (React Frontend):
🌐 **http://localhost:5173**

### **Backend API:**
🔧 **http://localhost:5000**

### **API Documentation:**
- Health Check: http://localhost:5000/api/health
- Chat API: http://localhost:5000/api/chat/health
- Generators: http://localhost:5000/api/generate/health

---

## 📋 **Available Scripts:**

### **`start.bat`** - Start Everything ▶️
Starts both frontend and backend servers.
```cmd
start.bat
```

### **`stop.bat`** - Stop Everything ⏹️
Stops all running servers.
```cmd
stop.bat
```

---

## 🎯 **What You Can Do:**

### **1. Medical Report Analysis** 📄
- Upload PDF medical reports
- Get AI-powered analysis
- View structured findings
- Export results as PDF

### **2. Conversational AI Chat** 💬 (NEW!)
- Ask questions about your reports
- Multi-turn conversations
- Evidence-grounded responses
- Verification scores

### **3. AI Content Generators** 🎨 (NEW!)
- Generate personalized diet plans (7 days)
- Create custom workout routines (4 weeks)
- Get daily health tips
- Receive educational content
- Discover wellness activities

### **4. Report Management** 📊
- View report history
- Compare reports over time
- Track health trends
- Secure user accounts

---

## 🛠️ **Manual Start (If Needed):**

### **Option A: Using PowerShell**
```powershell
# Start backend
cd backend
python app.py

# Start frontend (in another terminal)
cd frontend
npm run dev
```

### **Option B: Using Command Prompt**
```cmd
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 🔧 **First Time Setup:**

If you just cloned the project:

### **1. Install Backend Dependencies:**
```cmd
cd backend
pip install -r requirements.txt
```

### **2. Install Frontend Dependencies:**
```cmd
cd frontend
npm install
```

### **3. Set Up Database:**
- Open pgAdmin4
- Connect to `medical-report` database
- Run: `database/06_add_conversations.sql`

### **4. Configure Environment:**
- Check `backend/.env` has your database credentials
- Verify `GROQ_API_KEY` is set

### **5. Run the Application:**
```cmd
start.bat
```

---

## ✅ **Verify Everything Works:**

### **Test 1: Frontend**
Open: http://localhost:5173
- You should see the MedEasy login page

### **Test 2: Backend API**
Open: http://localhost:5000/api/health
- Should return: `{"status": "ok"}`

### **Test 3: Chat API** (NEW!)
Open: http://localhost:5000/api/chat/health
- Should return: `{"status": "healthy", "rag_enabled": true}`

### **Test 4: Generators API** (NEW!)
Open: http://localhost:5000/api/generate/health
- Should return: `{"status": "healthy", "generators_available": [...]}`

---

## 🐛 **Troubleshooting:**

### **Issue: "Python not found"**
- Install Python 3.8+ from python.org
- Make sure to check "Add Python to PATH" during installation

### **Issue: "Node not found"**
- Install Node.js 16+ from nodejs.org
- Restart your terminal after installation

### **Issue: "Port already in use"**
- Stop the servers: `stop.bat`
- Close any programs using ports 5000 or 5173
- Start again: `start.bat`

### **Issue: "Module not found"**
**Backend:**
```cmd
cd backend
pip install -r requirements.txt
```

**Frontend:**
```cmd
cd frontend
npm install
```

### **Issue: "Database connection error"**
- Make sure PostgreSQL is running
- Check `backend/.env` has correct credentials:
  ```
  DB_HOST=localhost
  DB_PORT=5432
  DB_NAME=medical-report
  DB_USER=postgres
  DB_PASSWORD=your_password
  ```

---

## 📚 **Documentation:**

### **For Users:**
- Main Application: http://localhost:5173
- Just upload a report and see AI analysis!

### **For Developers:**

**Project Structure:**
```
Medical_report/
├── start.bat              ← START HERE!
├── stop.bat               ← Stop servers
├── backend/
│   ├── app.py            ← Main Flask app
│   ├── api_chat.py       ← Chat API (NEW)
│   ├── api_generators.py ← Generators API (NEW)
│   ├── chat/             ← Chat system (NEW)
│   ├── generators/       ← AI generators (NEW)
│   ├── verification/     ← Verification (NEW)
│   ├── rag/              ← RAG system
│   └── medical_nlp/      ← Medical NLP
└── frontend/
    ├── src/
    │   ├── pages/        ← React pages
    │   └── components/   ← React components
    └── package.json
```

**API Endpoints:**
- Auth: `/api/auth/*`
- Reports: `/api/upload`, `/api/reports`
- Analysis: `/api/analyse`
- Chat: `/api/chat/*` (NEW!)
- Generators: `/api/generate/*` (NEW!)

---

## 🎓 **Tech Stack:**

### **Frontend:**
- React 19
- Vite
- React Router
- Lucide Icons

### **Backend:**
- Python 3.12
- Flask
- PostgreSQL
- Groq AI (120B LLM)

### **AI/ML:**
- Medical NLP (entity extraction)
- RAG (retrieval-augmented generation)
- Sentence transformers
- FAISS vector search
- Hallucination verification

### **Generative AI:**
- 120B parameter language models
- Creative content generation
- Multi-turn conversations
- Context-aware responses

---

## 🎉 **Features Highlight:**

### **Phase 1: Medical NLP** ✅
- Entity extraction from reports
- Medical terminology normalization
- Structured data extraction

### **Phase 2: RAG System** ✅
- Evidence-grounded responses
- Citation tracking
- Semantic search

### **Phase 3: Verification** ✅
- Citation validation
- Numeric consistency checking
- Confidence scoring

### **Phase 4: Conversational Chat** ✅ NEW!
- Multi-turn conversations
- Context management
- Report-aware responses

### **Phase 5: AI Generators** ✅ NEW!
- Diet plan generation
- Exercise routine creation
- Educational content
- Health tips

---

## 🚀 **Ready to Go!**

Just run:
```cmd
start.bat
```

And visit: **http://localhost:5173**

Enjoy your AI-powered medical intelligence platform! 🎊

---

## 📞 **Need Help?**

- Check the troubleshooting section above
- Review `backend/.env` configuration
- Verify database is running
- Ensure all dependencies are installed

---

**Built with ❤️ using Generative AI + NLP**
