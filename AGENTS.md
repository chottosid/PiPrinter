# AGENTS.md

Guidelines for agentic coding assistants working on PiPrinter codebase.

## Build and Development Commands

### Running the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Start development server (port 6969)
python -m app.main

# Alternative: Auto-reload mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 6969

# Run with uv (faster package manager)
uv run python -m app.main
```

### Dependency Management
```bash
pip install -r requirements.txt
# or: uv pip install -r requirements.txt
pip install package-name
pip freeze > requirements.txt
```

### Linting and Formatting (Recommended)
```bash
pip install black ruff mypy
black app/
ruff check app/
mypy app/
```

### Testing (Not Yet Implemented)
```bash
pytest                          # Run all tests
pytest tests/test_auth.py          # Run single file
pytest tests/test_auth.py::test_login  # Run specific test
pytest --cov=app tests/          # With coverage
```

### Database Operations
```bash
# Tables auto-created on startup
# Reset database (deletes all data)
rm printer_app.db
```

## Code Style Guidelines

### Import Ordering
```python
# 1. Standard library imports
from datetime import datetime, timedelta
from typing import Optional
import os

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 3. Local imports
from ..database import get_db
from ..models import User
from ..auth import get_current_user
```

### Type Hints
- All functions MUST have type hints
- Use `Optional[T]` for nullable types
- Use `List[T]`, `Dict[K, V]` for collections
- Use `async def` for async endpoints, `def` for sync functions

```python
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

async def register(user: UserRegister, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    ...
```

### Naming Conventions
- Classes: `PascalCase` (e.g., `UserRegister`, `PrinterManager`)
- Functions/variables: `snake_case` (e.g., `get_user_by_email`, `auth_token`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE`, `UPLOAD_DIR`)
- Private methods: `_underscore_prefix` (e.g., `_get_state_text`)

### Error Handling
- Use `HTTPException` for API errors with appropriate status codes
- Use try/except for external dependencies (CUPS, file I/O)
- Log errors where appropriate (use print for now, migrate to logging)

```python
# API errors
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# External dependency handling
try:
    self.conn = cups.Connection()
    return True
except Exception as e:
    print(f"Failed to connect to CUPS: {e}")
    return False
```

### Database Patterns
- Use SQLAlchemy ORM for all database operations
- Always use `db.commit()` after writes
- Use `db.refresh()` to get updated records
- Filter queries using model attributes

```python
# Create
db_user = User(email=user.email, hashed_password=hashed_password)
db.add(db_user)
db.commit()
db.refresh(db_user)

# Read
user = db.query(User).filter(User.email == email).first()

# Update/Delete
db.commit()
```

### FastAPI Endpoint Patterns
- Use `APIRouter` for grouping endpoints
- Include request/response models with `BaseModel`
- Use `Depends()` for database and auth dependencies
- Return JSON responses or template responses

```python
router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
```

### Template Patterns
- Use `Jinja2Templates` for HTML responses
- Always pass `"request": request` to TemplateResponse
- Extend base templates with `{% extends "base.html" %}`
- Use `{% block content %}` for page-specific content

```python
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
```

### Security Guidelines
- Always use `Depends(get_current_user)` for protected endpoints
- Hash passwords with `get_password_hash()` (bcrypt)
- Use JWT tokens for authentication (never store plain passwords)
- Validate file uploads (check extensions, sizes)
- Use environment variables for secrets (`.env` file)

### Configuration
- Use `.env` file for environment variables
- Load with `load_dotenv()` at module level
- Provide sensible defaults with `os.getenv("KEY", "default")`

```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
```

### Adding New Features
1. Create or update models in `app/models.py`
2. Add router in `app/routers/` with appropriate prefix
3. Include router in `app/main.py`
4. Create/update templates in `app/templates/`
5. Update `requirements.txt` if new dependencies needed
6. Test endpoints at `http://localhost:6969/docs`

### Common Gotchas
- Template directory must be `app/templates` (not relative paths)
- Database auto-creates on startup via `Base.metadata.create_all()`
- API_BASE in templates must match server port (default: 6969)
- CUPS requires `pycups` package and system installation
- SQLite database file is ignored by git (`.gitignore`)
- Uploads directory needs write permissions: `chmod 755 uploads`
