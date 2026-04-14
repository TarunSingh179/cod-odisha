# COD-Odisha Development Environment Setup
# Run this script once to set up everything for local development
# Usage: powershell -ExecutionPolicy Bypass -File dev_setup.ps1

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  COD-Odisha Development Environment Setup" -ForegroundColor Cyan  
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Get-Location }
Set-Location $ProjectRoot

# ============================================================
# 1. Python Virtual Environment
# ============================================================
Write-Host "[1/5] Setting up Python virtual environment..." -ForegroundColor Yellow

if (-not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to create venv. Make sure Python 3.9+ is installed." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  Virtual environment already exists."
}

# Activate venv
$activateScript = Join-Path $ProjectRoot "venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
}

# ============================================================
# 2. Install Backend Dependencies
# ============================================================
Write-Host ""
Write-Host "[2/5] Installing backend dependencies..." -ForegroundColor Yellow

$pipCmd = Join-Path $ProjectRoot "venv\Scripts\pip.exe"
if (-not (Test-Path $pipCmd)) {
    $pipCmd = "pip"
}

# Install backend requirements
& $pipCmd install -r backend\requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARNING: Some backend dependencies may have failed." -ForegroundColor DarkYellow
} else {
    Write-Host "  Backend dependencies installed." -ForegroundColor Green
}

# Install training requirements
& $pipCmd install -r model_training\requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARNING: Some training dependencies may have failed." -ForegroundColor DarkYellow
} else {
    Write-Host "  Training dependencies installed." -ForegroundColor Green
}

# ============================================================
# 3. Install Frontend Dependencies
# ============================================================
Write-Host ""
Write-Host "[3/5] Installing frontend dependencies..." -ForegroundColor Yellow

if (Get-Command npm -ErrorAction SilentlyContinue) {
    Push-Location frontend
    if (-not (Test-Path "node_modules")) {
        npm install --silent
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  WARNING: npm install had issues." -ForegroundColor DarkYellow
        } else {
            Write-Host "  Frontend dependencies installed." -ForegroundColor Green
        }
    } else {
        Write-Host "  node_modules already exists. Run 'cd frontend && npm install' to update."
    }
    Pop-Location
} else {
    Write-Host "  WARNING: npm not found. Install Node.js 18+ from https://nodejs.org" -ForegroundColor DarkYellow
}

# ============================================================
# 4. Setup Dataset
# ============================================================
Write-Host ""
Write-Host "[4/5] Setting up dataset..." -ForegroundColor Yellow

$archivePath = Join-Path $ProjectRoot "downloads\archive.zip"
$trainImgDir = Join-Path $ProjectRoot "data\COD10K\images\train"

# Check if dataset already has real data
$trainCount = 0
if (Test-Path $trainImgDir) {
    $trainCount = (Get-ChildItem $trainImgDir -File | Measure-Object).Count
}

if ($trainCount -gt 10) {
    Write-Host "  Dataset already set up: $trainCount training images." -ForegroundColor Green
} elseif (Test-Path $archivePath) {
    Write-Host "  Found archive.zip — extracting dataset..."
    $pythonCmd = Join-Path $ProjectRoot "venv\Scripts\python.exe"
    if (-not (Test-Path $pythonCmd)) { $pythonCmd = "python" }
    & $pythonCmd setup_data.py --source "$archivePath" --verify
} else {
    Write-Host "  No dataset archive found at downloads/archive.zip" -ForegroundColor DarkYellow
    Write-Host "  You can still run cloud training without local data." 
    Write-Host "  See: cloud_training/README.md"
}

# ============================================================
# 5. Create .env file
# ============================================================
Write-Host ""
Write-Host "[5/5] Setting up environment configuration..." -ForegroundColor Yellow

$envFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item ".env.example" ".env"
    Write-Host "  Created .env from .env.example" -ForegroundColor Green
    Write-Host "  Edit .env to set your API keys and preferences."
} else {
    Write-Host "  .env already exists."
}

# ============================================================
# Summary
# ============================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  To start development:" -ForegroundColor Cyan
Write-Host "    .\dev_start.ps1" -ForegroundColor White
Write-Host ""
Write-Host "  Or manually:" -ForegroundColor Cyan
Write-Host "    Backend:  cd backend && uvicorn app.main:app --reload --port 8000" -ForegroundColor White
Write-Host "    Frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "  For cloud training:" -ForegroundColor Cyan
Write-Host "    See cloud_training/README.md" -ForegroundColor White
Write-Host ""
