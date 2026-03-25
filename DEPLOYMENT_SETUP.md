# TrendNexAI Production Deployment Guide

> **Last Updated:** 2024 | **Status:** Production Ready ✅

## Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose (v20.10+)
- 4GB+ RAM, 20GB+ storage
- Linux server (Ubuntu 22.04 LTS recommended)

### Deploy with One Command

```bash
# 1. Clone & enter directory
git clone https://github.com/yourusername/trendnexai.git
cd trendnexai

# 2. Copy & configure environment
cp .env.example .env
nano .env  # Update API keys, passwords, domains

# 3. Deploy all 7 services
docker-compose up -d

# 4. Initialize database
docker-compose exec backend python -m app.db init_collections

# 5. Create admin user
docker-compose exec backend python -c "
from app.security import hash_password, add_admin_user
add_admin_user('admin', 'your_secure_password')
"

# 6. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8001
# Docs: http://localhost:8001/docs
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     TrendNexAI Production Stack                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Frontend   │  │   Backend    │  │    Nginx     │            │
│  │  Next.js     │  │   FastAPI    │  │   Proxy      │            │
│  │ (Port 3000)  │  │ (Port 8000)  │  │ (Port 80/443)│            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │                                     │
│         ┌──────────┬───────┼────────┬──────────┐                 │
│         │          │       │        │          │                 │
│  ┌──────▼────┐ ┌───▼──┐ ┌──▼────┐ ┌──▼────┐ ┌─▼────┐          │
│  │ MongoDB   │ │Redis │ │Celery │ │Celery │ │ Nginx│          │
│  │ (27017)   │ │(6379)│ │Worker │ │ Beat  │ │      │          │
│  │           │ │      │ │       │ │       │ │Config│          │
│  └───────────┘ └───────┘ └───────┘ └───────┘ └──────┘          │
│        DB         Cache    Jobs     Scheduler   Reverse         │
│                                                  Proxy           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7 Production Services

### 1. **MongoDB** (Database)
- **Image:** mongo:7.0
- **Port:** 27017 (internal)
- **Storage:** mongodb_data volume
- **Authentication:** Yes (MONGO_ROOT_USER/PASSWORD)
- **Replication:** Single node (set up cluster for high-availability)

### 2. **Redis** (Cache & Message Broker)
- **Image:** redis:7-alpine
- **Port:** 6379 (internal)
- **Storage:** redis_data volume (AOF enabled)
- **Authentication:** Yes (REDIS_PASSWORD)
- **Persistence:** Append-Only File (AOF)

### 3. **Backend API** (FastAPI)
- **Port:** 8001 (maps to 8000 internal)
- **Language:** Python 3.11
- **Auto-restarts:** Yes
- **Health Check:** /health endpoint
- **Services:**
  - REST API endpoints
  - JWT authentication
  - Rate limiting
  - Article management
  - Analytics tracking

### 4. **Celery Worker** (Background Jobs)
- **Concurrency:** 4 workers
- **Tasks:** Article processing, email, exports
- **Broker:** Redis
- **Storage:** Result backend in Redis
- **Restart:** Auto

### 5. **Celery Beat** (Scheduler)
- **Run:** Every 30 minutes - News fetch & processing
- **Schedule:** Configurable in main.py
- **Auto-restarts:** Yes
- **Database:** MongoDB for persistence

### 6. **Frontend** (Next.js)
- **Port:** 3000 (public)
- **Framework:** React 18 + TypeScript
- **Build:** Static + ISR
- **Image:** node:18-alpine
- **Auto-build:** Yes from source

### 7. **Nginx** (Optional - Reverse Proxy)
- **Port:** 80, 443
- **SSL:** Let's Encrypt support
- **Function:** Rate limiting, caching, compression

---

## Configuration

### Environment Variables (.env)

**Critical** - Must change:
```bash
# Database
MONGO_ROOT_PASSWORD=your_secure_password_minimum_20_chars

# Cache
REDIS_PASSWORD=your_secure_password_minimum_20_chars

# Credentials
ADMIN_PASSWORD=your_admin_password
SECRET_KEY=generate_with: python -c "import secrets; print(secrets.token_urlsafe(32))"

# APIs
OPENAI_API_KEY=sk-... (get from openai.com)
NEWS_API_KEY=... (get from newsapi.org)
```

**Important** - Review & update:
```bash
# Domain & URLs
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
NEXT_PUBLIC_SITE_URL=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Database Initialization

Collections created automatically:
```
articles           - News articles with metadata
analytics          - User engagement tracking
users              - Admin/editor accounts
categories         - Article categories
scheduled_jobs     - Celery Beat schedules
```

---

## Deployment Steps

### Step 1: Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### Step 2: Clone & Configure

```bash
# Clone repository
git clone https://github.com/yourusername/trendnexai.git
cd trendnexai

# Generate secure passwords
python3 << EOF
import secrets
print(f"SECRET_KEY: {secrets.token_urlsafe(32)}")
print(f"MONGO_PASSWORD: {secrets.token_urlsafe(20)}")
print(f"REDIS_PASSWORD: {secrets.token_urlsafe(20)}")
EOF

# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

### Step 3: Deploy Stack

```bash
# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f

# Verify all services running
docker-compose ps
```

### Step 4: Initialize Database

```bash
# Create admin user
docker-compose exec backend python << EOF
from app.db import db
from app.security import hash_password

admin_user = {
    "username": "admin",
    "password_hash": hash_password("your_secure_password"),
    "role": "admin",
    "is_active": True,
    "created_at": datetime.utcnow()
}
result = db.users.insert_one(admin_user)
print(f"Admin user created: {result.inserted_id}")
EOF

# Create indexes for performance
docker-compose exec backend python << EOF
from app.db import db
# Articles
db.articles.create_index([("slug", 1)])
db.articles.create_index([("status", 1)])
db.articles.create_index([("category", 1)])
db.articles.create_index([("tags", 1)])
db.articles.create_index([("createdAt", -1)])
# Analytics
db.analytics.create_index([("article_slug", 1)])
db.analytics.create_index([("timestamp", 1)])
print("Indexes created successfully")
EOF
```

### Step 5: Health Checks

```bash
# Check all services
curl http://localhost:8001/health
curl http://localhost:3000/

# Check Docker logs for errors
docker-compose logs backend
docker-compose logs celery-worker
docker-compose logs celery-beat

# Verify database connection
docker-compose exec backend python -c "
from app.db import db
count = db.articles.count_documents({})
print(f'Articles in database: {count}')
"

# Verify cache connection
docker-compose exec backend python -c "
from app.cache import CacheManager
import asyncio
result = asyncio.run(CacheManager.get_stats())
print(f'Redis stats: {result}')
"
```

---

## Monitoring & Maintenance

### Check Service Status

```bash
# All services
docker-compose ps

# Individual service logs
docker-compose logs backend -f
docker-compose logs celery-worker -f
docker-compose logs celery-beat -f

# Resource usage
docker stats

# Database size
docker-compose exec mongodb mongosh --eval "db.stats()"
```

### Backup & Restore

```bash
# Backup MongoDB
docker-compose exec mongodb mongodump --uri="mongodb://admin:password@localhost:27017/trendnexai" -o /backup/mongo_backup_$(date +%Y%m%d)

# Backup Redis
docker-compose exec redis redis-cli BGSAVE

# Restore MongoDB
docker-compose exec mongodb mongorestore /backup/mongo_backup_YYYYMMDD
```

### Updates & Upgrades

```bash
# Pull latest images
docker-compose pull

# Restart stack with new images
docker-compose up -d

# View changes
git diff CURRENT_HASH..NEW_HASH

# Rollback if needed
docker-compose down
git checkout PREVIOUS_HASH
docker-compose up -d
```

---

## Security Best Practices

### 1. Secrets Management

```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use secret manager in production
# AWS Secrets Manager, Vault, etc.
```

### 2. HTTPS/SSL

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure nginx with SSL
# See nginx.conf template
```

### 3. Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw default deny incoming
sudo ufw enable
```

### 4. Database Security

```bash
# Strong passwords
# Limit MongoDB access to localhost
# Enable MongoDB authentication
# Regular backups with encryption
```

### 5. API Security

```bash
# Rate limiting enabled ✅
# CORS configured ✅
# Input validation ✅
# SQL injection protection (MongoDB) ✅
# CSRF protection ✅

# Enable in .env
RATE_LIMIT_REQUESTS=100  # per minute
```

---

## Scaling (High Availability)

### Horizontal Scaling

```yaml
# docker-compose.yml - Add more workers
version: '3.9'
services:
  celery-worker-1:
    # Original worker
  celery-worker-2:
    # Second worker for parallel processing
    build: ...
    command: celery -A app.celery_worker worker
```

### Load Balancing

```bash
# With Nginx (included)
# Or AWS Load Balancer
# Or Kubernetes ingress
```

### Database Replication

```bash
# MongoDB replica set (cluster)
# Redis cluster (sentinel mode)
```

---

## Troubleshooting

### Service Not Starting

```bash
# Check logs
docker-compose logs service-name

# Rebuild service
docker-compose build --no-cache service-name

# Remove containers & start fresh
docker-compose rm service-name
docker-compose up -d service-name
```

### Database Connection Error

```bash
# Verify MongoDB is running
docker-compose exec mongodb mongosh --eval "db.version()"

# Check connection string
# Format: mongodb://user:password@host:port/database

# Verify network
docker network ls
```

### Out of Memory

```bash
# Check disk space
df -h

# Check container memory
docker stats

# Increase volume size or clean up
docker system prune -a
```

### Cache Issues

```bash
# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Check Redis size
docker-compose exec redis redis-cli INFO stats
```

---

## Performance Optimization

### Database Query Optimization

```
✅ Indexes created on:
   - slug (articles.slug)
   - status (articles.status)
   - category (articles.category)
   - createdAt (articles.createdAt)

✅ Use explain() to check query plans
   db.articles.find({status: "published"}).explain("executionStats")
```

### Caching Strategy

```
Redis TTLs:
- articles_list: 60s
- article_detail: 300s
- categories: 3600s
- search: 300s
```

### Frontend Optimization

```
✅ Next.js ISR: 3600s
✅ Image optimization: Automatic
✅ Code splitting: Automatic
✅ Static generation: 1000 top articles
```

---

## Monitoring & Alerts

### Recommended Tools

- **Logging:** ELK Stack, Datadog, or CloudWatch
- **Monitoring:** Prometheus + Grafana
- **Uptime:** UptimeRobot, StatusPage
- **Performance:** New Relic, DataDog
- **Error Tracking:** Sentry

### Key Metrics to Track

```
✅ API response time (target: <200ms)
✅ Database query time (target: <50ms)
✅ Cache hit rate (target: >80%)
✅ Error rate (target: <0.1%)
✅ CPU usage (target: <70%)
✅ Memory usage (target: <80%)
✅ Disk usage (target: <85%)
```

---

## Support & Documentation

- **API Docs:** http://localhost:8001/docs (Swagger)
- **GitHub:** https://github.com/yourusername/trendnexai
- **Issues:** GitHub Issues
- **Chat:** GitHub Discussions

---

## Quick Reference Commands

```bash
# View status
docker-compose ps

# View logs
docker-compose logs -f [service]

# Execute command
docker-compose exec [service] [command]

# Restart service
docker-compose restart [service]

# Stop all
docker-compose down

# Start all
docker-compose up -d

# Rebuild
docker-compose build --no-cache

# Pull latest
docker-compose pull

# Remove volumes (CAUTION!)
docker-compose down -v

# Scale service
docker-compose up -d --scale celery-worker=3
```

---

**Production Checklist:**

- [ ] All environment variables configured
- [ ] Passwords meet security requirements (>20 chars)
- [ ] HTTPS/SSL configured
- [ ] Firewall rules configured
- [ ] Backups scheduled
- [ ] Monitoring enabled
- [ ] Health checks passing
- [ ] Database indexes created
- [ ] Admin user created
- [ ] First news sync completed
- [ ] Load testing passed
- [ ] Security audit passed

---

**Last Updated:** 2024  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
