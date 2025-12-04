# Seed Data Directory

This directory contains JSON files with initial curriculum data for the database.

## Files

- `states.json` - Indian states
- `boards.json` - Education boards and universities (national and state-specific)
- `syllabus.json` - Syllabus definitions
- `classes.json` - Classes/grades/semesters within syllabi
- `subjects.json` - Subjects within classes
- `chapters.json` - Chapters within subjects

## Usage

Run the seed script:

```bash
# Local development
make seed
# or
python seed_data.py

# In Docker
make seed-docker
# or
docker compose exec content-service python seed_data.py
```

## Adding New Data

Simply edit the JSON files and run the seed script again. The system is idempotent:

- Existing records are updated if needed
- New records are added
- No duplicates are created

## JSON Format Guidelines

1. **Use unique identifiers**: Names should be unique within their scope
2. **Reference by name**: Use names (not IDs) to link related entities
3. **Follow relationships**: Ensure referenced entities exist before referencing them
4. **Order matters**: Seed in dependency order (states → boards → syllabus → classes → subjects → chapters)

## Example: Adding a New Board

Edit `boards.json`:

```json
{
  "name": "New Board Name",
  "description": "Board description",
  "state_code": "KA" // or null for national boards
}
```

Then run `make seed` again.
