from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.db import get_db, init_db, seed_db, create_user
from database.queries import get_user_by_id, get_recent_transactions, get_summary_stats, get_category_breakdown
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Redirect to home if already logged in
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Basic validation
        if not name or not email or not password or not confirm_password:
            flash("All fields are required", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        # Connect to database
        db = get_db()

        try:
            # Create user
            user_id = create_user(name, email, password)

            # Set session variables
            session["user_id"] = user_id
            session["user_email"] = email
            session["user_name"] = name

            flash("Registration successful!", "success")
            return redirect(url_for("landing"))
        except sqlite3.IntegrityError:
            flash("Email already registered", "error")
            return render_template("register.html")
        except Exception as e:
            flash("An error occurred during registration", "error")
            return render_template("register.html")
        finally:
            db.close()

    # GET request
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect to home if already logged in
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        # Get form data
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate input
        if not email or not password:
            flash("Email and password are required", "error")
            return render_template("login.html")

        # Connect to database
        db = get_db()

        try:
            # Find user by email
            cursor = db.execute(
                "SELECT id, name, email, password_hash FROM users WHERE email = ?",
                (email,)
            )
            user = cursor.fetchone()

            # Check if user exists and password matches
            if user and check_password_hash(user["password_hash"], password):
                # Set session variables
                session["user_id"] = user["id"]
                session["user_email"] = user["email"]
                session["user_name"] = user["name"]

                flash("Login successful!", "success")
                return redirect(url_for("profile"))
            else:
                flash("Invalid email or password", "error")
                return render_template("login.html")
        except Exception as e:
            flash("An error occurred during login", "error")
            return render_template("login.html")
        finally:
            db.close()

    # GET request
    return render_template("login.html")


@app.route("/logout")
def logout():
    # Clear session
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #


def validate_date(date_str):
    """Validates a date string in YYYY-MM-DD format."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return None

def get_date_filter_context(date_from, date_to):
    """
    Validates dates, computes presets, and determines the active filter.
    Returns (valid_from, valid_to, active_filter, presets)
    """
    v_from = validate_date(date_from)
    v_to = validate_date(date_to)

    # Consistency check
    if v_from and v_to and v_from > v_to:
        return None, None, "error", {}

    today = datetime.now().date()
    presets = {
        "this-month": {
            "from": today.replace(day=1).strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d")
        },
        "last-3-months": {
            "from": (today - timedelta(days=90)).strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d")
        },
        "last-6-months": {
            "from": (today - timedelta(days=180)).strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d")
        }
    }

    active_filter = "all"
    if v_from and v_to:
        active_filter = "custom"
        for key, range_val in presets.items():
            if v_from == range_val["from"] and v_to == range_val["to"]:
                active_filter = key
                break

    return v_from, v_to, active_filter, presets

@app.route("/profile")
def profile():
    # Authentication guard
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    # Fetch real user data
    user = get_user_by_id(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for("login"))

    # --- Date Filter Logic ---
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    valid_from, valid_to, active_filter, presets = get_date_filter_context(date_from, date_to)

    if active_filter == "error":
        flash("Start date must be before end date.", "error")
        valid_from, valid_to, active_filter = None, None, "all"

    stats = get_summary_stats(user_id, valid_from, valid_to)
    transactions = get_recent_transactions(user_id, date_from=valid_from, date_to=valid_to)
    categories = get_category_breakdown(user_id, valid_from, valid_to)

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
        date_from=valid_from,
        date_to=valid_to,
        active_filter=active_filter,
        presets=presets
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


# Initialize database and seed data on application startup
with app.app_context():
    init_db()
    seed_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
