#!/usr/bin/env powershell
# Docker Export Script for CCD2 Project
# This script exports the Docker image to a .tar file for distribution

param(
    [string]$ImageName = "ccd2-app",
    [string]$Tag = "latest",
    [string]$OutputDir = ".",
    [string]$OutputFileName = ""
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

# Format file size
function Format-FileSize {
    param([long]$Size)
    
    if ($Size -gt 1GB) {
        return "{0:N2} GB" -f ($Size / 1GB)
    } elseif ($Size -gt 1MB) {
        return "{0:N2} MB" -f ($Size / 1MB)
    } elseif ($Size -gt 1KB) {
        return "{0:N2} KB" -f ($Size / 1KB)
    } else {
        return "$Size bytes"
    }
}

# Main script
Clear-Host
Write-Step "CCD2 Docker Image Exporter"

# Check if Docker is installed and running
Write-Info "Checking Docker installation..."
try {
    docker --version | Out-Null
    Write-Success "Docker is installed"
} catch {
    Write-Error "Docker is not installed or not in PATH"
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

# Construct full image name
$FullImageName = "${ImageName}:${Tag}"

# Check if image exists
Write-Info "Checking if image exists: $FullImageName"
try {
    $ImageExists = docker images -q $FullImageName
    if ([string]::IsNullOrEmpty($ImageExists)) {
        Write-Error "Image not found: $FullImageName"
        Write-Info "Please build the image first using: .\docker-build.ps1"
        exit 1
    }
    Write-Success "Image found: $FullImageName"
} catch {
    Write-Error "Failed to check image existence"
    exit 1
}

# Get image information
try {
    $ImageSize = docker images $FullImageName --format "{{.Size}}"
    Write-Info "Image size: $ImageSize"
} catch {
    Write-Info "Could not retrieve image size"
}

# Prepare output directory
if ($OutputDir -eq ".") {
    $OutputDir = $PSScriptRoot
}

$OutputDirPath = Resolve-Path $OutputDir -ErrorAction SilentlyContinue
if (-not $OutputDirPath) {
    Write-Info "Creating output directory: $OutputDir"
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    $OutputDirPath = Resolve-Path $OutputDir
}

Write-Success "Output directory: $OutputDirPath"

# Generate output filename if not provided
if ([string]::IsNullOrEmpty($OutputFileName)) {
    $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $OutputFileName = "ccd2-app-${Tag}-${Timestamp}.tar"
}

# Ensure .tar extension
if (-not $OutputFileName.EndsWith(".tar")) {
    $OutputFileName += ".tar"
}

$OutputFilePath = Join-Path $OutputDirPath $OutputFileName

# Check if output file already exists
if (Test-Path $OutputFilePath) {
    Write-Info "Output file already exists: $OutputFilePath"
    $Overwrite = Read-Host "Overwrite? (y/N)"
    if ($Overwrite -ne "y" -and $Overwrite -ne "Y") {
        Write-Info "Export cancelled"
        exit 0
    }
    Remove-Item $OutputFilePath -Force
}

# Export the image
Write-Step "Exporting Docker Image"
Write-Info "Image: $FullImageName"
Write-Info "Output: $OutputFilePath"
Write-ColorOutput "`nThis may take several minutes depending on image size..." "Yellow"

$ExportStartTime = Get-Date

try {
    Write-ColorOutput "`nExport progress:" "Cyan"
    Write-ColorOutput "----------------------------------------" "DarkGray"
    
    docker save -o $OutputFilePath $FullImageName
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker save failed with exit code $LASTEXITCODE"
    }
    
    Write-ColorOutput "----------------------------------------" "DarkGray"
} catch {
    Write-Error "Failed to export image: $_"
    if (Test-Path $OutputFilePath) {
        Remove-Item $OutputFilePath -Force
    }
    exit 1
}

$ExportEndTime = Get-Date
$ExportDuration = $ExportEndTime - $ExportStartTime

# Verify the exported file
if (-not (Test-Path $OutputFilePath)) {
    Write-Error "Export failed: Output file not created"
    exit 1
}

$FileInfo = Get-Item $OutputFilePath
$FormattedSize = Format-FileSize $FileInfo.Length

Write-Success "Image exported successfully!"
Write-Info "Export duration: $($ExportDuration.ToString('mm\:ss'))"

# Summary
Write-Step "Export Summary"
Write-ColorOutput "File: $($FileInfo.Name)" "White"
Write-ColorOutput "Path: $($FileInfo.FullName)" "White"
Write-ColorOutput "Size: $FormattedSize" "White"
Write-ColorOutput "Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "White"

# Calculate SHA256 hash for verification
Write-Info "`nCalculating SHA256 hash for verification..."
try {
    $Hash = Get-FileHash -Path $OutputFilePath -Algorithm SHA256
    Write-ColorOutput "SHA256: $($Hash.Hash)" "White"
    
    # Save hash to a file
    $HashFilePath = "$OutputFilePath.sha256"
    "$($Hash.Hash)  $($FileInfo.Name)" | Out-File -FilePath $HashFilePath -Encoding ASCII
    Write-Success "Hash saved to: $HashFilePath"
} catch {
    Write-Info "Could not calculate hash"
}

# Next steps
Write-ColorOutput "`n========================================" "Green"
Write-ColorOutput "Next Steps:" "Green"
Write-ColorOutput "========================================" "Green"
Write-ColorOutput "1. Transfer the file to another machine:" "White"
Write-ColorOutput "   $($FileInfo.Name)" "Yellow"
Write-ColorOutput "`n2. On the target machine, load the image:" "White"
Write-ColorOutput "   docker load -i $($FileInfo.Name)" "Yellow"
Write-ColorOutput "`n3. Run the container:" "White"
Write-ColorOutput "   docker run -d -p 80:80 --name ccd2 $FullImageName" "Yellow"
Write-ColorOutput "`n4. Access the application:" "White"
Write-ColorOutput "   http://localhost" "Yellow"
Write-ColorOutput "========================================`n" "Green"

