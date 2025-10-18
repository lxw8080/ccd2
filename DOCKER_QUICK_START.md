# CCD2 Docker Quick Start Guide

## 🚀 Quick Commands

### On Build Machine (Create Docker Image)

```powershell
# Step 1: Build the Docker image
.\docker-build.ps1

# Step 2: Export to .tar file
.\docker-export.ps1

# Step 3: Transfer the .tar file to target machine
# File location: ccd2-app-latest-YYYYMMDD-HHMMSS.tar
```

### On Target Machine (Deploy Docker Image)

```powershell
# Step 1: Load and run the image
.\docker-load-and-run.ps1 -TarFile ccd2-app-latest-YYYYMMDD-HHMMSS.tar

# Step 2: Access the application
# Open browser: http://localhost
```

---

## 📋 Prerequisites

- ✅ Docker Desktop installed and running
- ✅ PowerShell (Windows)
- ✅ 5GB free disk space (build machine)
- ✅ 3GB free disk space (target machine)

---

## 🔧 Common Commands

### Container Management

```powershell
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker logs -f ccd2

# Stop container
docker stop ccd2

# Start container
docker start ccd2

# Restart container
docker restart ccd2

# Remove container
docker rm -f ccd2
```

### Image Management

```powershell
# List images
docker images

# Remove image
docker rmi ccd2-app:latest

# View image details
docker inspect ccd2-app:latest
```

### Troubleshooting

```powershell
# Check container health
docker inspect ccd2 | Select-String -Pattern "Health"

# Execute command in container
docker exec -it ccd2 /bin/bash

# View resource usage
docker stats ccd2

# View container processes
docker exec ccd2 ps aux
```

---

## 🌐 Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| API Docs | http://localhost/docs |
| Health Check | http://localhost/api/health |

---

## ⚙️ Custom Configuration

### Run on Different Port

```powershell
.\docker-load-and-run.ps1 -TarFile ccd2-app.tar -Port 8080
# Access: http://localhost:8080
```

### Use External Database

```powershell
.\docker-load-and-run.ps1 -TarFile ccd2-app.tar `
    -DatabaseUrl "postgresql://user:pass@db-host:5432/ccd_db" `
    -RedisUrl "redis://redis-host:6379/0"
```

### Persist Data

```powershell
docker run -d `
    -p 80:80 `
    --name ccd2 `
    -v ccd2-uploads:/app/uploads `
    -v ccd2-logs:/app/logs `
    ccd2-app:latest
```

---

## 🆘 Quick Troubleshooting

### Container won't start?

```powershell
# Check logs
docker logs ccd2

# Check if port is in use
netstat -ano | findstr :80

# Try different port
.\docker-load-and-run.ps1 -Port 8080
```

### Can't access the application?

```powershell
# Check container status
docker ps

# Check health
Invoke-WebRequest -Uri "http://localhost/api/health"

# View nginx logs
docker exec ccd2 cat /var/log/supervisor/nginx.log
```

### Database connection errors?

```powershell
# Check environment variables
docker exec ccd2 env | Select-String -Pattern "DATABASE"

# Test database connectivity
docker exec ccd2 pg_isready -h your-db-host -p 5432
```

---

## 📚 Full Documentation

For detailed instructions, see: **DOCKER_DEPLOYMENT_GUIDE.md**

---

## 🔄 Update Workflow

```powershell
# 1. Build new version
.\docker-build.ps1 -Tag "v2.0"

# 2. Export new version
.\docker-export.ps1 -Tag "v2.0"

# 3. On target machine
docker stop ccd2
docker rm ccd2
.\docker-load-and-run.ps1 -TarFile ccd2-app-v2.0.tar
```

---

## 📦 File Structure

```
ccd2/
├── Dockerfile                    # Multi-stage production Dockerfile
├── .dockerignore                 # Files to exclude from build
├── docker-build.ps1              # Build script
├── docker-export.ps1             # Export script
├── docker-load-and-run.ps1       # Load and run script
├── DOCKER_DEPLOYMENT_GUIDE.md    # Full documentation
└── DOCKER_QUICK_START.md         # This file
```

---

## ✅ Verification Checklist

After deployment:

- [ ] Container is running: `docker ps`
- [ ] Health check passes: `http://localhost/api/health`
- [ ] Frontend loads: `http://localhost`
- [ ] API docs accessible: `http://localhost/docs`
- [ ] Can login to application
- [ ] File uploads work
- [ ] No errors in logs: `docker logs ccd2`

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` environment variable
- [ ] Configure external PostgreSQL database
- [ ] Configure external Redis cache
- [ ] Set up SSL/TLS (HTTPS)
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerts
- [ ] Test disaster recovery procedure
- [ ] Document custom configuration

---

## 💡 Tips

1. **Always verify the SHA256 hash** when transferring .tar files
2. **Use environment files** for complex configurations
3. **Enable auto-restart**: `--restart unless-stopped`
4. **Monitor resource usage**: `docker stats ccd2`
5. **Regular backups**: Backup `/app/uploads` and database
6. **Keep images updated**: Rebuild periodically with latest dependencies

---

## 📞 Need Help?

1. Check logs: `docker logs ccd2`
2. Review full guide: `DOCKER_DEPLOYMENT_GUIDE.md`
3. Check Docker status: `docker info`
4. Verify configuration: `docker exec ccd2 env`

