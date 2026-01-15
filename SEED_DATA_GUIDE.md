# Seed Data System Guide

## Overview

The seed data system allows you to populate the database with initial curriculum data using JSON files. It's designed to be:

- **Idempotent**: Safe to run multiple times
- **Extensible**: Add new data by editing JSON files
- **Validated**: Checks relationships and fails loudly on errors

## Quick Start

```bash
# 1. Run migrations first
alembic upgrade head

# 2. Seed the database
make seed
# or
python seed_data.py

# In Docker
make seed-docker
```

## Directory Structure

```
seed_data/
├── states.json      # Indian states and UTs
├── boards.json      # Education boards (national & state-specific)
├── classes.json     # Classes/grades/semesters (linked to boards)
├── subjects.json    # Subjects (linked to classes)
└── chapters.json    # Chapters (linked to subjects)
```

## JSON File Formats

### states.json

```json
[
  { "name": "Karnataka", "code": "KA" },
  { "name": "Tamil Nadu", "code": "TN" }
]
```

### boards.json

```json
[
  {
    "name": "CBSE",
    "description": "Central Board of Secondary Education",
    "state_code": null // null for national boards
  },
  {
    "name": "Karnataka State Board",
    "description": "KSEEB",
    "state_code": "KA" // state code for state-specific boards
  }
]
```

### classes.json

```json
[
  {
    "board_name": "CBSE", // Must match board name
    "name": "Class 10",
    "display_order": 10
  },
  {
    "board_name": "Karnataka State Board",
    "name": "1st PUC",
    "display_order": 11
  }
]
```

### subjects.json

```json
[
  {
    "class_name": "Class 10", // Must match class name
    "name": "Science"
  }
]
```

### chapters.json

```json
[
  {
    "subject_name": "Science", // Must match subject name
    "title": "Light – Reflection and Refraction",
    "chapter_number": 1,
    "description": "Optional description"
  }
]
```

## Adding New Data

1. **Edit the appropriate JSON file** in `seed_data/`
2. **Run the seed script**:
   ```bash
   make seed
   ```

The system will:

- Add new records
- Update existing records (if fields changed)
- Skip duplicates (idempotent)

## Validation Rules

### Board-State Relationship

- National boards: `state_code` must be `null`
- State boards: `state_code` must match an existing state code

### Reference Validation

- All referenced entities must exist:
  - `state_code` → must exist in states (for state-specific boards)
  - `board_name` → must exist in boards (for classes)
  - `class_name` → must exist in classes (for subjects)
  - `subject_name` → must exist in subjects (for chapters)

### Data Hierarchy

- States → Boards (boards reference states)
- Boards → Classes (classes reference boards)
- Classes → Subjects (subjects reference classes)
- Subjects → Chapters (chapters reference subjects)

## Error Handling

The script will:

- ✅ **Fail loudly** if references don't exist
- ✅ **Validate** board-state relationships
- ✅ **Warn** if duplicate names found (uses first match)
- ✅ **Rollback** on errors (transaction safety)

## Example: Adding New Curriculum

### Step 1: Add State (if new)

Edit `seed_data/states.json`:

```json
{ "name": "Goa", "code": "GA" }
```

### Step 2: Add Board

Edit `seed_data/boards.json`:

```json
{
  "name": "Goa State Board",
  "description": "Goa Board of Secondary Education",
  "state_code": "GA"
}
```

### Step 3: Add Classes

Edit `seed_data/classes.json`:

```json
{
  "board_name": "Goa State Board",
  "name": "Class 10 (SSC)",
  "display_order": 10
}
```

### Step 4: Add Subjects and Chapters

Follow the same pattern in respective JSON files.

### Step 5: Run Seed

```bash
make seed
```

## Troubleshooting

### Error: "Board 'X' not found"

- Check `boards.json` - board name must match exactly
- Ensure boards are seeded before classes

### Error: "State with code 'X' not found"

- Check `states.json` - state code must exist
- Ensure states are seeded before boards

### Error: "Class 'X' not found"

- Check `classes.json` - class name must match exactly
- Ensure classes are seeded before subjects

### Warning: "Multiple classes/subjects named 'X' found"

- Make names more specific in JSON files
- Example: "Class 10 (CBSE)" vs "Class 10 (Karnataka)"

## Best Practices

1. **Use descriptive names**: Make names unique and descriptive
2. **Follow dependency order**: States → Boards → Classes → Subjects → Chapters
3. **Test incrementally**: Add a few records, test, then add more
4. **Version control**: Commit JSON files to track curriculum changes
5. **Backup before seeding**: Especially in production
6. **Run idempotently**: Safe to run seed script multiple times - it updates existing records

## Production Usage

```bash
# 1. Backup database
pg_dump -U postgres content_db > backup.sql

# 2. Run migrations
alembic upgrade head

# 3. Seed data
python seed_data.py

# 4. Verify
# Check API endpoints or database directly
```

## Extending the System

To add new entity types:

1. Create JSON file in `seed_data/`
2. Add model import in `seed_data.py`
3. Create seed function following the pattern
4. Call function in `main()` in dependency order
5. Update this guide
