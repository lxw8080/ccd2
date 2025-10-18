#!/usr/bin/env powershell
# Docker Build Script for CCD2 Project
# This script builds the Docker image for the CCD2 application

param(
    [string]$ImageName = "ccd2-app",
    [string]$Tag = "latest",
    [switch]$NoCache = $false
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

# Main script
Clear-Host
Write-Step "CCD2 Docker Image Builder"

# Check if Docker is installed and running
Write-Info "Checking Docker installation..."
try {
    $dockerVersion = docker --version
    Write-Success "Docker is installed: $dockerVersion"
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

# Get project root directory
$ProjectRoot = $PSScriptRoot
Write-Info "Project root: $ProjectRoot"

# Check if Dockerfile exists
$DockerfilePath = Join-Path $ProjectRoot "Dockerfile"
if (-not (Test-Path $DockerfilePath)) {
    Write-Error "Dockerfile not found at: $DockerfilePath"
    exit 1
}
Write-Success "Dockerfile found"

# Check if required directories exist
$RequiredDirs = @("backend", "frontend")
foreach ($dir in $RequiredDirs) {
    $dirPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $dirPath)) {
        Write-Error "Required directory not found: $dir"
        exit 1
    }
}
Write-Success "All required directories found"

# Build the Docker image
Write-Step "Building Docker Image"
$FullImageName = "${ImageName}:${Tag}"
Write-Info "Image name: $FullImageName"
Write-Info "Build context: $ProjectRoot"

if ($NoCache) {
    Write-Info "Building with --no-cache flag (this will take longer)"
}

$BuildArgs = @(
    "build",
    "-t", $FullImageName,
    "-f", $DockerfilePath
)

if ($NoCache) {
    $BuildArgs += "--no-cache"
}

$BuildArgs += $ProjectRoot

Write-Info "Running: docker $($BuildArgs -join ' ')"
Write-ColorOutput "`nBuild output:" "Cyan"
Write-ColorOutput "----------------------------------------" "DarkGray"

$BuildStartTime = Get-Date

try {
    & docker $BuildArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Docker build failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-ColorOutput "----------------------------------------" "DarkGray"
    Write-Error "Docker build failed: $_"
    exit 1
}

$BuildEndTime = Get-Date
$BuildDuration = $BuildEndTime - $BuildStartTime

Write-ColorOutput "----------------------------------------" "DarkGray"
Write-Success "Docker image built successfully!"
Write-Info "Build duration: $($BuildDuration.ToString('mm\:ss'))"

# Get image information
Write-Step "Image Information"
try {
    $ImageInfo = docker images $FullImageName --format "{{.Repository}}:{{.Tag}} | Size: {{.Size}} | Created: {{.CreatedSince}}"
    Write-ColorOutput $ImageInfo "White"
} catch {
    Write-Info "Could not retrieve image information"
}

# Summary
Write-Step "Build Summary"
Write-Success "Image name: $FullImageName"
Write-Success "Build completed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

Write-ColorOutput "`n========================================" "Green"
Write-ColorOutput "Next Steps:" "Green"
Write-ColorOutput "========================================" "Green"
Write-ColorOutput "1. Export image to file:" "White"
Write-ColorOutput "   .\docker-export.ps1 -ImageName $ImageName -Tag $Tag" "Yellow"
Write-ColorOutput "`n2. Run the image locally:" "White"
Write-ColorOutput "   docker run -d -p 80:80 --name ccd2 $FullImageName" "Yellow"
Write-ColorOutput "`n3. View running containers:" "White"
Write-ColorOutput "   docker ps" "Yellow"
Write-ColorOutput "`n4. View logs:" "White"
Write-ColorOutput "   docker logs -f ccd2" "Yellow"
Write-ColorOutput "`n5. Stop the container:" "White"
Write-ColorOutput "   docker stop ccd2 && docker rm ccd2" "Yellow"
Write-ColorOutput "========================================`n" "Green"

