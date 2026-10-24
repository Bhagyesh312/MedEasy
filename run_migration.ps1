# Run database migration for Phase 4 Chat System

$env:PGPASSWORD = "kali"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  MedEasy AI - Database Migration" -ForegroundColor Cyan
Write-Host "  Phase 4: Chat System Tables" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Connecting to database: medical-report..." -ForegroundColor Yellow

psql -h localhost -U postgres -d medical-report -f database/06_add_conversations.sql

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS! Migration completed." -ForegroundColor Green
    Write-Host ""
    Write-Host "Tables created:" -ForegroundColor Green
    Write-Host "  ✓ conversations" -ForegroundColor Green
    Write-Host "  ✓ conversation_summaries" -ForegroundColor Green
    Write-Host ""
    Write-Host "Chat system is now ready! 🎉" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ ERROR: Migration failed." -ForegroundColor Red
    Write-Host "Please check the error message above." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
