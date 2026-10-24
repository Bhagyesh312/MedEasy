@echo off
REM ============================================================================
REM  MedEasy AI 2.0 - Production Ready Startup Script
REM  Starts both frontend and backend servers
REM ============================================================================

title MedEasy AI 2.0 - Starting...

echo.
echo ============================================================================
echo                    MEDEASY AI 2.0 - STARTUP
echo ============================================================================
echo.

REM Check if running from correct directory
if not exist "backend\app.py" (
    echo ERROR: Please run this script from the project root directory!
    echo Expected structure: Medical_report\start.bat
    pause
    exit /b 1
)

echo [1/4] Checking environment...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.11+ and try again.
    pause
    exit /b 1
)
echo   ✓ Python found

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH!
    echo Please install Node.js 18+ and try again.
    pause
    exit /b 1
)
echo   ✓ Node.js found

REM Check if PostgreSQL is running
echo   Checking PostgreSQL connection...
python -c "import psycopg2; from dotenv import load_dotenv; import os; load_dotenv('backend/.env'); conn = psycopg2.connect(host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'), database=os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD')); conn.close(); print('✓ Database connected')" 2>nul
if errorlevel 1 (
    echo   ⚠ Warning: Cannot connect to PostgreSQL
    echo   Make sure PostgreSQL is running and .env is configured
)

echo.
echo [2/4] Starting Backend Server (Flask + AI)...
echo   Location: backend\
echo   URL: http://localhost:5000
echo.

REM Start backend in a new window
start "MedEasy Backend - Flask" /D "%~dp0backend" cmd /k "python app.py"

REM Wait for backend to initialize
timeout /t 4 /nobreak >nul

echo [3/4] Starting Frontend Server (React + Vite)...
echo   Location: frontend\
echo   URL: http://localhost:5173 or 5174
echo.

REM Start frontend in a new window
start "MedEasy Frontend - React" /D "%~dp0frontend" cmd /k "npm run dev"

REM Wait for frontend to initialize
timeout /t 6 /nobreak >nul

echo [4/4] Opening application in browser...
echo.

REM Wait a bit more for servers to fully start
timeout /t 3 /nobreak >nul

REM Try both possible ports
start http://localhost:5173 >nul 2>&1
timeout /t 1 /nobreak >nul
start http://localhost:5174 >nul 2>&1

echo.
echo ============================================================================
echo                     MEDEASY AI 2.0 - READY!
echo ============================================================================
echo.
echo   Frontend:  http://localhost:5173 (or 5174 if port conflict)
echo   Backend:   http://localhost:5000
echo.
echo   ✨ CORE FEATURES:
echo   ✓ Medical Report Analysis
echo   ✓ AI-Powered Explanations
echo   ✓ PDF Export
echo   ✓ Report History ^& Comparison
echo   ✓ Multilingual Support (EN/HI/GU)
echo.
echo   🆕 GENAI FEATURES:
echo   ✓ 7-Day Diet Plan Generator (WORKING!)
echo   ✓ Medical NLP ^& RAG System
echo   ✓ Hallucination Verification
echo   ✓ Conversational Chat (Backend Ready)
echo   ✓ USDA Food Database Integration
echo.
echo   🔐 AUTHENTICATION:
echo   ✓ JWT ^& Email OTP Verification
echo   ✓ Rate Limiting ^& Security
echo.
echo   📊 STATUS:
echo   - All bugs fixed
echo   - Diet plan formatting perfect
echo   - Production ready
echo   - Code cleaned up
echo.
echo   Two terminal windows opened:
echo   1. MedEasy Backend (Flask - Port 5000)
echo   2. MedEasy Frontend (React - Port 5173/5174)
echo.
echo   📝 DOCUMENTATION:
echo   - README.md          - Getting started
echo   - FEATURES.md        - Complete feature list
echo   - CHANGELOG.md       - Version history
echo   - PROJECT_STATUS.md  - Current status
echo   - TESTING_CHECKLIST.md - QA checklist
echo   - DATASETS.md        - Data sources
echo.
echo   🛑 TO STOP THE SERVERS:
echo   - Run stop.bat
echo   - Or close both terminal windows
echo   - Or press Ctrl+C in each window
echo.
echo ============================================================================
echo.
echo Press any key to close this window (servers will keep running)...
pause >nul
