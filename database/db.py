import sqlite3
from werkzeug.security import generate_password_hash

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled"""
    db = sqlite3.connect('spendly.db')
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db

def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS"""
    db = get_db()

    # Create users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create expenses table
    db.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    db.commit()
    db.close()

def seed_db():
    """Inserts sample data for development, prevents duplicate inserts"""
    db = get_db()

    # Check if users table already has data
    cursor = db.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]

    if user_count > 0:
        db.close()
        return  # Data already seeded

    # Insert demo user
    password_hash = generate_password_hash('demo123', method='pbkdf2:sha256')
    cursor = db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Demo User', 'demo@spendly.com', password_hash)
    )
    user_id = cursor.lastrowid

    # Insert sample expenses across categories
    sample_expenses = [
        # Food
        (user_id, 12.50, 'Food', '2026-07-05', 'Lunch at cafe'),
        (user_id, 25.00, 'Food', '2026-07-10', 'Groceries'),
        # Transport
        (user_id, 45.00, 'Transport', '2026-07-03', 'Gas refill'),
        (user_id, 15.00, 'Transport', '2026-07-12', 'Bus fare'),
        # Bills
        (user_id, 80.00, 'Bills', '2026-07-01', 'Electricity bill'),
        # Health
        (user_id, 30.00, 'Health', '2026-07-08', 'Pharmacy'),
        # Entertainment
        (user_id, 20.00, 'Entertainment', '2026-07-15', 'Movie tickets'),
        # Shopping
        (user_id, 60.00, 'Shopping', '2026-07-14', 'New clothes'),
    ]

    db.executemany(
        'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
        sample_expenses
    )

    db.commit()
    db.close()