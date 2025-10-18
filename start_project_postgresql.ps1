#!/usr/bin/env powershell
# -*- coding: utf-8 -*-

Write-Host "Starting CCD2 Project with PostgreSQL..." -ForegroundColor Green

# Backend setup and start
Write-Host "`n[1/3] Installing backend dependencies..." -ForegroundColor Cyan
$backendPath = "C:\Users\16094\Desktop\项目\ccd2\backend"
Set-Location $backendPath

Write-Host "Installing Python packages..." -ForegroundColor Yellow
pip install -q --upgrade pip
pip install -q -r requirements.txt

Write-Host "`n[2/3] Starting FastAPI backend..." -ForegroundColor Cyan
Write-Host "Backend will run on http://localhost:8000" -ForegroundColor Magenta
Start-Process python -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -NoNewWindow

# Wait for backend to start
Start-Sleep -Seconds 5

# Frontend setup and start
Write-Host "`n[3/3] Installing and starting frontend..." -ForegroundColor Cyan
$frontendPath = "C:\Users\16094\Desktop\项目\ccd2\frontend"
Set-Location $frontendPath

if (Test-Path "node_modules") {
    Write-Host "Node modules already installed" -ForegroundColor Green
} else {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install --quiet
}

Write-Host "`nStarting Vite dev server..." -ForegroundColor Yellow
Write-Host "Frontend will run on http://localhost:5173" -ForegroundColor Magenta
npm run dev

Write-Host "`n✅ CCD2 Project started successfully!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan





