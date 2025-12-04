# Cloud Deployment Guide

This guide covers deploying the Content Service API to various cloud platforms.

## 📋 Pre-Deployment Checklist

- [ ] Update CORS settings in `app/main.py` (restrict origins)
- [ ] Set strong database passwords
- [ ] Configure environment variables
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall/security groups
- [ ] Set up monitoring and logging
- [ ] Configure backups for database

---

## 🚀 Platform-Specific Deployment Guides

### 1. Railway

**Steps:**

1. **Connect Repository:**

   - Go to [Railway](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Configure Environment Variables:**

   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ENVIRONMENT=production
   PORT=8000
   ```

3. **Add PostgreSQL Service:**

   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway automatically creates `DATABASE_URL`

4. **Deploy:**

   - Railway auto-detects Dockerfile
   - Or use: `railway up`

5. **Run Migrations:**
   ```bash
   railway run alembic upgrade head
   ```

**Commands:**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up

# Run migrations
railway run alembic upgrade head

# View logs
railway logs
```

---

### 2. Render

**Steps:**

1. **Create Web Service:**

   - Go to [Render](https://render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure:**

   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3

3. **Add PostgreSQL Database:**

   - Click "New" → "PostgreSQL"
   - Copy the connection string to `DATABASE_URL`

4. **Environment Variables:**

   ```bash
   DATABASE_URL=<from-postgres-service>
   PORT=10000
   ```

5. **Run Migrations:**
   - Add a "Background Worker" service
   - Command: `alembic upgrade head`
   - Or use Render Shell: `render shell`

**Auto-Deploy:** Render automatically deploys on git push

---

### 3. DigitalOcean App Platform

**Steps:**

1. **Create App:**

   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App" → "GitHub"

2. **Configure App Spec** (or use UI):

   ```yaml
   name: content-service
   services:
     - name: api
       github:
         repo: your-username/school-ai.content.api
         branch: main
       dockerfile_path: Dockerfile.prod
       http_port: 8000
       instance_count: 1
       instance_size_slug: basic-xxs
       envs:
         - key: DATABASE_URL
           scope: RUN_TIME
           value: ${db.DATABASE_URL}
         - key: ENVIRONMENT
           value: production
   databases:
     - name: db
       engine: PG
       version: "15"
   ```

3. **Add Database:**

   - In UI: "Resources" → "Create Database"
   - Select PostgreSQL 15

4. **Deploy:**

   - Click "Create Resources"
   - DigitalOcean builds and deploys

5. **Run Migrations:**
   - Use "Console" or add a one-off task:
   ```bash
   alembic upgrade head
   ```

---

### 4. AWS (EC2 + RDS)

**Steps:**

1. **Create RDS PostgreSQL:**

   ```bash
   # Using AWS CLI
   aws rds create-db-instance \
     --db-instance-identifier content-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username postgres \
     --master-user-password YourSecurePassword \
     --allocated-storage 20
   ```

2. **Launch EC2 Instance:**

   - AMI: Ubuntu 22.04
   - Instance Type: t3.small or larger
   - Security Group: Allow ports 22, 8000

3. **SSH into EC2:**

   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

4. **Install Docker:**

   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   ```

5. **Clone and Deploy:**

   ```bash
   git clone https://github.com/your-username/school-ai.content.api.git
   cd school-ai.content.api

   # Create .env
   echo "DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/dbname" > .env

   # Build and run
   docker compose -f docker-compose.prod.yml up -d --build

   # Run migrations
   docker compose exec content-service alembic upgrade head
   ```

6. **Set up Nginx (Reverse Proxy):**

   ```bash
   sudo apt install nginx
   # Configure /etc/nginx/sites-available/content-service
   # Point to localhost:8000
   ```

7. **Set up SSL with Let's Encrypt:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

---

### 5. Google Cloud Platform (Cloud Run)

**Steps:**

1. **Enable APIs:**

   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   ```

2. **Create Cloud SQL PostgreSQL:**

   ```bash
   gcloud sql instances create content-db \
     --database-version=POSTGRES_15 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

3. **Build and Deploy:**

   ```bash
   # Build container
   gcloud builds submit --tag gcr.io/PROJECT-ID/content-service

   # Deploy to Cloud Run
   gcloud run deploy content-service \
     --image gcr.io/PROJECT-ID/content-service \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL="postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE"
   ```

4. **Run Migrations:**
   ```bash
   gcloud run jobs create migrate \
     --image gcr.io/PROJECT-ID/content-service \
     --command alembic \
     --args upgrade,head
   ```

---

### 6. Azure (Container Instances + PostgreSQL)

**Steps:**

1. **Create Azure Database for PostgreSQL:**

   - Azure Portal → Create Resource → Azure Database for PostgreSQL
   - Configure and create

2. **Build and Push Image:**

   ```bash
   # Login to Azure
   az login
   az acr login --name yourregistry

   # Build and push
   docker build -f Dockerfile.prod -t yourregistry.azurecr.io/content-service:latest .
   docker push yourregistry.azurecr.io/content-service:latest
   ```

3. **Deploy Container Instance:**
   ```bash
   az container create \
     --resource-group your-rg \
     --name content-service \
     --image yourregistry.azurecr.io/content-service:latest \
     --dns-name-label your-dns-name \
     --ports 8000 \
     --environment-variables DATABASE_URL="postgresql://..."
   ```

---

## 🔧 Production Configuration

### Update CORS Settings

Edit `app/main.py`:

```python
import os

# In production, restrict CORS origins
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://yourdomain.com,https://www.yourdomain.com"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Change from ["*"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Environment Variables

Create `.env.production`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Application
ENVIRONMENT=production
LOG_LEVEL=info
PORT=8000

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECRET_KEY=your-secret-key-here

# Optional: Monitoring
SENTRY_DSN=your-sentry-dsn
```

---

## 📦 Using Production Docker Compose

```bash
# Build production image
docker compose -f docker-compose.prod.yml build

# Start service
docker compose -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.prod.yml exec content-service alembic upgrade head

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Stop service
docker compose -f docker-compose.prod.yml down
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` files**
2. **Use strong database passwords**
3. **Restrict CORS origins**
4. **Enable SSL/TLS (HTTPS)**
5. **Use secrets management** (AWS Secrets Manager, Azure Key Vault, etc.)
6. **Set up firewall rules**
7. **Regular security updates**
8. **Monitor logs for suspicious activity**

---

## 📊 Monitoring & Logging

### Health Checks

The service includes a health endpoint:

```bash
curl https://yourdomain.com/health
```

### Logging

Add structured logging:

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
```

### Monitoring Services

- **Sentry**: Error tracking
- **Datadog**: APM and logging
- **New Relic**: Application monitoring
- **Prometheus + Grafana**: Metrics

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway login --token ${{ secrets.RAILWAY_TOKEN }}
          railway up

      - name: Run Migrations
        run: |
          railway run alembic upgrade head
```

---

## 🆘 Troubleshooting

### Database Connection Issues

```bash
# Test connection
python -c "from app.db.session import engine; engine.connect(); print('Connected!')"
```

### Migration Issues

```bash
# Check current migration
alembic current

# View migration history
alembic history

# Rollback if needed
alembic downgrade -1
```

### Container Issues

```bash
# View logs
docker compose logs -f content-service

# Check container status
docker ps

# Restart service
docker compose restart content-service
```

---

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [PostgreSQL Production Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
