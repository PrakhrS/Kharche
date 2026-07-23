import sqlite3
import random
import sys
from datetime import datetime, timedelta

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled"""
    db = sqlite3.connect('spendly.db')
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db

def main():
    if len(sys.argv) != 4:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    # Verify user exists
    db = get_db()
    cursor = db.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    db.close()
    if not user:
        print(f"No user found with id {user_id}.")
        sys.exit(1)

    # Categories with weights and ranges (amount in ₹)
    categories = {
        'Food': {'weight': 30, 'range': (50, 800), 'descriptions': [
            'Lunch at local restaurant', 'Groceries from kirana store', 'Snacks and tea',
            'Dinner with family', 'Breakfast at hotel', 'Food delivery', 'Vegetables market',
            'Milk and dairy products', 'Spices and condiments', 'Sweet shop purchase'
        ]},
        'Transport': {'weight': 20, 'range': (20, 500), 'descriptions': [
            'Auto rickshaw fare', 'Bus ticket', 'Metro recharge', 'Fuel for bike',
            'Petrol for car', 'Parking fees', 'Toll charges', 'Cab service',
            'Vehicle maintenance', 'Bike servicing'
        ]},
        'Bills': {'weight': 15, 'range': (200, 3000), 'descriptions': [
            'Electricity bill', 'Water bill', 'Gas cylinder', 'Internet recharge',
            'Mobile postpaid', 'DTH recharge', 'Landline bill', 'Maintenance charges',
            'Society fee', 'Property tax installment'
        ]},
        'Health': {'weight': 10, 'range': (100, 2000), 'descriptions': [
            'Doctor consultation', 'Medicines from pharmacy', 'Diagnostic tests',
            'Dental checkup', 'Eye checkup and glasses', 'Ayurvedic treatment',
            'Health insurance premium', 'Fitness center fee', 'Yoga classes',
            'Medical equipment'
        ]},
        'Entertainment': {'weight': 10, 'range': (100, 1500), 'descriptions': [
            'Movie tickets', 'Concert or show', 'Amusement park', 'Gaming zone',
            'Streaming subscription', 'Book purchase', 'Magazine subscription',
            'Sports event tickets', 'Weekend getaway', 'Museum entry'
        ]},
        'Shopping': {'weight': 10, 'range': (200, 5000), 'descriptions': [
            'Clothing purchase', 'Footwear', 'Electronics accessory',
            'Home décor item', 'Kitchen utensils', 'Personal grooming',
            'Gift for family', 'Festival shopping', 'Online marketplace',
            'Traditional wear'
        ]},
        'Other': {'weight': 5, 'range': (50, 1000), 'descriptions': [
            'Postage and courier', 'Bank charges', 'ATM withdrawal fee',
            'Document processing', 'Minor repair', 'Cleaning services',
            'Laundry bill', 'Pet care expenses', 'Donation or charity',
            'Miscellaneous expenses'
        ]}
    }

    # Prepare weighted category selection
    cat_list = []
    weights = []
    for cat, data in categories.items():
        cat_list.append(cat)
        weights.append(data['weight'])

    # Generate expenses
    expenses = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30*months)

    for _ in range(count):
        # Select category based on weights
        category = random.choices(cat_list, weights=weights)[0]
        data = categories[category]
        amount = round(random.uniform(*data['range']), 2)
        # Random date within the range
        time_between_dates = end_date - start_date
        days_between = time_between_dates.days
        random_days = random.randrange(days_between)
        random_date = start_date + timedelta(days=random_days)
        date_str = random_date.strftime('%Y-%m-%d')
        description = random.choice(data['descriptions'])
        expenses.append((user_id, amount, category, date_str, description))

    # Insert in a single transaction
    db = get_db()
    try:
        db.executemany(
            '''INSERT INTO expenses (user_id, amount, category, date, description)
               VALUES (?, ?, ?, ?, ?)''',
            expenses
        )
        db.commit()
        inserted_count = db.execute('SELECT COUNT(*) FROM expenses WHERE user_id = ?', (user_id,)).fetchone()[0]
        # Get date range for this user's expenses
        date_range = db.execute(
            '''SELECT MIN(date) as min_date, MAX(date) as max_date
               FROM expenses WHERE user_id = ?''',
            (user_id,)
        ).fetchone()
        # Get a sample of 5 recent expenses
        sample = db.execute(
            '''SELECT id, amount, category, date, description
               FROM expenses WHERE user_id = ?
               ORDER BY date DESC LIMIT 5''',
            (user_id,)
        ).fetchall()
        db.close()
    except Exception as e:
        db.rollback()
        db.close()
        print(f"Error inserting expenses: {e}")
        sys.exit(1)

    # Print confirmation
    print(f"Inserted {inserted_count} expenses for user {user_id}")
    print(f"Date range: {date_range['min_date']} to {date_range['max_date']}")
    print("\nSample of 5 inserted records:")
    for exp in sample:
        print(f"ID: {exp['id']}, Amount: ₹{exp['amount']:.2f}, Category: {exp['category']}, Date: {exp['date']}, Description: {exp['description']}")

if __name__ == '__main__':
    main()