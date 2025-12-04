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
├── states.json      # Indian states
├── boards.json      # Education boards (national & state-specific)
├── syllabus.json    # Syllabus definitions
├── classes.json     # Classes/grades/semesters
├── subjects.json    # Subjects
└── chapters.json    # Chapters
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

### syllabus.json

```json
[
  {
    "board_name": "CBSE", // Must match board name
    "state_code": null, // Must match board's state (null for national)
    "name": "CBSE Class 10",
    "academic_year": "2024-25"
  }
]
```

### classes.json

```json
[
  {
    "syllabus_name": "CBSE Class 10", // Must match syllabus name
    "name": "Class 10",
    "display_order": 10
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

### Syllabus-Board Relationship

- If board is state-specific → syllabus `state_code` must match board's state
- If board is national → syllabus `state_code` must be `null`

### Reference Validation

- All referenced entities must exist:
  - `board_name` → must exist in boards
  - `state_code` → must exist in states
  - `syllabus_name` → must exist in syllabus
  - `class_name` → must exist in classes
  - `subject_name` → must exist in subjects

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

### Step 3: Add Syllabus

Edit `seed_data/syllabus.json`:

```json
{
  "board_name": "Goa State Board",
  "state_code": "GA",
  "name": "Goa SSC",
  "academic_year": "2024-25"
}
```

### Step 4: Add Classes, Subjects, Chapters

Follow the same pattern in respective JSON files.

### Step 5: Run Seed

```bash
make seed
```

## Troubleshooting

### Error: "Board 'X' not found"

- Check `boards.json` - board name must match exactly
- Ensure boards are seeded before syllabus

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
2. **Follow dependency order**: States → Boards → Syllabus → Classes → Subjects → Chapters
3. **Test incrementally**: Add a few records, test, then add more
4. **Version control**: Commit JSON files to track curriculum changes
5. **Backup before seeding**: Especially in production

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
