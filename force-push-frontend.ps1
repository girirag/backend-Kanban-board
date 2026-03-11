Write-Host "Force pushing frontend with latest changes..." -ForegroundColor Yellow
Set-Location "C:\Users\Giriraghav Kishore\projects\kanban-frontend"

Write-Host "Aborting rebase..." -ForegroundColor Cyan
git rebase --abort

Write-Host "Pulling with merge strategy..." -ForegroundColor Cyan
git pull origin main --strategy=ours --no-edit

Write-Host "Pushing updates..." -ForegroundColor Cyan
git push origin main

Write-Host ""
Write-Host "Frontend updated successfully!" -ForegroundColor Green
Write-Host "Visit: https://github.com/girirag/Frontend-Kanban-board" -ForegroundColor Cyan

Set-Location "C:\Users\Giriraghav Kishore\projects\firstApp"
Read-Host "Press Enter to exit"
