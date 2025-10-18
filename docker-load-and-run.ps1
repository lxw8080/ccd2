#!/usr/bin/env powershell
# Docker Load and Run Script for CCD2 Project
# This script loads a Docker image from a .tar file and runs it

param(
    [Parameter(Mandatory=$false)]
    [string]$TarFile = "",
    [string]$ContainerName = "ccd2",
    [int]$Port = 80,
    [string]$DatabaseUrl = "",
    [string]$RedisUrl = "",
    [switch]$Help = $false
)

# Color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "`n========================================" "Cyan"
    Write-ColorOutput $Message "Cyan"
    Write-ColorOutput "========================================" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" "Yellow"
}

function Show-Help {
    Write-ColorOutput "`nCCD2 Docker Load and Run Script" "Cyan"
    Write-ColorOutput "================================`n" "Cyan"
    Write-ColorOutput "Usage:" "White"
    Write-ColorOutput "  .\docker-load-and-run.ps1 -TarFile <path-to-tar-file> [options]`n" "Yellow"
    Write-ColorOutput "Parameters:" "White"
    Write-ColorOutput "  -TarFile <path>        Path to the .tar file (required)" "Gray"
    Write-ColorOutput "  -ContainerName <name>  Container name (default: ccd2)" "Gray"
    Write-ColorOutput "  -Port <number>         Host port to bind (default: 80)" "Gray"
    Write-ColorOutput "  -DatabaseUrl <url>     PostgreSQL database URL" "Gray"
    Write-ColorOutput "  -RedisUrl <url>        Redis URL" "Gray"
    Write-ColorOutput "  -Help                  Show this help message`n" "Gray"
    Write-ColorOutput "Examples:" "White"
    Write-ColorOutput "  .\docker-load-and-run.ps1 -TarFile ccd2-app-latest.tar" "Yellow"
    Write-ColorOutput "  .\docker-load-and-run.ps1 -TarFile ccd2-app.tar -Port 8080" "Yellow"
    Write-ColorOutput "  .\docker-load-and-run.ps1 -TarFile ccd2-app.tar -DatabaseUrl 'postgresql://user:pass@host:5432/db'`n" "Yellow"
}

# Show help if requested
if ($Help) {
    Show-Help
    exit 0
}

# Main script
Clear-Host
Write-Step "CCD2 Docker Load and Run"

# Check if Docker is installed and running
Write-Info "Checking Docker installation..."
try {
    docker --version | Out-Null
    Write-Success "Docker is installed"
} catch {
    Write-Error "Docker is not installed or not in PATH"
    Write-Info "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check if Docker daemon is running
Write-Info "Checking Docker daemon..."
try {
    docker ps | Out-Null
    Write-Success "Docker daemon is running"
} catch {
    Write-Error "Docker daemon is not running"
    Write-Info "Please start Docker Desktop and try again"
    exit 1
}

# Find .tar file if not specified
if ([string]::IsNullOrEmpty($TarFile)) {
    Write-Info "No tar file specified, searching in current directory..."
    $TarFiles = Get-ChildItem -Path $PSScriptRoot -Filter "ccd2-app*.tar" | Sort-Object LastWriteTime -Descending
    
    if ($TarFiles.Count -eq 0) {
        Write-Error "No .tar files found in current directory"
        Write-Info "Please specify the tar file using -TarFile parameter"
        Show-Help
        exit 1
    }
    
    if ($TarFiles.Count -eq 1) {
        $TarFile = $TarFiles[0].FullName
        Write-Success "Found tar file: $($TarFiles[0].Name)"
    } else {
        Write-Info "Multiple tar files found:"
        for ($i = 0; $i -lt $TarFiles.Count; $i++) {
            Write-ColorOutput "  [$i] $($TarFiles[$i].Name) - $(Get-Date $TarFiles[$i].LastWriteTime -Format 'yyyy-MM-dd HH:mm:ss')" "White"
        }
        $Selection = Read-Host "`nSelect file number (0-$($TarFiles.Count - 1))"
        try {
            $Index = [int]$Selection
            if ($Index -ge 0 -and $Index -lt $TarFiles.Count) {
                $TarFile = $TarFiles[$Index].FullName
                Write-Success "Selected: $($TarFiles[$Index].Name)"
            } else {
                Write-Error "Invalid selection"
                exit 1
            }
        } catch {
            Write-Error "Invalid input"
            exit 1
        }
    }
}

# Verify tar file exists
if (-not (Test-Path $TarFile)) {
    Write-Error "Tar file not found: $TarFile"
    exit 1
}

$TarFileInfo = Get-Item $TarFile
Write-Success "Tar file: $($TarFileInfo.FullName)"
Write-Info "File size: $([math]::Round($TarFileInfo.Length / 1MB, 2)) MB"

# Verify hash if available
$HashFile = "$TarFile.sha256"
if (Test-Path $HashFile) {
    Write-Info "Verifying file integrity..."
    try {
        $ExpectedHash = (Get-Content $HashFile).Split()[0]
        $ActualHash = (Get-FileHash -Path $TarFile -Algorithm SHA256).Hash
        
        if ($ExpectedHash -eq $ActualHash) {
            Write-Success "File integrity verified (SHA256 match)"
        } else {
            Write-Error "File integrity check failed (SHA256 mismatch)"
            Write-Info "Expected: $ExpectedHash"
            Write-Info "Actual:   $ActualHash"
            $Continue = Read-Host "Continue anyway? (y/N)"
            if ($Continue -ne "y" -and $Continue -ne "Y") {
                exit 1
            }
        }
    } catch {
        Write-Info "Could not verify hash: $_"
    }
}

# Load the Docker image
Write-Step "Loading Docker Image"
Write-Info "This may take several minutes..."

$LoadStartTime = Get-Date

try {
    Write-ColorOutput "`nLoad progress:" "Cyan"
    Write-ColorOutput "----------------------------------------" "DarkGray"
    
    $LoadOutput = docker load -i $TarFile 2>&1
    Write-ColorOutput $LoadOutput "White"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker load failed with exit code $LASTEXITCODE"
    }
    
    Write-ColorOutput "----------------------------------------" "DarkGray"
} catch {
    Write-Error "Failed to load image: $_"
    exit 1
}

$LoadEndTime = Get-Date
$LoadDuration = $LoadEndTime - $LoadStartTime

Write-Success "Image loaded successfully!"
Write-Info "Load duration: $($LoadDuration.ToString('mm\:ss'))"

# Extract image name from load output
$ImageName = "ccd2-app:latest"
if ($LoadOutput -match "Loaded image: (.+)") {
    $ImageName = $Matches[1].Trim()
    Write-Info "Loaded image: $ImageName"
}

# Check if container with same name already exists
Write-Info "Checking for existing container: $ContainerName"
$ExistingContainer = docker ps -a -q -f name=^${ContainerName}$

if ($ExistingContainer) {
    Write-Info "Container '$ContainerName' already exists"
    $Action = Read-Host "Action: (r)emove and recreate, (s)top existing, (c)ancel? (r/s/c)"
    
    switch ($Action.ToLower()) {
        "r" {
            Write-Info "Removing existing container..."
            docker rm -f $ContainerName | Out-Null
            Write-Success "Container removed"
        }
        "s" {
            Write-Info "Stopping existing container..."
            docker stop $ContainerName | Out-Null
            Write-Success "Container stopped"
            Write-Info "Use 'docker start $ContainerName' to start it again"
            exit 0
        }
        default {
            Write-Info "Operation cancelled"
            exit 0
        }
    }
}

# Prepare environment variables
$EnvVars = @()

if (-not [string]::IsNullOrEmpty($DatabaseUrl)) {
    $EnvVars += "-e", "DATABASE_URL=$DatabaseUrl"
    Write-Info "Using custom database URL"
} else {
    Write-Info "Using default database URL (you may need to configure this)"
}

if (-not [string]::IsNullOrEmpty($RedisUrl)) {
    $EnvVars += "-e", "REDIS_URL=$RedisUrl"
    Write-Info "Using custom Redis URL"
}

# Run the container
Write-Step "Starting Container"
Write-Info "Container name: $ContainerName"
Write-Info "Port mapping: ${Port}:80"

try {
    $RunArgs = @(
        "run",
        "-d",
        "-p", "${Port}:80",
        "--name", $ContainerName,
        "--restart", "unless-stopped"
    )
    
    $RunArgs += $EnvVars
    $RunArgs += $ImageName
    
    $ContainerId = docker @RunArgs
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker run failed with exit code $LASTEXITCODE"
    }
    
    Write-Success "Container started successfully!"
    Write-Info "Container ID: $($ContainerId.Substring(0, 12))"
} catch {
    Write-Error "Failed to start container: $_"
    exit 1
}

# Wait for container to be healthy
Write-Info "`nWaiting for container to be ready..."
Start-Sleep -Seconds 5

$MaxWait = 60
$Waited = 0
$Healthy = $false

while ($Waited -lt $MaxWait) {
    try {
        $Response = Invoke-WebRequest -Uri "http://localhost:${Port}/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($Response.StatusCode -eq 200) {
            $Healthy = $true
            break
        }
    } catch {
        # Continue waiting
    }
    
    Start-Sleep -Seconds 2
    $Waited += 2
    Write-Host "." -NoNewline
}

Write-Host ""

if ($Healthy) {
    Write-Success "Container is healthy and ready!"
} else {
    Write-Info "Container started but health check timed out"
    Write-Info "Check logs with: docker logs $ContainerName"
}

# Summary
Write-Step "Deployment Summary"
Write-ColorOutput "Container Name: $ContainerName" "White"
Write-ColorOutput "Image: $ImageName" "White"
Write-ColorOutput "Status: Running" "Green"

Write-ColorOutput "`n========================================" "Green"
Write-ColorOutput "Access the Application:" "Green"
Write-ColorOutput "========================================" "Green"
Write-ColorOutput "Frontend:  http://localhost:${Port}" "Yellow"
Write-ColorOutput "API Docs:  http://localhost:${Port}/docs" "Yellow"
Write-ColorOutput "Health:    http://localhost:${Port}/api/health" "Yellow"

Write-ColorOutput "`n========================================" "Green"
Write-ColorOutput "Useful Commands:" "Green"
Write-ColorOutput "========================================" "Green"
Write-ColorOutput "View logs:        docker logs -f $ContainerName" "White"
Write-ColorOutput "Stop container:   docker stop $ContainerName" "White"
Write-ColorOutput "Start container:  docker start $ContainerName" "White"
Write-ColorOutput "Remove container: docker rm -f $ContainerName" "White"
Write-ColorOutput "Container stats:  docker stats $ContainerName" "White"
Write-ColorOutput "========================================`n" "Green"

