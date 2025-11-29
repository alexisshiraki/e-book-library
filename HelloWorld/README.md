# HelloWorld

Simple Python grade calculator example and run instructions.

**Prerequisites:**

- Python 3.8 or newer installed and available in your PATH.

**Setup (PowerShell)**

1. Check Python is installed:

```powershell
python --version
```

2. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Upgrade `pip` and install dependencies (none required by default):

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Run the app**

Run the grade calculator interactively:

```powershell
python .\hello.py
```

Or provide input via a pipe (example prints `Grade: A`):

```powershell
echo 95 | python .\hello.py
```

**Notes**

- The original, broken version was backed up as `hello_backup.py`.
- `app.py` currently contains shell/clone commands and is not valid Python; review before executing.
- Your workspace contains a VS Code build task that runs `msbuild` (`.vscode\tasks.json`) — this is for .NET projects and not required for running this Python script.

**Optional: Create a single-file executable**

Install `pyinstaller` and create an executable:

```powershell
pip install pyinstaller
pyinstaller --onefile hello.py
```

**Database example (SQLAlchemy)**

This repository includes a small SQLAlchemy ORM example in `db_sqlalchemy.py` that demonstrates:

- Creating an SQLite database file `data.db`.
- Creating a `users` table.
- Inserting and querying rows.

To run the example after activating the venv:

```powershell
pip install -r requirements.txt
python .\db_sqlalchemy.py
```

**db_sqlalchemy example output**

Running the SQLAlchemy example (`db_sqlalchemy.py`) will create `data.db` (if missing), create the `users` table, insert one example row, and print rows. Example output:

```powershell
$ python .\db_sqlalchemy.py
1: Alice (30)
```


**CRUD helpers and demo**

This repo includes `crud.py` with simple helper functions that operate on a SQLAlchemy `Session`:

- `create_user(session, name, age=None)` — create and return a `User`.
- `get_user(session, user_id)` — fetch a user by id.
- `update_user_age(session, user_id, new_age)` — update and return the user.
- `delete_user(session, user_id)` — delete a user and return `True` if deleted.
- `list_users(session, limit=None, offset=0)` — return users (ordered by id) with optional limit/offset.
- `paginate_users(session, page=1, per_page=10)` — returns a dict with `items`, `total`, `page`, `per_page`.
- `filter_users_by_age(session, min_age=None, max_age=None)` — return users filtered by age range.

Quick demo (file-based `data.db`):

```powershell
python .\crud.py
```

Or run the interactive demo inside `crud.py` (creates sample rows and shows listing, filtering, pagination).

**CLI Usage**

The `crud.py` script includes a small CLI you can use against the file-based `data.db`.

Common examples (PowerShell):

```powershell
# Create a user
python .\crud.py create "Sam" --age 34

# List users (limit + offset)
python .\crud.py list --limit 10 --offset 0

# Get a user by id
python .\crud.py get 1

# Update a user's age
python .\crud.py update 1 --age 35

# Delete a user
python .\crud.py delete 1

# Paginate (page, per-page)
python .\crud.py paginate --page 1 --per-page 5

# Filter by age range
python .\crud.py filter --min-age 25 --max-age 40

# Run the demo (same as no args)
python .\crud.py demo
```

These examples assume you have created and activated a virtual environment and installed dependencies from `requirements.txt`.

**Example outputs**

Below are sample outputs you can expect when running a few common commands.

- Create:

```powershell
$ python .\crud.py create "Sam" --age 34
Created: 1 Sam (34)
```

- List:

```powershell
$ python .\crud.py list --limit 10
1: Sam (34)
2: Alice (30)
```

- Paginate:

```powershell
$ python .\crud.py paginate --page 1 --per-page 1
Page 1 (1 per page) - total: 2
1: Sam (34)
```

- Filter:

```powershell
$ python .\crud.py filter --min-age 30
2: Alice (30)
```

**Troubleshooting**

- Virtual environment not active / `python` resolves to system Python:
	- Ensure you activate the venv before running commands:
		```powershell
		.\.venv\Scripts\Activate.ps1
		```

- `alembic` command not found:
	- Install Alembic into the environment: `pip install alembic` or use `python -m alembic`.

- `pytest` not found in PowerShell:
	- If `pytest` is installed in the venv, run with the interpreter: `python -m pytest`.

- `sqlite3.OperationalError: database is locked`:
	- Close other processes using `data.db`. On Windows, antivirus or editors may lock the file; retry after closing them.

- Alembic `table already exists` when running `upgrade`:
	- This happens if you previously created tables manually. Use `alembic stamp head` to record the migration state without reapplying SQL, or drop the existing tables before running migrations in a fresh environment.

**Flask Web UI**

A web interface is provided in `app.py` for managing users through a browser. After installing dependencies, start the web server:

```powershell
python .\app.py
```

Then visit `http://localhost:5000` in your browser. The interface provides:

- **List users** (paginated, 10 per page) — view all users with links to edit/delete
- **View user** — see details for a specific user
- **Create user** — form to add a new user (name required, age optional)
- **Edit user** — update existing user name and age
- **Delete user** — remove a user (with confirmation)

Example workflow:
1. Visit `http://localhost:5000` to see the list (initially empty)
2. Click "+ New User" to create one
3. Enter name "Alice", age "30", submit
4. See Alice in the list
5. Click "Alice" name link to view details
6. Click "Edit" to change her age to "31"
7. Back on list, click "Delete" to remove her (confirm when prompted)

The web app uses the same SQLAlchemy ORM and CRUD helpers as the CLI, so data created via the web UI is accessible via CLI and vice versa.

**One-line PowerShell setup**

Create and activate a virtualenv, upgrade pip, and install requirements in one line (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install --upgrade pip; pip install -r requirements.txt
```


