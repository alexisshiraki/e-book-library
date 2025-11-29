"""PostgreSQL Integration Guide

This document explains how to use PostgreSQL with the CRUD application.

## Quick Start: Using SQLite (Default)

By default, the application uses SQLite. No setup required:

```powershell
python app.py
python crud.py list
pytest tests/
```

## PostgreSQL Setup

### 1. Install PostgreSQL

**Windows:**
Download from https://www.postgresql.org/download/windows/

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu):**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

### 2. Create a Database User and Database

**On Windows/macOS/Linux:**
```bash
# Connect to PostgreSQL default database
psql -U postgres

# Create a user (replace 'myuser' and 'mypassword')
CREATE USER myuser WITH PASSWORD 'mypassword';

# Create a database owned by the user
CREATE DATABASE myapp OWNER myuser;

# Grant privileges
ALTER ROLE myuser WITH CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE myapp TO myuser;
GRANT ALL PRIVILEGES ON SCHEMA public TO myuser;

# Exit psql
\q
```

### 3. Set DATABASE_URL Environment Variable

**PowerShell (Windows):**
```powershell
$env:DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/myapp"

# Or for a session-wide setting:
[Environment]::SetEnvironmentVariable("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/myapp", "User")
```

**Bash (macOS/Linux):**
```bash
export DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/myapp"

# Or add to ~/.bashrc for permanent setting:
echo 'export DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/myapp"' >> ~/.bashrc
source ~/.bashrc
```

### 4. Run the Application with PostgreSQL

The application automatically detects the DATABASE_URL and uses PostgreSQL:

```powershell
# PowerShell
$env:DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/myapp"
python app.py
```

```bash
# Bash
export DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/myapp"
python app.py
```

## Testing with PostgreSQL

### Create a Test Database

```bash
createdb test_db

# Or with specific user:
createdb -U myuser test_db
```

### Run Integration Tests with PostgreSQL

```powershell
# PowerShell
$env:DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/test_db"
python -m pytest tests/test_integration.py -v
```

```bash
# Bash
DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/test_db" pytest tests/test_integration.py -v
```

### Run All Tests (SQLite + PostgreSQL Checks)

```powershell
# Default: runs with SQLite
python -m pytest tests/ -v

# With PostgreSQL (requires DATABASE_URL set)
$env:DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/test_db"
python -m pytest tests/ -v
```

## Connection Strings

### SQLite (Default)
```
sqlite:///data.db                # File-based database
sqlite:///:memory:               # In-memory (for testing)
```

### PostgreSQL
```
postgresql://user:password@localhost:5432/dbname
postgres://user:password@localhost:5432/dbname  # Alternative
```

**Connection String Parts:**
- `user`: Database user (e.g., myuser)
- `password`: User password (e.g., mypassword)
- `localhost`: Database server host (e.g., 127.0.0.1, example.com)
- `5432`: PostgreSQL port (default is 5432)
- `dbname`: Database name (e.g., myapp)

## CRUD Operations with PostgreSQL

The CRUD helpers in `crud.py` work identically with both SQLite and PostgreSQL:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_config import init_db
from crud import create_user, list_users, get_user

# Option 1: Use environment variable (automatic detection)
import os
database_url = os.getenv('DATABASE_URL', 'sqlite:///data.db')
engine, Session = init_db(database_url)

# Option 2: Explicitly provide PostgreSQL URL
engine, Session = init_db('postgresql://myuser:mypassword@localhost:5432/myapp')

session = Session()
user = create_user(session, 'Alice', 30)
users = list_users(session)
session.close()
```

## Flask Web App with PostgreSQL

The Flask app automatically uses the configured database (SQLite or PostgreSQL):

```powershell
# PowerShell: Run with PostgreSQL
$env:DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/myapp"
python app.py
```

```bash
# Bash: Run with PostgreSQL
export DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/myapp"
python app.py
```

Then visit `http://localhost:5000` as usual.

## Troubleshooting

**Connection refused: Check PostgreSQL is running**
```bash
# macOS
brew services list | grep postgresql

# Linux
sudo service postgresql status

# Windows: Check PostgreSQL service in Services app
```

**FATAL: database "test_db" does not exist**
```bash
createdb test_db
# Or with specific user:
createdb -U myuser test_db
```

**psycopg2 module not found**
```powershell
pip install psycopg2-binary
# Or from requirements.txt:
pip install -r requirements.txt
```

**Permission denied for creating tables**
```bash
# Grant privileges to the user:
psql -U postgres
GRANT ALL PRIVILEGES ON SCHEMA public TO myuser;
\q
```

**psycopg2.OperationalError: could not translate host name**
- Check the hostname/IP in your DATABASE_URL
- Default is usually `localhost` or `127.0.0.1`
- If using a remote server, ensure network connectivity

## Performance Tips

- **Connection Pooling:** The `db_config.py` automatically sets `pool_size=10, max_overflow=20` for PostgreSQL
- **Connection Health:** Uses `pool_pre_ping=True` to verify connections before use
- **Batch Operations:** For inserting many users, consider wrapping in a transaction:
  ```python
  session.begin()
  for i in range(1000):
      create_user(session, f'User{i}', 20+i%50)
  session.commit()
  ```

## Summary

| Feature | SQLite | PostgreSQL |
|---------|--------|-----------|
| Setup | No setup needed | Requires server + user + database |
| Best for | Development, testing, small apps | Production, large data, concurrent access |
| Concurrency | Limited | Excellent |
| Data Persistence | File-based | Server-based |
| Default URL | `sqlite:///data.db` | Set via `DATABASE_URL` |
| Driver | Built-in | `psycopg2-binary` |

