# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Run the application**: `python app.py` or `flask run` (if FLASK_APP is set)
- **Run tests**: There are no tests currently set up. (If tests are added, use `pytest` or similar.)
- **Linting**: No linter configured. Consider adding `flake8` or `pylint`.
- **Database initialization**: The `database/db.py` file contains stubs for `get_db()`, `init_db()`, and `seed_db()`. Students will implement these in Step 1.
- **Static files**: Located in the `static/` directory.
- **Templates**: Located in the `templates/` directory, using Flask's Jinja2 templating.

## Project Structure

- `app.py`: Main Flask application containing route definitions.
- `templates/`: HTML templates for rendering pages.
  - `base.html`: Base template with common structure.
  - Other templates extend `base.html` for specific pages (landing, login, register, terms, privacy).
- `static/`: Static assets (CSS, JavaScript, images).
  - `main.js`: Main JavaScript file.
- `database/`: Database-related code.
  - `db.py`: Stub for database connection, initialization, and seeding.
- `venv/`: Python virtual environment (created during setup).
- `requirements.txt`: Python dependencies (Flask, etc.).

## Architecture Overview

This is a Flask web application following a typical MVC-like structure:

- **Models**: Not yet implemented; will be in `database/db.py` (or separate models module).
- **Views**: Route handlers in `app.py` that render templates.
- **Templates**: Jinja2 templates in the `templates/` directory.

The application is structured for a student project where each step implements a new feature:
1. Database setup
2. User authentication (login/register)
3. Logout
4. Profile page
5. Expense management (add, edit, delete)
6. etc.

## Common Development Tasks

- To run the app locally: `python app.py` (runs on http://localhost:5000)
- To stop the app: Press `Ctrl+C` in the terminal.
- To install dependencies: `pip install -r requirements.txt` (inside the virtual environment)
- To activate the virtual environment: `source venv/bin/activate` (on Unix/macOS) or `venv\Scripts\activate` (on Windows)

## Notes

- The application uses SQLite for simplicity; the database file will be created in the instance folder when `init_db()` is called.
- Templates extend `base.html` which includes Bootstrap for styling (note: Bootstrap files may need to be added to `static/` or via CDN).
- JavaScript interactivity is minimal; `main.js` is currently empty.
