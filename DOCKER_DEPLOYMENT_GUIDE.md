# CCD2 Docker Deployment Guide

This guide provides comprehensive instructions for containerizing, exporting, and deploying the CCD2 (Customer Collection Data) application using Docker.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Instructions](#detailed-instructions)
  - [1. Building the Docker Image](#1-building-the-docker-image)
  - [2. Exporting the Image](#2-exporting-the-image)
  - [3. Loading and Running on Another Machine](#3-loading-and-running-on-another-machine)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## Overview

The CCD2 application is a full-stack customer data collection system consisting of:

- **Frontend**: React + TypeScript + Vite + Ant Design
- **Backend**: FastAPI (Python) with PostgreSQL and Redis
- **Architecture**: Multi-stage Docker build with Nginx reverse proxy

The Docker image packages both frontend and backend into a single container for easy deployment.

---

## Prerequisites

### On Build Machine (where you build the image)

- **Docker Desktop** installed and running
  - Download from: https://www.docker.com/products/docker-desktop
  - Minimum version: Docker 20.10+
- **PowerShell** (included with Windows)
- **Disk Space**: At least 5GB free space for building and exporting

### On Target Machine (where you deploy the image)

- **Docker Desktop** or **Docker Engine** installed and running
- **PowerShell** (for Windows) or **Bash** (for Linux/Mac)
- **Disk Space**: At least 3GB free space for the image
- **Network**: Access to required databases (PostgreSQL, Redis) if using external services

---

## Quick Start

### On Build Machine

```powershell
# 1. Build the Docker image
.\docker-build.ps1

# 2. Export the image to a .tar file
.\docker-export.ps1

# 3. Transfer the generated .tar file to target machine
# File will be named: ccd2-app-latest-YYYYMMDD-HHMMSS.tar
```

### On Target Machine

```powershell
# 1. Load and run the image
.\docker-load-and-run.ps1 -TarFile ccd2-app-latest-YYYYMMDD-HHMMSS.tar

# 2. Access the application
# Open browser: http://localhost
```

---

## Detailed Instructions

### 1. Building the Docker Image

The build process uses a multi-stage Dockerfile to create an optimized production image.

#### Using the Build Script (Recommended)

```powershell
# Basic build
.\docker-build.ps1

# Build with custom image name and tag
.\docker-build.ps1 -ImageName "my-ccd2" -Tag "v1.0"

# Build without cache (clean build)
.\docker-build.ps1 -NoCache
```

#### Manual Build

```powershell
docker build -t ccd2-app:latest -f Dockerfile .
```

#### What Happens During Build

1. **Stage 1 - Frontend Build**
   - Uses Node.js 18 Alpine image
   - Installs npm dependencies
   - Builds React application for production
   - Output: Optimized static files in `/dist`

2. **Stage 2 - Backend Base**
   - Uses Python 3.11 Slim image
   - Installs system dependencies (PostgreSQL client, libmagic, etc.)
   - Installs Python packages from requirements.txt

3. **Stage 3 - Production Image**
   - Combines frontend and backend
   - Installs Nginx as reverse proxy
   - Configures Supervisor to manage processes
   - Sets up health checks
   - Final image size: ~800MB-1.2GB

#### Build Time

- First build: 10-20 minutes (depending on internet speed)
- Subsequent builds: 2-5 minutes (with Docker cache)

---

### 2. Exporting the Image

Export the built image to a `.tar` file for transfer to other machines.

#### Using the Export Script (Recommended)

```powershell
# Basic export (auto-generates filename with timestamp)
.\docker-export.ps1

# Export with custom filename
.\docker-export.ps1 -OutputFileName "ccd2-production.tar"

# Export to specific directory
.\docker-export.ps1 -OutputDir "C:\Docker\Images"

# Export specific image version
.\docker-export.ps1 -ImageName "ccd2-app" -Tag "v1.0"
```

#### Manual Export

```powershell
docker save -o ccd2-app-latest.tar ccd2-app:latest
```

#### Export Output

The script creates:
- **TAR file**: The Docker image archive (typically 800MB-1.2GB)
- **SHA256 file**: Hash file for integrity verification (e.g., `ccd2-app-latest.tar.sha256`)

#### Transferring the File

Transfer both files to the target machine using:
- USB drive
- Network share
- SCP/SFTP
- Cloud storage (OneDrive, Google Drive, etc.)

**Example using SCP:**
```powershell
scp ccd2-app-latest.tar* user@target-machine:/path/to/destination/
```

---

### 3. Loading and Running on Another Machine

#### Using the Load and Run Script (Recommended)

```powershell
# Auto-detect and load the tar file
.\docker-load-and-run.ps1

# Specify tar file explicitly
.\docker-load-and-run.ps1 -TarFile "ccd2-app-latest-20251018-143022.tar"

# Run on custom port
.\docker-load-and-run.ps1 -TarFile "ccd2-app.tar" -Port 8080

# Run with custom database
.\docker-load-and-run.ps1 -TarFile "ccd2-app.tar" `
    -DatabaseUrl "postgresql://user:pass@db-server:5432/ccd_db" `
    -RedisUrl "redis://redis-server:6379/0"

# Show help
.\docker-load-and-run.ps1 -Help
```

#### Manual Load and Run

```powershell
# 1. Load the image
docker load -i ccd2-app-latest.tar

# 2. Run the container
docker run -d `
    -p 80:80 `
    --name ccd2 `
    --restart unless-stopped `
    ccd2-app:latest

# 3. Check status
docker ps

# 4. View logs
docker logs -f ccd2
```

#### Accessing the Application

Once the container is running:

- **Frontend**: http://localhost (or http://localhost:PORT if custom port)
- **API Documentation**: http://localhost/docs
- **Health Check**: http://localhost/api/health

#### Default Credentials

Check your backend configuration for default admin credentials. Typically:
- Username: `admin`
- Password: (configured in your database initialization)

---

## Configuration

### Environment Variables

The Docker image supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://ccd_user:ccd_password@localhost:5432/ccd_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `STORAGE_TYPE` | File storage type (local/oss/minio) | `local` |
| `UPLOAD_DIR` | Upload directory path | `/app/uploads` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Setting Environment Variables

#### At Runtime

```powershell
docker run -d `
    -p 80:80 `
    --name ccd2 `
    -e DATABASE_URL="postgresql://user:pass@host:5432/db" `
    -e REDIS_URL="redis://host:6379/0" `
    -e SECRET_KEY="your-super-secret-key-here" `
    ccd2-app:latest
```

#### Using Environment File

Create a file named `ccd2.env`:

```env
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
LOG_LEVEL=DEBUG
```

Run with environment file:

```powershell
docker run -d `
    -p 80:80 `
    --name ccd2 `
    --env-file ccd2.env `
    ccd2-app:latest
```

### Persistent Data

To persist uploaded files and logs:

```powershell
docker run -d `
    -p 80:80 `
    --name ccd2 `
    -v ccd2-uploads:/app/uploads `
    -v ccd2-logs:/app/logs `
    ccd2-app:latest
```

---

## Troubleshooting

### Build Issues

#### Problem: Build fails with "npm install" errors

**Solution:**
```powershell
# Try building without cache
.\docker-build.ps1 -NoCache

# Or manually clear Docker cache
docker builder prune -a
```

#### Problem: Build fails with Python dependency errors

**Solution:**
Check that `backend/requirements.txt` is present and properly formatted.

### Export Issues

#### Problem: "Image not found" error

**Solution:**
```powershell
# List available images
docker images

# Build the image first
.\docker-build.ps1
```

#### Problem: Export fails with "no space left on device"

**Solution:**
- Free up disk space
- Clean up unused Docker resources:
  ```powershell
  docker system prune -a
  ```

### Runtime Issues

#### Problem: Container starts but application is not accessible

**Solution:**
```powershell
# Check container status
docker ps -a

# View logs
docker logs ccd2

# Check if port is already in use
netstat -ano | findstr :80

# Try running on different port
.\docker-load-and-run.ps1 -Port 8080
```

#### Problem: Database connection errors

**Solution:**
- Ensure PostgreSQL is accessible from the container
- Check DATABASE_URL is correct
- Verify network connectivity:
  ```powershell
  docker exec ccd2 ping your-db-host
  ```

#### Problem: Container exits immediately

**Solution:**
```powershell
# View container logs
docker logs ccd2

# Run in interactive mode for debugging
docker run -it --rm ccd2-app:latest /bin/bash
```

### Health Check Failures

```powershell
# Check health status
docker inspect ccd2 | Select-String -Pattern "Health"

# Manual health check
Invoke-WebRequest -Uri "http://localhost/api/health"

# View supervisor logs
docker exec ccd2 cat /var/log/supervisor/supervisord.log
docker exec ccd2 cat /var/log/supervisor/backend.log
docker exec ccd2 cat /var/log/supervisor/nginx.log
```

---

## Advanced Usage

### Using Docker Compose

For easier management with external services, create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ccd_user
      POSTGRES_PASSWORD: ccd_password
      POSTGRES_DB: ccd_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  ccd2:
    image: ccd2-app:latest
    ports:
      - "80:80"
    environment:
      DATABASE_URL: postgresql://ccd_user:ccd_password@postgres:5432/ccd_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: your-production-secret-key
    volumes:
      - uploads:/app/uploads
      - logs:/app/logs
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
  uploads:
  logs:
```

Run with:
```powershell
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling and Load Balancing

Run multiple instances behind a load balancer:

```powershell
# Run multiple instances
docker run -d -p 8001:80 --name ccd2-1 ccd2-app:latest
docker run -d -p 8002:80 --name ccd2-2 ccd2-app:latest
docker run -d -p 8003:80 --name ccd2-3 ccd2-app:latest
```

### Monitoring

```powershell
# View resource usage
docker stats ccd2

# View real-time logs
docker logs -f ccd2

# Execute commands in container
docker exec -it ccd2 /bin/bash

# View running processes
docker exec ccd2 ps aux
```

### Backup and Restore

#### Backup

```powershell
# Backup uploads
docker cp ccd2:/app/uploads ./backup/uploads

# Backup database (if using containerized PostgreSQL)
docker exec postgres pg_dump -U ccd_user ccd_db > backup/database.sql
```

#### Restore

```powershell
# Restore uploads
docker cp ./backup/uploads ccd2:/app/uploads

# Restore database
docker exec -i postgres psql -U ccd_user ccd_db < backup/database.sql
```

### Updating the Application

```powershell
# 1. Build new version
.\docker-build.ps1 -Tag "v2.0"

# 2. Export new version
.\docker-export.ps1 -Tag "v2.0"

# 3. On target machine, stop old container
docker stop ccd2
docker rm ccd2

# 4. Load and run new version
.\docker-load-and-run.ps1 -TarFile "ccd2-app-v2.0.tar"
```

---

## Security Considerations

1. **Change Default Secrets**: Always change `SECRET_KEY` in production
2. **Use HTTPS**: Deploy behind a reverse proxy with SSL/TLS
3. **Network Isolation**: Use Docker networks to isolate services
4. **Regular Updates**: Keep base images and dependencies updated
5. **Scan for Vulnerabilities**: Use `docker scan ccd2-app:latest`

---

## Performance Optimization

1. **Resource Limits**:
   ```powershell
   docker run -d `
       -p 80:80 `
       --name ccd2 `
       --memory="2g" `
       --cpus="2" `
       ccd2-app:latest
   ```

2. **Use Production Database**: Don't use SQLite in production
3. **Enable Redis Caching**: Configure Redis for session and data caching
4. **CDN for Static Assets**: Serve frontend assets through CDN

---

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Docker logs: `docker logs ccd2`
- Check application logs in `/app/logs`
- Verify configuration with: `docker exec ccd2 env`

---

## License

This deployment guide is part of the CCD2 project.

