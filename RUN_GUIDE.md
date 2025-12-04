# How to Run Content Service

This guide provides step-by-step instructions for running the application in two ways:

1. **Docker** (Recommended - easier setup)
2. **Local** (Direct Python execution)

---

## 🐳 Option 1: Running in Docker

### Prerequisites

- Docker and Docker Compose installed
- Local PostgreSQL running (or use Docker PostgreSQL)

### Step-by-Step Instructions

#### Step 1: Create/Update `.env` file

**If using your local PostgreSQL:**

```bash
# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:Welcome%401@host.docker.internal:5432/vyon-content
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=content_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
EOF
```

**If using Docker PostgreSQL (default):**

```bash
# Use the setup script
./setup.sh
# Choose option 1 when prompted
```

#### Step 2: Build and start services

**For local PostgreSQL:**

```bash
docker compose -f docker-compose.local.yml up --build
```

**For Docker PostgreSQL:**

```bash
docker compose up --build
```

#### Step 3: Wait for services to be ready

Wait until you see:

```
content-service | Application startup complete.
```

#### Step 4: Run database migrations

```bash
# Generate initial migration (first time only)
docker compose exec content-service alembic revision --autogenerate -m "Initial migration"

# Apply migrations
docker compose exec content-service alembic upgrade head
```

#### Step 5: Verify the application

- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Step 6: Test the API

```bash
# Health check
curl http://localhost:8000/health

# Create a board
curl -X POST "http://localhost:8000/boards" \
  -H "Content-Type: application/json" \
  -d '{"name": "CBSE", "description": "Central Board of Secondary Education"}'
```

### Useful Docker Commands

```bash
# View logs
docker compose logs -f content-service

# Stop services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v

# Restart service
docker compose restart content-service

# Access container shell
docker compose exec content-service /bin/bash

# View database (if using Docker PostgreSQL)
docker compose exec postgres psql -U postgres -d content_db
```

---

## 💻 Option 2: Running Locally (Without Docker)

### Prerequisites

- Python 3.11 or higher
- PostgreSQL running locally
- pip (Python package manager)

### Step-by-Step Instructions

#### Step 1: Create virtual environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Create/Update `.env` file

```bash
# Create .env file with your local PostgreSQL
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:Welcome%401@localhost:5432/vyon-content
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=content_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
EOF
```

**Note:** Use `localhost` (not `host.docker.internal`) when running locally.

#### Step 4: Verify database connection

```bash
# Test connection (optional)
python -c "from app.db.session import engine; engine.connect(); print('✅ Database connection successful!')"
```

#### Step 5: Run database migrations

```bash
# Generate initial migration (first time only)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### Step 6: Start the application

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Step 7: Verify the application

- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

#### Step 8: Test the API

```bash
# Health check
curl http://localhost:8000/health

# Create a board
curl -X POST "http://localhost:8000/boards" \
  -H "Content-Type: application/json" \
  -d '{"name": "CBSE", "description": "Central Board of Secondary Education"}'
```

### Useful Local Development Commands

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback migration
alembic downgrade -1

# Check migration status
alembic current

# View all migrations
alembic history
```

---

## 🔧 Troubleshooting

### Issue: Cannot connect to database

**Docker:**

- Ensure PostgreSQL is running: `pg_isready -h localhost -p 5432`
- Check if using `host.docker.internal` (not `localhost`) in `.env`
- Verify database exists: `psql -U postgres -l | grep vyon-content`

**Local:**

- Verify PostgreSQL is running: `pg_isready`
- Check connection string in `.env` uses `localhost`
- Ensure database exists: `createdb -U postgres vyon-content`

### Issue: Migration errors

```bash
# Reset migrations (⚠️ WARNING: This deletes all data)
# Only do this in development!

# Docker:
docker compose exec content-service alembic downgrade base
docker compose exec content-service alembic upgrade head

# Local:
alembic downgrade base
alembic upgrade head
```

### Issue: Port already in use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
```

### Issue: Module not found errors

```bash
# Ensure you're in the virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📋 Quick Reference

### Docker Quick Start

```bash
# 1. Setup
./setup.sh

# 2. Start (local PostgreSQL)
docker compose -f docker-compose.local.yml up --build

# 3. Migrate
docker compose exec content-service alembic upgrade head

# 4. Access
# http://localhost:8000/docs
```

### Local Quick Start

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
# Create .env with: DATABASE_URL=postgresql://postgres:Welcome%401@localhost:5432/vyon-content

# 3. Migrate
alembic upgrade head

# 4. Run
uvicorn app.main:app --reload
```

---

## 🎯 Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Create test data**: Use the Swagger UI to create boards, states, etc.
3. **Check database**: Verify data in PostgreSQL
4. **Read documentation**: See `README.md` for API details

---

## 📝 Notes

- **URL Encoding**: Special characters in passwords must be URL-encoded:

  - `@` → `%40`
  - `#` → `%23`
  - `%` → `%25`
  - etc.

- **Database URL Format**:

  ```
  postgresql://username:password@host:port/database_name
  ```

- **Environment Variables**: The app reads from `.env` file automatically
