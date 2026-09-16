import pytest
from app import app
from database.db import init_db, get_db, create_user
from database.queries import insert_expense
import sqlite3
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            init_db()
            # Clear tables to ensure a clean state for each test
            db = get_db()
            db.execute("DELETE FROM expenses")
            db.execute("DELETE FROM users")
            db.commit()
            db.close()
            # Create a test user
            user_id = create_user("Test User", "test@example.com", "password123")
            yield client, user_id

def test_insert_expense_valid(client):
    client_app, user_id = client
    # Test valid insertion
    insert_expense(user_id, 50.0, "Food", "2026-03-20", "Lunch")

    db = get_db()
    cursor = db.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row['amount'] == 50.0
    assert row['category'] == "Food"
    assert row['date'] == "2026-03-20"
    assert row['description'] == "Lunch"
    db.close()

def test_insert_expense_no_description(client):
    client_app, user_id = client
    # Test insertion with None/empty description
    insert_expense(user_id, 20.0, "Transport", "2026-03-21", "")

    db = get_db()
    cursor = db.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row['description'] is None
    db.close()

def test_add_expense_get_unauthenticated(client):
    client_app, user_id = client
    response = client_app.get("/expenses/add")
    assert response.status_code == 302
    assert response.location.endswith("/login")

def test_add_expense_get_authenticated(client):
    client_app, user_id = client
    with client_app.session_transaction() as sess:
        sess['user_id'] = user_id

    response = client_app.get("/expenses/add")
    assert response.status_code == 200
    assert b'amount' in response.data
    assert b'category' in response.data
    assert b'date' in response.data
    assert b'description' in response.data
    assert b'Food' in response.data
    assert b'Other' in response.data

def test_add_expense_post_unauthenticated(client):
    client_app, user_id = client
    response = client_app.post("/expenses/add", data={
        "amount": "50.0",
        "category": "Food",
        "date": "2026-03-20",
        "description": "Lunch"
    })
    assert response.status_code == 302
    assert response.location.endswith("/login")

def test_add_expense_post_success(client):
    client_app, user_id = client
    with client_app.session_transaction() as sess:
        sess['user_id'] = user_id

    response = client_app.post("/expenses/add", data={
        "amount": "50.0",
        "category": "Food",
        "date": "2026-03-20",
        "description": "Lunch"
    })

    assert response.status_code == 302
    assert response.location.endswith("/profile")

    db = get_db()
    cursor = db.execute("SELECT * FROM expenses WHERE user_id = ? AND amount = 50.0", (user_id,))
    row = cursor.fetchone()
    assert row is not None
    db.close()

def test_add_expense_post_missing_amount(client):
    client_app, user_id = client
    with client_app.session_transaction() as sess:
        sess['user_id'] = user_id

    response = client_app.post("/expenses/add", data={
        "amount": "",
        "category": "Food",
        "date": "2026-03-20",
        "description": "Lunch"
    })

    assert response.status_code == 200
    assert b"Invalid amount provided" in response.data or b"Amount must be a positive number" in response.data

def test_add_expense_post_zero_amount(client):
    client_app, user_id = client
    with client_app.session_transaction() as sess:
        sess['user_id'] = user_id

    response = client_app.post("/expenses/add", data={
        "amount": "0",
        "category": "Food",
        "date": "2026-03-20",
        "description": "Lunch"
    })

    assert response.status_code == 200
    assert b"Amount must be a positive number" in response.data

def test_add_expense_post_non_numeric_amount(client):
    client_app, user_id = client
    with client_app.session_transaction() as sess:
        sess['user_id'] = user_id

    response = client_app.post("/expenses/add", data={
        "amount": "abc",
        "category": "Food",
        "date": "2026-03-20",
        "description": "Lunch"
    })

    assert response.status_code == 200
    assert b"Invalid amount provided" in response.data

def test_add_expense_post_invalid_category(client):
    client_app, user_id = client
    with client_app.session_transaction() as sess:
        sess['user_id'] = user_id

    response = client_app.post("/expenses/add", data={
        "amount": "50.0",
        "category": "InvalidCat",
        "date": "2026-03-20",
        "description": "Lunch"
    })

    assert response.status_code == 200
    assert b"Please select a valid category" in response.data

def test_add_expense_post_invalid_date(client):
    client_app, user_id = client
    with client_app.session_transaction() as sess:
        sess['user_id'] = user_id

    response = client_app.post("/expenses/add", data={
        "amount": "50.0",
        "category": "Food",
        "date": "not-a-date",
        "description": "Lunch"
    })

    assert response.status_code == 200
    assert b"A valid date is required" in response.data

def test_add_expense_post_no_description(client):
    client_app, user_id = client
    with client_app.session_transaction() as sess:
        sess['user_id'] = user_id

    response = client_app.post("/expenses/add", data={
        "amount": "50.0",
        "category": "Food",
        "date": "2026-03-20",
        "description": ""
    })

    assert response.status_code == 302
    assert response.location.endswith("/profile")

    db = get_db()
    cursor = db.execute("SELECT * FROM expenses WHERE user_id = ? AND description IS NULL", (user_id,))
    row = cursor.fetchone()
    assert row is not None
    db.close()
