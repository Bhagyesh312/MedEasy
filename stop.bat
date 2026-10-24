@echo off
REM ============================================================================
REM  MedEasy AI 2.0 - Stop Script
REM  Stops all MedEasy servers
REM ============================================================================

title MedEasy AI 2.0 - Stopping Servers...

echo.
echo ============================================================================
echo                  MEDEASY AI 2.0 - STOP SERVERS
echo ============================================================================
echo.

echo Stopping all MedEasy servers...
echo.

REM Kill Python processes (Flask backend)
echo [1/2] Stopping Backend (Flask/Python)...
taskkill /F /FI "WindowTitle eq MedEasy Backend*" >nul 2>&1
if errorlevel 1 (
    echo   ⚠ Backend not running or already stopped
) else (
    echo   ✓ Backend stopped
)

REM Kill Node processes (React frontend)
echo [2/2] Stopping Frontend (React/Node)...
taskkill /F /FI "WindowTitle eq MedEasy Frontend*" >nul 2>&1
if errorlevel 1 (
    echo   ⚠ Frontend not running or already stopped
) else (
    echo   ✓ Frontend stopped
)

echo.
echo ============================================================================
echo                  ALL SERVERS STOPPED
echo ============================================================================
echo.
echo All MedEasy servers have been shut down.
echo You can run start.bat to restart them.
echo.
pause
