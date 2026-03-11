Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing Updates to GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Backend
Write-Host "Updating Backend Repository..." -ForegroundColor Yellow
Set-Location "C:\Users\Giriraghav Kishore\projects\kanban-backend"

git add .
$backendStatus = git status --porcelain
if ($backendStatus) {
    git commit -m "Update: Enhanced UI with red theme, improved drag-drop, emoji column headers"
    git push origin main
    Write-Host "✓ Backend pushed successfully!" -ForegroundColor Green
} else {
    Write-Host "✓ Backend - No changes to commit" -ForegroundColor Yellow
}

Write-Host ""

# Frontend
Write-Host "Updating Frontend Repository..." -ForegroundColor Yellow
Set-Location "C:\Users\Giriraghav Kishore\projects\kanban-frontend"

git add .
$frontendStatus = git status --porcelain
if ($frontendStatus) {
    git commit -m "Update: Enhanced UI with red theme, improved drag-drop, emoji column headers, better typography"
    git push origin main
    Write-Host "✓ Frontend pushed successfully!" -ForegroundColor Green
} else {
    Write-Host "✓ Frontend - No changes to commit" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All Updates Pushed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repositories:" -ForegroundColor Yellow
Write-Host "  Backend:  https://github.com/girirag/backend-Kanban-board" -ForegroundColor Cyan
Write-Host "  Frontend: https://github.com/girirag/Frontend-Kanban-board" -ForegroundColor Cyan
Write-Host ""

Set-Location "C:\Users\Giriraghav Kishore\projects\firstApp"
Read-Host "Press Enter to exit"
