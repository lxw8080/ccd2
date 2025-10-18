# CCD2 Docker Images Export Script
# Export all required Docker images for deployment

Write-Host "=========================================="
Write-Host "CCD2 Docker Images Export Tool"
Write-Host "=========================================="
Write-Host ""

# Create export directory
$exportDir = "docker-images-export"
if (!(Test-Path $exportDir)) {
    New-Item -ItemType Directory -Path $exportDir | Out-Null
    Write-Host "[OK] Created export directory: $exportDir"
}

# Define images to export
$images = @(
    @{Name="ccd2-app"; Tag="latest"; File="ccd2-app-latest.tar"},
    @{Name="redis"; Tag="7-alpine"; File="redis-7-alpine.tar"}
)

Write-Host "Images to export:"
foreach ($img in $images) {
    Write-Host "  - $($img.Name):$($img.Tag) -> $($img.File)"
}
Write-Host ""

# Check and pull missing images
Write-Host "Checking images..."
foreach ($img in $images) {
    $imageName = "$($img.Name):$($img.Tag)"
    $exists = docker images -q $imageName
    
    if ($exists) {
        Write-Host "  [OK] $imageName exists"
    } else {
        Write-Host "  [PULL] $imageName not found, pulling..."
        docker pull $imageName
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [ERROR] Failed to pull $imageName"
            exit 1
        }
        Write-Host "  [OK] Pulled $imageName"
    }
}

Write-Host ""
Write-Host "Exporting images..."
Write-Host ""

# Export images
$totalSize = 0
foreach ($img in $images) {
    $imageName = "$($img.Name):$($img.Tag)"
    $outputFile = Join-Path $exportDir $img.File
    
    Write-Host "Exporting $imageName ..."
    Write-Host "  Output: $outputFile"
    
    docker save -o $outputFile $imageName
    
    if ($LASTEXITCODE -eq 0) {
        $fileInfo = Get-Item $outputFile
        $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
        $totalSize += $fileInfo.Length
        
        Write-Host "  [OK] Exported successfully - Size: $sizeMB MB"
        
        # Calculate SHA256
        Write-Host "  Calculating SHA256..."
        $hash = Get-FileHash -Algorithm SHA256 $outputFile
        $hashFile = "$outputFile.sha256"
        "$($hash.Hash)  $($img.File)" | Out-File -FilePath $hashFile -Encoding ASCII
        
        Write-Host "  [OK] SHA256: $($hash.Hash)"
    } else {
        Write-Host "  [ERROR] Export failed"
        exit 1
    }
    
    Write-Host ""
}

# Copy deployment files
Write-Host "Copying deployment files..."

$deployFiles = @(
    "docker-compose.production.yml",
    ".env.production.example",
    "deploy-on-server.sh"
)

foreach ($file in $deployFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $exportDir
        Write-Host "  [OK] Copied: $file"
    } else {
        Write-Host "  [WARN] File not found: $file"
    }
}

Write-Host ""
Write-Host "[OK] Created README.md"

Write-Host ""
Write-Host "=========================================="
Write-Host "Export Completed Successfully!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Export Directory: $exportDir"
Write-Host "Total Size: $([math]::Round($totalSize / 1MB, 2)) MB"
Write-Host ""
Write-Host "Exported Images:"
foreach ($img in $images) {
    Write-Host "  [OK] $($img.Name):$($img.Tag)"
}
Write-Host ""
Write-Host "Next Steps:"
Write-Host "  1. Transfer '$exportDir' directory to Ubuntu server"
Write-Host "  2. Run deploy-on-server.sh on the server"
Write-Host "  3. Configure .env.production file"
Write-Host "  4. Access application at http://server-ip:8080"
Write-Host ""

