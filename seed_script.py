import sqlite3
import random
from datetime import datetime, timedelta
from database.db import get_db

def seed_expenses(user_id, count, months):
    categories = {
        "Food": {"range": (50, 800), "weight": 30, "descriptions": ["Lunch at Cafe", "Grocery Store", "Street Food", "Dinner at Home", "Tea and Snacks"]},
        "Transport": {"range": (20, 500), "weight": 20, "descriptions": ["Uber Ride", "Auto Rickshaw", "Petrol", "Bus Fare", "Metro Ticket"]},
        "Bills": {"range": (200, 3000), "weight": 15, "descriptions": ["Electricity Bill", "Water Bill", "Internet Recharge", "Mobile Bill", "Rent"]},
        "Health": {"range": (100, 2000), "weight": 5, "descriptions": ["Pharmacy", "Doctor Consultation", "Lab Test", "Vitamins", "Dentist"]},
        "Entertainment": {"range": (100, 1500), "weight": 5, "descriptions": ["Movie Ticket", "Netflix", "Bowling", "Gaming Zone", "Concert"]},
        "Shopping": {"range": (200, 5000), "weight": 15, "descriptions": ["New Clothes", "Footwear", "Electronics", "Amazon Order", "Gift"]},
        "Other": {"range": (50, 1000), "weight": 10, "descriptions": ["Stationery", "Donation", "Parking Fee", "Laundry", "Miscellaneous"]}
    }

    cat_names = list(categories.keys())
    cat_weights = [categories[c]["weight"] for c in cat_names]

    expenses = []
    start_date = datetime.now() - timedelta(days=months * 30)

    for _ in range(count):
        cat = random.choices(cat_names, weights=cat_weights, k=1)[0]
        amount = round(random.uniform(*categories[cat]["range"]), 2)
        desc = random.choice(categories[cat]["descriptions"])

        # Random date within the last 'months' months
        days_offset = random.randint(0, months * 30)
        date = (start_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')

        expenses.append((user_id, amount, cat, date, desc))

    db = get_db()
    try:
        cursor = db.cursor()
        # Use a transaction
        cursor.execute("BEGIN TRANSACTION")
        cursor.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        db.commit()

        # Get date range
        dates = [e[3] for e in expenses]
        min_date = min(dates)
        max_date = max(dates)

        print(f"Successfully inserted {len(expenses)} expenses.")
        print(f"Date range: {min_date} to {max_date}")
        print("\nSample records:")
        for e in expenses[:5]:
            print(f"Date: {e[3]}, Category: {e[2]}, Amount: ₹{e[1]}, Description: {e[4]}")

    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_expenses(7, 2, 6)
