# Content Service API

A microservice for managing educational content across multiple education boards, states, universities, and exam syllabi.

## Features

- **Multi-Board Support**: CBSE, ICSE, IB, IGCSE, NIOS, State Boards, Engineering Universities, Exam Boards
- **Hierarchical Content Structure**: Board → State → Syllabus → Class → Subject → Chapter
- **Key Points Management**: Atomic learning units for each chapter
- **AI-Powered Lesson Planning**: Generate lesson plans with session grouping
- **Session Management**: Detailed session content with activities, assessments, and resources
- **Question Bank**: Comprehensive question storage and management

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

1. **Board**: Education boards and universities
2. **State**: States (for state boards)
3. **Syllabus**: Specific syllabus instances
4. **Class**: Grades/semesters/sections
5. **Subject**: Subjects within a class
6. **Chapter**: Chapters within a subject
7. **KeyPoint**: Atomic learning concepts
8. **Session**: AI-grouped teaching sessions
9. **SessionKeyPoint**: Mapping between sessions and key points
10. **SessionDetails**: Detailed teaching content
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

# Open shell in container
make shell
```

## API Endpoints

### Boards
- `POST /boards` - Create a board
- `GET /boards` - List all boards

### States
- `POST /states` - Create a state
- `GET /states` - List all states

### Syllabus
- `POST /syllabus` - Create a syllabus
- `GET /syllabus` - List all syllabi
- `GET /syllabus/{id}` - Get syllabus by ID
- `DELETE /syllabus/{id}` - Delete a syllabus

### Classes
- `POST /classes` - Create a class
- `GET /classes/syllabus/{syllabus_id}` - Get classes by syllabus
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

### Sessions
- `POST /sessions` - Create a session
- `GET /sessions/chapters/{chapter_id}` - Get sessions by chapter
- `PUT /sessions/{id}` - Update a session
- `DELETE /sessions/{id}` - Delete a session

### Session Key Points
- `POST /session-key-points/bulk` - Create session-key-point mappings
- `GET /session-key-points/sessions/{session_id}` - Get key points by session

### Session Details
- `POST /session-details` - Create session details
- `GET /session-details/sessions/{session_id}` - Get session details
- `PUT /session-details/{id}` - Update session details

### Questions
- `POST /questions` - Create a question
- `POST /questions/bulk` - Create multiple questions
- `GET /questions/chapters/{chapter_id}` - Get questions by chapter
- `GET /questions/{id}` - Get question by ID
- `PUT /questions/{id}` - Update a question
- `DELETE /questions/{id}` - Delete a question

### Lesson Plans
- `POST /lesson-plans/generate` - Generate lesson plan (placeholder for AI integration)

## API Documentation

Once the service is running, access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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
```bash
docker compose exec content-service alembic downgrade -1
```

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

