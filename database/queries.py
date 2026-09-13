from database.db import get_db
from datetime import datetime

def get_user_by_id(user_id):
    """
    Fetch user details by ID.
    Returns a dict with name, email, member_since (formatted as 'Month YYYY').
    """
    db = get_db()
    try:
        cursor = db.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            # Convert ISO timestamp 'YYYY-MM-DD HH:MM:SS' to 'Month YYYY'
            created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
            member_since = created_at.strftime('%B %Y')
            return {
                "name": row['name'],
                "email": row['email'],
                "member_since": member_since,
                "initials": (row['name'][0] if row['name'] else 'U').upper()
            }
        return None
    finally:
        db.close()

def get_summary_stats(user_id):
    """
    Calculate total spent, transaction count, and top category for a user.
    Returns a dict with formatted values.
    """
    db = get_db()
    try:
        # Get total spent and count
        cursor = db.execute(
            "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()

        total_spent = row['total'] if row['total'] is not None else 0.0
        transaction_count = row['count'] if row['count'] is not None else 0

        if transaction_count == 0:
            return {
                "total_spent": "₹ 0.00",
                "transaction_count": 0,
                "top_category": "—"
            }

        # Get top category
        cursor = db.execute(
            "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,)
        )
        cat_row = cursor.fetchone()
        top_category = cat_row['category'] if cat_row else "—"

        return {
            "total_spent": f"₹ {total_spent:,.2f}",
            "transaction_count": transaction_count,
            "top_category": top_category
        }
    finally:
        db.close()


def get_recent_transactions(user_id, limit=10):
    """
    Fetch recent expenses for the given user_id.
    Returns a list of dicts with formatted amount.
    """
    db = get_db()
    try:
        cursor = db.execute(
            "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()

        transactions = []
        for row in rows:
            transactions.append({
                "date": row['date'],
                "description": row['description'],
                "category": row['category'],
                "amount": f"₹ {row['amount']:,.2f}"
            })
        return transactions
    finally:
        db.close()

def get_category_breakdown(user_id):
    """
    Aggregate total amount spent per category for the given user_id.
    Returns a list of dicts: {"name": "Category", "total": "₹ X,XXX.XX", "percentage": X}.
    """
    db = get_db()
    try:
        cursor = db.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        if not rows:
            return []

        total_spending = sum(row['total'] for row in rows)
        if total_spending == 0:
            return []

        results = []
        percentages = []

        for row in rows:
            pct = round((row['total'] / total_spending) * 100)
            percentages.append(pct)
            results.append({
                "name": row['category'],
                "total": row['total'],
                "percentage": pct
            })

        # Adjust for rounding errors to ensure sum is exactly 100
        diff = 100 - sum(percentages)
        if diff != 0:
            # Adjust the largest category (first in the list since it's ORDER BY total DESC)
            results[0]["percentage"] += diff

        # Format the totals with currency symbol and formatting
        for res in results:
            res["total"] = f"₹ {res['total']:,.2f}"

        return results
    finally:
        db.close()
