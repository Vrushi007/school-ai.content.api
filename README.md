# Content Service API

A microservice for managing educational content across multiple education boards, states, universities, and exam syllabi.

## Features

- **Multi-Board Support**: CBSE, ICSE, IB, IGCSE, NIOS, State Boards, Engineering Universities, Exam Boards
- **Hierarchical Content Structure**: State → Board → Class → Subject → Chapter → Key Points
- **Key Points Management**: Atomic learning units with difficulty and cognitive levels (Bloom's taxonomy)
- **AI-Powered Lesson Planning**: Intelligent session grouping based on learning progression
- **Session Content Generation**: Automated summary, objectives, and detailed teaching content
- **Question Bank**: Comprehensive question storage and management
- **Hash-based Caching**: Efficient lesson plan reuse based on input parameters

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy 2.x**: ORM for database operations
- **Alembic**: Database migrations
- **PostgreSQL**: Relational database
- **Pydantic v2**: Data validation
- **Docker & Docker Compose**: Containerization

## Project Structure

```
content-service/
├── app/
│   ├── db/
│   │   ├── base.py          # SQLAlchemy declarative base
│   │   ├── session.py       # Database session management
│   │   └── init_db.py       # Database initialization
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic layer
│   ├── utils/               # Utility functions
│   └── main.py              # FastAPI application
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── alembic.ini              # Alembic configuration
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Database Models

1. **State**: Indian states and UTs
2. **Board**: Education boards (national and state-specific)
3. **Class**: Grades/semesters/sections within a board
4. **Subject**: Subjects within a class
5. **Chapter**: Chapters within a subject
6. **KeyPoint**: Atomic learning concepts with difficulty and cognitive levels
7. **KeyPointContent**: Detailed content for each key point
8. **LessonPlanInput**: Cached input parameters for lesson plan generation (with hash)
9. **LessonPlanSessionMap**: AI-grouped sessions with key point mappings
10. **LessonPlanSessionContent**: Generated session summaries, objectives, and detailed content
11. **Question**: Questions for assessments
12. **Answer**: Answers to questions

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Setup

1. **Clone the repository**

2. **Create `.env` file** (copy from `.env.example`):

   ```bash
   cp .env.example .env
   ```

3. **Build and start services**:

   ```bash
   docker compose up --build
   ```

4. **Run database migrations**:

   ```bash
   docker compose exec content-service alembic upgrade head
   ```

5. **Seed the database** (optional - populates initial curriculum data):
   ```bash
   make seed-docker
   # or
   docker compose exec content-service python seed_data.py
   ```
   See [SEED_DATA_GUIDE.md](./SEED_DATA_GUIDE.md) for detailed seeding documentation.

### Detailed Guides

- **[RUN_GUIDE.md](./RUN_GUIDE.md)** - Comprehensive setup and running instructions (Docker & Local)
- **[SEED_DATA_GUIDE.md](./SEED_DATA_GUIDE.md)** - Complete guide to seed data system and JSON formats
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Cloud deployment guides (Railway, Render, AWS, GCP, Azure, DigitalOcean)

### Using Makefile

```bash
# Build Docker images
make build

# Start services
make up

# Stop services
make down

# View logs
make logs

# Run migrations
make upgrade

# Create new migration
make migrate msg="description of migration"

# Seed database (Docker)
make seed-docker

# Seed database (Local)
make seed

# Open shell in container
make shell

# Clean up (remove containers and volumes)
make clean
```

## API Endpoints

### Boards

- `POST /boards` - Create a board
- `GET /boards` - List all boards

### States

- `POST /states` - Create a state
- `GET /states` - List all states

### Classes

- `POST /classes` - Create a class
- `GET /classes/{board_id}` - Get classes by board
- `PUT /classes/{id}` - Update a class
- `DELETE /classes/{id}` - Delete a class

### Subjects

- `POST /subjects` - Create a subject
- `GET /subjects/classes/{class_id}` - Get subjects by class
- `PUT /subjects/{id}` - Update a subject
- `DELETE /subjects/{id}` - Delete a subject

### Chapters

- `POST /chapters` - Create a chapter
- `GET /chapters/subjects/{subject_id}` - Get chapters by subject
- `GET /chapters/{id}` - Get chapter by ID
- `PUT /chapters/{id}` - Update a chapter
- `DELETE /chapters/{id}` - Delete a chapter

### Key Points

- `POST /key-points` - Create a key point
- `POST /key-points/bulk` - Create multiple key points
- `GET /key-points/chapters/{chapter_id}` - Get key points by chapter
- `PUT /key-points/{id}` - Update a key point
- `DELETE /key-points/{id}` - Delete a key point

### Lesson Plans (AI-Powered)

- `POST /lesson-plans/group-kps-into-sessions` - Group key points into teaching sessions
  - Request: board_id, class_id, subject_id, chapter_id, planned_sessions
  - Response: Grouped sessions with metadata, cached results when available
  
- `POST /lesson-plans/generate-session-summary` - Generate AI summary and objectives for a session
  - Request: session_map_id
  - Response: Session summary and learning objectives
  
- `POST /lesson-plans/get-session-detailed-content` - Get or generate detailed teaching content
  - Request: session_id
  - Response: Complete teaching script, board work, activities, assessments, resources

### Questions

- `POST /questions` - Create a question
- `POST /questions/bulk` - Create multiple questions
- `GET /questions/chapters/{chapter_id}` - Get questions by chapter
- `GET /questions/{id}` - Get question by ID
- `PUT /questions/{id}` - Update a question
- `DELETE /questions/{id}` - Delete a question

## Seeding Data

The project includes a comprehensive seed data system with curriculum data for multiple boards (CBSE, ICSE, IB, State Boards, etc.).

### Quick Seed

```bash
# Docker
make seed-docker

# Local
make seed
```

### What Gets Seeded

- 36 Indian states and UTs
- 185+ education boards (national and state-specific)
- 1,163+ classes/grades across all boards
- 333+ subjects
- Sample chapters for major boards (CBSE, ICSE, Karnataka State Board, etc.)

See [SEED_DATA_GUIDE.md](./SEED_DATA_GUIDE.md) for complete documentation on:

- JSON file formats
- Adding custom data
- Validation rules
- Troubleshooting

## Database Migrations

### Create a new migration:

```bash
docker compose exec content-service alembic revision --autogenerate -m "description"
```

### Apply migrations:

```bash
docker compose exec content-service alembic upgrade head
```

### Rollback migration:

4. **Start the server**:

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Seed the database** (optional):
   ```bash
   python seed_data.py
   ```

See [RUN_GUIDE.md](./RUN_GUIDE.md) for detailed local setup instructions.

## Cloud Deployment

Deploy to various cloud platforms with one-click or simple CLI commands:

- **Railway** - Automatic deployments from GitHub
- **Render** - Easy web service + PostgreSQL setup
- **AWS** - ECS/Fargate or EC2 with RDS
- **Google Cloud** - Cloud Run + Cloud SQL
- **Azure** - Container Apps + PostgreSQL
- **DigitalOcean** - App Platform deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete step-by-step deployment guides for each platform.

## Environment Variablesent-service alembic upgrade head

````

### Rollback migration:
```bash
docker compose exec content-service alembic downgrade -1
````

## Development

### Local Development (without Docker)

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL** and update `.env` with your database URL

3. **Run migrations**:

   ```bash
   alembic upgrade head
   ```

4. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

See `.env.example` for required environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: Database name

## License

MIT
