# MedEasy — Medical Report Simplifier

**Live:** https://medeasy-dpe6.onrender.com

> Upload a lab report PDF and get a plain-language explanation with colour-coded results, doctor questions, PDF export, report comparison, and multilingual support.

---

## Features

- **AI Analysis** — Groq (Llama 3.3 70B) reads every test value and explains it in simple language
- **Colour-coded results** — Normal / High / Low / Critical with reference ranges
- **Overall summary** — plain paragraph summarising the full report
- **Doctor questions** — AI-generated questions to bring to your next appointment
- **PDF export** — download a formatted report PDF
- **Report comparison** — compare two reports side by side to track changes over time
- **Multilingual** — switch between English, Hindi (हिंदी) and Gujarati (ગુજરાતી)
- **Authentication** — JWT login/register with email OTP verification (Gmail SMTP)
- **Form validation** — name, email, password strength, confirm password, patient name
- **Rate limiting** — OTP: 5/hr per IP, Login: 10/min per IP
- **Responsive** — works on mobile, tablet and desktop

---

## Tech Stack

| Layer    | Technology |
|----------|------------|
| Frontend | React 19, Vite 8, plain CSS |
| Backend  | Flask (Python 3.11+) |
| AI       | Groq API — Llama 3.3 70B |
| Database | PostgreSQL 14+ |
| Auth     | JWT (flask-jwt-extended) + Email OTP |
| Email    | Gmail SMTP |
| PDF      | ReportLab |
| Icons    | Lucide React |
| Rate limiting | flask-limiter |

---

## Project Structure

```
MedEasy/
├── backend/
│   ├── app.py              Flask API + serves React build in production
│   ├── analyser.py         Groq AI — analysis, summary, compare, multilingual
│   ├── extractor.py        PDF text extraction (PyMuPDF + pdfplumber)
│   ├── db.py               All PostgreSQL queries
│   ├── pdf_export.py       ReportLab PDF generator
│   ├── email_service.py    Gmail SMTP OTP sender
│   ├── .env                Your secrets (never committed)
│   ├── .env.example        Template — copy to .env and fill in
│   ├── Procfile            For Render/Heroku deployment
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AuthPage.jsx        Login / Register / OTP verification
│   │   │   ├── UploadPage.jsx      PDF upload with drag & drop
│   │   │   ├── ResultPage.jsx      Analysis results + PDF export
│   │   │   ├── HistoryPage.jsx     Past reports list
│   │   │   ├── ComparePage.jsx     Side-by-side report comparison
│   │   │   └── NotFoundPage.jsx    404 page
│   │   ├── components/
│   │   │   ├── Navbar.jsx          Sticky nav with language toggle + user menu
│   │   │   ├── FindingCard.jsx     Collapsible test result card
│   │   │   └── Spinner.jsx
│   │   ├── context/
│   │   │   ├── AuthContext.jsx     JWT auth state
│   │   │   └── LangContext.jsx     EN / HI / GU translations
│   │   └── api.js                  All API calls with error handling
│   ├── public/
│   │   └── favicon.svg             Medical cross icon
│   ├── .env.example
│   └── vite.config.js              Dev proxy + production build config
│
├── database/
│   ├── 01_create_tables.sql        Core schema — run first
│   ├── 02_sample_data.sql          Optional test data
│   ├── 03_add_users.sql            Users table
│   └── 04_add_otp.sql              OTP verification table
│
├── sample_thyroid_lipid_report.pdf     Sample report for testing
├── .gitignore
└── README.md
```

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- A free [Groq API key](https://console.groq.com)
- A Gmail account with [App Password](https://myaccount.google.com/apppasswords) enabled

### 1 — Database (pgAdmin4)

Create a database (e.g. `medical_report_db`), then run these SQL files in order using the Query Tool:

```
database/01_create_tables.sql
database/03_add_users.sql
database/04_add_otp.sql
```

Optionally load test data:
```
database/02_sample_data.sql
```

### 2 — Backend

```bash
cd backend
cp .env.example .env
# Edit .env and fill in all values
pip install -r requirements.txt
python app.py
```

Backend runs at **http://localhost:5000**

### 3 — Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

The Vite dev server proxies `/api` requests to Flask automatically — no CORS issues in development.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Free key from [console.groq.com](https://console.groq.com) |
| `DB_HOST` | PostgreSQL host (default: `localhost`) |
| `DB_PORT` | PostgreSQL port (default: `5432`) |
| `DB_NAME` | Your database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `JWT_SECRET_KEY` | Long random string — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV` | `development` locally, `production` when deployed |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | Your Gmail address |
| `SMTP_PASSWORD` | Gmail App Password (16 chars, no spaces) |
| `SMTP_FROM` | Display name + email e.g. `MedEasy <you@gmail.com>` |
| `PORT` | Port to run on (default: `5000`) |

---

## Deployment

**Live URL:** https://medeasy-dpe6.onrender.com

- Backend hosted on [Render](https://render.com) (Web Service)
- Database hosted on [Neon](https://neon.tech) (PostgreSQL, Singapore region)
- Frontend served by Flask from the `frontend/dist` build

---

## Production Deployment

### Build the frontend

```bash
cd frontend
npm run build
```

This creates `frontend/dist/`. Flask automatically serves it for all non-API routes.

### Run with Gunicorn

```bash
cd backend
gunicorn app:app --bind 0.0.0.0:5000
```

### Deploy on Render (recommended free option)

**Backend — Web Service**
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add all environment variables from `.env.example` in the Render dashboard

**Frontend — Static Site** *(optional — only if deploying separately)*
- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`

---

## Sample Reports

Two sample PDFs are included for testing:

| File | Contents |
|------|----------|
| `sterling-accuris-pathology-sample-report-unlocked.pdf` | CBC (complete blood count) |
| `sample_thyroid_lipid_report.pdf` | Thyroid + Lipid + Liver + Glucose + Vitamins (14 flagged values) |

---

## Medical Disclaimer

MedEasy explains lab reports in plain language only. It does not provide medical diagnoses or replace professional medical advice. Always consult a qualified doctor for medical decisions.
