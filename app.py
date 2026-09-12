from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.db import get_db, init_db, seed_db, create_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

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


@app.route("/profile")
def profile():
    # Authentication guard
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Hardcoded data for UI validation (Step 4)
    user = {
        "name": session.get("user_name", "Prakhar Sharma"),
        "email": session.get("user_email", "prakhar@example.com"),
        "member_since": "January 2024",
        "initials": "PS"
    }

    stats = {
        "total_spent": "₹ 12,450.00",
        "transaction_count": 42,
        "top_category": "Food & Dining"
    }

    transactions = [
        {"date": "2024-09-10", "description": "Grocery Shopping", "category": "Shopping", "amount": "₹ 1,200.00"},
        {"date": "2024-09-08", "description": "Uber Ride", "category": "Transport", "amount": "₹ 350.00"},
        {"date": "2024-09-05", "description": "Dinner at Taj", "category": "Food", "amount": "₹ 4,500.00"},
        {"date": "2024-09-02", "description": "Netflix Subscription", "category": "Entertainment", "amount": "₹ 499.00"},
        {"date": "2024-08-28", "description": "Electric Bill", "category": "Utilities", "amount": "₹ 2,100.00"},
    ]

    categories = [
        {"name": "Food & Dining", "total": "₹ 4,200.00", "percentage": 34},
        {"name": "Shopping", "total": "₹ 3,100.00", "percentage": 25},
        {"name": "Transport", "total": "₹ 1,800.00", "percentage": 14},
        {"name": "Utilities", "total": "₹ 2,100.00", "percentage": 17},
        {"name": "Entertainment", "total": "₹ 1,250.00", "percentage": 10},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories
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
