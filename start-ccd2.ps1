# CCD2 Project Quick Start Script (PowerShell)
# Start both backend and frontend services

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-ColorOutput "============================================================" "Cyan"
    Write-ColorOutput "  $Text" "Cyan"
    Write-ColorOutput "============================================================" "Cyan"
    Write-Host ""
}

$ProjectRoot = $PSScriptRoot
$BackendPath = Join-Path $ProjectRoot "backend"
$FrontendPath = Join-Path $ProjectRoot "frontend"

Clear-Host
Write-Header "CCD2 Customer Collection System - Quick Start"
Write-ColorOutput "Project Path: $ProjectRoot" "Gray"
Write-Host ""

Write-ColorOutput "`n[STEP] Checking prerequisites..." "Magenta"

# Check Python
Write-ColorOutput "[INFO] Checking Python..." "Yellow"
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "[OK] Python installed: $pythonVersion" "Green"
    } else {
        throw "Python not found"
    }
} catch {
    Write-ColorOutput "[ERROR] Python not detected!" "Red"
    Write-ColorOutput "Please install Python 3.8+: https://www.python.org/downloads/" "Yellow"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
Write-ColorOutput "[INFO] Checking Node.js..." "Yellow"
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "[OK] Node.js installed: $nodeVersion" "Green"
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-ColorOutput "[ERROR] Node.js not detected!" "Red"
    Write-ColorOutput "Please install Node.js 16+: https://nodejs.org/" "Yellow"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check npm
Write-ColorOutput "[INFO] Checking npm..." "Yellow"
try {
    $npmVersion = npm --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "[OK] npm installed: $npmVersion" "Green"
    } else {
        throw "npm not found"
    }
} catch {
    Write-ColorOutput "[ERROR] npm not detected!" "Red"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check .env
Write-ColorOutput "[INFO] Checking configuration..." "Yellow"
$envFile = Join-Path $BackendPath ".env"
if (Test-Path $envFile) {
    Write-ColorOutput "[OK] Configuration file exists" "Green"
} else {
    Write-ColorOutput "[ERROR] backend\.env not found!" "Red"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-ColorOutput "`n[STEP] Installing backend dependencies..." "Magenta"
Push-Location $BackendPath
python -m pip install --quiet -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput "[OK] Backend dependencies installed" "Green"
} else {
    Write-ColorOutput "[ERROR] Failed to install dependencies" "Red"
    Pop-Location
    Read-Host "Press Enter to exit"
    exit 1
}
Pop-Location

Write-ColorOutput "`n[STEP] Checking frontend dependencies..." "Magenta"
$nodeModules = Join-Path $FrontendPath "node_modules"
if (Test-Path $nodeModules) {
    Write-ColorOutput "[OK] npm dependencies exist" "Green"
} else {
    Write-ColorOutput "[INFO] Installing npm dependencies..." "Yellow"
    Push-Location $FrontendPath
    npm install
    Pop-Location
}

Write-ColorOutput "`n[STEP] Starting backend service..." "Magenta"
$backendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} -ArgumentList $BackendPath

Start-Sleep -Seconds 3

if ($backendJob.State -eq "Running") {
    Write-ColorOutput "[OK] Backend started" "Green"
} else {
    Write-ColorOutput "[ERROR] Backend failed to start" "Red"
    Stop-Job $backendJob
    Remove-Job $backendJob
    exit 1
}

Write-ColorOutput "`n[STEP] Starting frontend service..." "Magenta"
Write-Host ""
Write-Header "Services Started"
Write-ColorOutput "Frontend:  http://localhost:5173" "Green"
Write-ColorOutput "Backend:   http://localhost:8000" "Green"
Write-ColorOutput "API Docs:  http://localhost:8000/docs" "Green"
Write-Host ""
Write-ColorOutput "Press Ctrl+C to stop all services" "Yellow"
Write-Host ""

Push-Location $FrontendPath
try {
    npm run dev
} finally {
    Pop-Location
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Write-ColorOutput "`nAll services stopped" "Green"
}
