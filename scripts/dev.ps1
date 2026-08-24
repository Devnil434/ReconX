Write-Host "Starting ReconX infrastructure..."

docker compose up -d

Write-Host ""
Write-Host "PostgreSQL: localhost:5432"
Write-Host "Redis:       localhost:6379"
Write-Host ""
Write-Host "Start API:"
Write-Host "cd apps/api"
Write-Host ".\.venv\Scripts\Activate.ps1"
Write-Host "uvicorn app.main:app --reload --port 8000"
Write-Host ""
Write-Host "Start Web:"
Write-Host "cd apps/web"
Write-Host "npm run dev"
