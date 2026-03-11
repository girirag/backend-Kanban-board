Write-Host "Fixing Frontend Push..." -ForegroundColor Yellow
Set-Location "C:\Users\Giriraghav Kishore\projects\kanban-frontend"

Write-Host "Pulling latest changes..." -ForegroundColor Cyan
git pull origin main --rebase

Write-Host "Pushing updates..." -ForegroundColor Cyan
git push origin main

Write-Host ""
Write-Host "Frontend updated successfully!" -ForegroundColor Green
Write-Host "Visit: https://github.com/girirag/Frontend-Kanban-board" -ForegroundColor Cyan

Set-Location "C:\Users\Giriraghav Kishore\projects\firstApp"
Read-Host "Press Enter to exit"
