# COD-Odisha Development Server Starter
# Starts both backend (FastAPI) and frontend (Vite) for development
# Usage: powershell -ExecutionPolicy Bypass -File dev_start.ps1

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  COD-Odisha Development Server" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Get-Location }

# Find Python - check multiple venv locations
$pythonCmd = $null
$venvPaths = @(
    (Join-Path $ProjectRoot ".venv\Scripts\python.exe"),
    (Join-Path $ProjectRoot "venv\Scripts\python.exe"),
    (Join-Path (Split-Path $ProjectRoot -Parent) ".venv\Scripts\python.exe")
)
foreach ($p in $venvPaths) {
    if (Test-Path $p) {
        $pythonCmd = $p
        Write-Host "  Python: $p" -ForegroundColor DarkGray
        break
    }
}
if (-not $pythonCmd) {
    $pythonCmd = "python"
    Write-Host "  Python: system python (no venv found)" -ForegroundColor DarkGray
}

# ============================================================
# Start Backend (FastAPI)
# ============================================================
Write-Host "[Backend] Starting FastAPI server on port 8000..." -ForegroundColor Yellow

$backendDir = Join-Path $ProjectRoot "backend"

$backendJob = Start-Job -ScriptBlock {
    param($dir, $python)
    Set-Location $dir
    & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 2>&1
} -ArgumentList $backendDir, $pythonCmd

Write-Host "  Backend starting... (Job: $($backendJob.Id))" -ForegroundColor Green
Write-Host "  API docs: http://localhost:8000/docs" -ForegroundColor DarkGray

# ============================================================
# Start Frontend (Vite)
# ============================================================
Write-Host ""
Write-Host "[Frontend] Starting Vite dev server on port 5173..." -ForegroundColor Yellow

$frontendDir = Join-Path $ProjectRoot "frontend"

$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    cmd /c npm run dev 2>&1
} -ArgumentList $frontendDir

Write-Host "  Frontend starting... (Job: $($frontendJob.Id))" -ForegroundColor Green
Write-Host "  App: http://localhost:5173" -ForegroundColor DarkGray

# ============================================================
# Monitor
# ============================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Development servers are starting!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Press Ctrl+C to stop all servers" -ForegroundColor DarkGray
Write-Host ""

# Wait a moment, then show early output from both jobs
Start-Sleep -Seconds 5
Write-Host "--- Backend output ---" -ForegroundColor Yellow
Receive-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
Write-Host "--- Frontend output ---" -ForegroundColor Yellow
Receive-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
Write-Host "----------------------" -ForegroundColor DarkGray

try {
    while ($true) {
        # Check if jobs are still running
        $backendState = (Get-Job -Id $backendJob.Id).State
        $frontendState = (Get-Job -Id $frontendJob.Id).State
        
        if ($backendState -eq "Failed") {
            Write-Host "  [Backend] Error:" -ForegroundColor Red
            Receive-Job -Id $backendJob.Id
        }
        if ($frontendState -eq "Failed") {
            Write-Host "  [Frontend] Error:" -ForegroundColor Red
            Receive-Job -Id $frontendJob.Id
        }
        
        Start-Sleep -Seconds 5
    }
} finally {
    Write-Host ""
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
    Stop-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
    Write-Host "Servers stopped." -ForegroundColor Green
}
