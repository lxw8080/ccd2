# Stop CCD2 Services Script
# This script stops all running backend and frontend services

Write-Host "Stopping CCD2 Services..." -ForegroundColor Yellow
Write-Host ""

# Stop processes on port 8000 (Backend)
Write-Host "[INFO] Checking port 8000 (Backend)..." -ForegroundColor Cyan
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    $processId = $port8000.OwningProcess
    Write-Host "[INFO] Found process $processId on port 8000" -ForegroundColor Yellow
    try {
        Stop-Process -Id $processId -Force -ErrorAction Stop
        Write-Host "[SUCCESS] Stopped process $processId" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Could not stop process $processId" -ForegroundColor Red
    }
} else {
    Write-Host "[INFO] Port 8000 is free" -ForegroundColor Green
}

# Stop processes on port 5173 (Frontend)
Write-Host "[INFO] Checking port 5173 (Frontend)..." -ForegroundColor Cyan
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($port5173) {
    $processId = $port5173.OwningProcess
    Write-Host "[INFO] Found process $processId on port 5173" -ForegroundColor Yellow
    try {
        Stop-Process -Id $processId -Force -ErrorAction Stop
        Write-Host "[SUCCESS] Stopped process $processId" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Could not stop process $processId" -ForegroundColor Red
    }
} else {
    Write-Host "[INFO] Port 5173 is free" -ForegroundColor Green
}

# Wait a moment for ports to be released
Start-Sleep -Seconds 2

# Verify ports are free
Write-Host ""
Write-Host "Verifying ports..." -ForegroundColor Cyan
$port8000Check = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port5173Check = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue

if (-not $port8000Check -and -not $port5173Check) {
    Write-Host "[SUCCESS] All ports are now free!" -ForegroundColor Green
} else {
    if ($port8000Check) {
        Write-Host "[WARNING] Port 8000 is still in use by process $($port8000Check.OwningProcess)" -ForegroundColor Red
    }
    if ($port5173Check) {
        Write-Host "[WARNING] Port 5173 is still in use by process $($port5173Check.OwningProcess)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

