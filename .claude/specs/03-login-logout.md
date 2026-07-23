# Spec: Login and Logout

## Overview
Implement user login and logout functionality so registered users can access their Spendly account. This step upgrades the existing stub `GET /login` route to handle POST requests for credential validation, sets user session data on successful login, and provides a logout endpoint to clear the session. This builds on the registration feature (step 02) and is required for accessing protected routes such as profile and expense management.

## Depends on
- Step 01 — Database setup (`users` table with `email` and `password_hash` columns, `get_db()` function)
- Step 02 — Registration (`create_user` helper function exists)

## Routes
- `GET /login` — render login form — public (already exists as stub, upgrade it)
- `POST /login` — process login form, validate credentials, set session, redirect to `/profile` — public
- `GET /logout` — clear session and redirect to landing page — logged-in users only

## Database changes
No database changes required. The existing `users` table (id, name, email, password_hash, created_at) and the `create_user` helper from step 02 are sufficient. We will use `check_password_hash` from `werkzeug.security` to verify passwords.

## Templates
- **Modify**: `templates/base.html`
  - Update the navigation bar to show conditional links:
    - When not logged in: show "Sign In" and "Get Started" (or similar) links.
    - When logged in: show the user's name (or email) and a "Logout" link.
- **Modify**: `templates/login.html`
  - Ensure the form uses `method="post"` and action `url_for('login')`.
  - Add a block to display flash error messages (e.g., "Invalid email or password").
  - Keep all existing visual design.

## Files to change
- `app.py` — upgrade `login()` to handle `GET` and `POST`; add `logout()` route; import `check_password_hash`; use `session` to store user info; add validation and flash messages.
- `templates/base.html` — update navigation links based on authentication state.
- `templates/login.html` — wire up form action/method and add flash message display.

## Files to create
None.

## New dependencies
No new dependencies. Uses `werkzeug.security.check_password_hash` (already installed via Flask's werkzeug) and Flask's built-in `session`, `flash`, `redirect`, `url_for`.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterised queries only — never use f-strings in SQL.
- Hash passwords with `werkzeug.security.generate_password_hash` (already done in registration) and verify with `check_password_hash` — never store or compare plaintext.
- `app.secret_key` must be set in `app.py` for `session` to work (already set as 'dev-secret-key-change-in-production').
- Server-side validation must check:
  1. Email and password are non-empty.
  2. Email exists in the `users` table.
  3. Password matches the stored hash (using `check_password_hash`).
- On any validation failure, re-render the login form with a flashed error message — do not redirect.
- On success, set `session['user_id']`, `session['user_email']`, `session['user_name']` (or similar), flash a success message, and redirect to `url_for('profile')`.
- For `GET /logout`, clear the session (using `session.clear()`), flash an optional info message, and redirect to `url_for('landing')`.
- Use `url_for()` for every internal link — never hardcode URLs.
- All templates must extend `base.html`.
- Use CSS variables — never hardcode hex values.

## Definition of done
- [ ] `GET /login` renders the login form without errors.
- [ ] Submitting the form with valid email and password logs the user in, sets session data, flashes a success message, and redirects to `/profile`.
- [ ] Submitting with a non-existent email re-renders the form with an error message (e.g., "Invalid email or password").
- [ ] Submitting with an incorrect password re-renders the form with an error message (e.g., "Invalid email or password").
- [ ] Submitting with empty email or password re-renders the form with a validation error.
- [ ] After login, the navigation bar shows the user's name/email and a logout link.
- [ ] Clicking logout clears the session, flashes a message (optional), and redirects to the landing page.
- [ ] Accessing `/profile` while logged in shows the profile page (stub is okay for now); accessing while logged out redirects to login (we may implement this later, but for now we can check that the session is set).
- [ ] No session fixation vulnerabilities: use Flask's built-in session handling.
