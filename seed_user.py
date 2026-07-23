import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
import random
import sys
sys.path.append('.')
from database.db import get_db

# Common Indian first names and last names
first_names = [
    "Rahul", "Priya", "Amit", "Sneha", "Vikram", "Ananya", "Rohan", "Pooja",
    "Arjun", "Deepika", "Karan", "Kavya", "Varun", "Nisha", "Aditya", "Isha",
    "Sameer", "Anjali", "Vivek", "Meera", "Siddharth", "Trisha", "Ashish",
    "Divya", "Manish", "Neha", "Akshay", "Amrita", "Jai", "Anusha"
]

last_names = [
    "Sharma", "Patel", "Singh", "Kumar", "Reddy", "Menon", "Agarwal", "Gupta",
    "Joshi", "Desai", "Iyer", "Pillai", "Malhotra", "Banerjee", "Choudhary",
    "Kapoor", "Mishra", "Verma", "Rao", "Kaur", "Biswas", "Saxena", "Khan",
    "Kaur", "Bose", "Kulkarni", "Nair", "Acharya"
]

def generate_unique_email(first_name, last_name):
    base = f"{first_name.lower()}.{last_name.lower()}"
    while True:
        # Generate a random 2-3 digit number
        suffix = random.randint(10, 999)
        email = f"{base}{suffix}@gmail.com"
        # Check if email exists in the database
        db = get_db()
        cursor = db.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone() is None:
            db.close()
            return email
        db.close()

def main():
    # Generate a random Indian name
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    name = f"{first_name} {last_name}"

    # Generate unique email
    email = generate_unique_email(first_name, last_name)

    # Hash password
    password_hash = generate_password_hash('password123', method='pbkdf2:sha256')

    # Current timestamp
    created_at = datetime.now().isoformat()

    # Insert into database
    db = get_db()
    cursor = db.execute(
        'INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
        (name, email, password_hash, created_at)
    )
    user_id = cursor.lastrowid
    db.commit()
    db.close()

    # Print confirmation
    print(f"id: {user_id}")
    print(f"name: {name}")
    print(f"email: {email}")

if __name__ == '__main__':
    main()