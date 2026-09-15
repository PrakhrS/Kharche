import pytest
from app import app as flask_app
from database.db import init_db, get_db
from datetime import datetime, timedelta

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    # Register
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    # Login
    client.post('/login', data={'email': 'test@example.com', 'password': 'password123'})
    return client

def seed_expenses(user_id, expenses):
    """
    Helper to seed expenses.
    expenses: list of tuples (amount, category, date, description)
    """
    db = get_db()
    for exp in expenses:
        db.execute(
            'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
            (user_id, *exp)
        )
    db.commit()
    db.close()

class TestProfileDateFilter:

    def test_profile_auth_guard(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_profile_all_time_default(self, auth_client):
        """By default, all expenses should be shown."""
        # Get user_id from session
        with auth_client.session_transaction() as session:
            user_id = session['user_id']

        seed_expenses(user_id, [
            (100.0, 'Food', '2026-01-01', 'Jan Lunch'),
            (200.0, 'Transport', '2026-02-01', 'Feb Cab'),
            (300.0, 'Bills', '2026-03-01', 'Mar Electric'),
        ])

        response = auth_client.get('/profile')
        assert response.status_code == 200
        assert '₹ 600.00' in response.get_data(as_text=True)
        assert 'Jan Lunch' in response.get_data(as_text=True)
        assert 'Feb Cab' in response.get_data(as_text=True)
        assert 'Mar Electric' in response.get_data(as_text=True)

    def test_profile_valid_date_range(self, auth_client):
        """Expenses should be filtered by valid date range."""
        with auth_client.session_transaction() as session:
            user_id = session['user_id']

        seed_expenses(user_id, [
            (100.0, 'Food', '2026-01-01', 'Too Early'),
            (200.0, 'Transport', '2026-02-01', 'Just Right'),
            (300.0, 'Bills', '2026-03-01', 'Too Late'),
        ])

        # Filter for February
        response = auth_client.get('/profile?date_from=2026-01-15&date_to=2026-02-15')
        assert response.status_code == 200
        assert '₹ 200.00' in response.get_data(as_text=True)
        assert 'Just Right' in response.get_data(as_text=True)
        assert 'Too Early' not in response.get_data(as_text=True)
        assert 'Too Late' not in response.get_data(as_text=True)

    def test_profile_empty_range(self, auth_client):
        """A range with no expenses should show zeroed stats."""
        with auth_client.session_transaction() as session:
            user_id = session['user_id']

        seed_expenses(user_id, [(100.0, 'Food', '2026-01-01', 'Jan Lunch')])

        # Range in the future
        response = auth_client.get('/profile?date_from=2027-01-01&date_to=2027-01-31')
        assert response.status_code == 200
        assert '₹ 0.00' in response.get_data(as_text=True)
        assert 'Jan Lunch' not in response.get_data(as_text=True)

    def test_profile_preset_simulation_this_month(self, auth_client):
        """Simulate 'This Month' preset range."""
        with auth_client.session_transaction() as session:
            user_id = session['user_id']

        today = datetime.now()
        this_month_start = today.replace(day=1).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        last_month_date = (today - timedelta(days=40)).strftime('%Y-%m-%d')

        seed_expenses(user_id, [
            (50.0, 'Food', this_month_start, 'Current Month'),
            (100.0, 'Bills', last_month_date, 'Past Month'),
        ])

        response = auth_client.get(f'/profile?date_from={this_month_start}&date_to={today_str}')
        assert '₹ 50.00' in response.get_data(as_text=True)
        assert 'Current Month' in response.get_data(as_text=True)
        assert 'Past Month' not in response.get_data(as_text=True)

    def test_profile_invalid_range_start_after_end(self, auth_client):
        """If date_from > date_to, flash error and show all data."""
        with auth_client.session_transaction() as session:
            user_id = session['user_id']

        seed_expenses(user_id, [(100.0, 'Food', '2026-01-01', 'Expense 1')])

        # Start date AFTER end date
        response = auth_client.get('/profile?date_from=2026-12-31&date_to=2026-01-01')

        # Verify flash message
        assert 'Start date must be before end date.' in response.get_data(as_text=True)
        # Verify fallback to all data
        assert 'Expense 1' in response.get_data(as_text=True)
        assert '₹ 100.00' in response.get_data(as_text=True)

    def test_profile_malformed_date(self, auth_client):
        """Malformed dates should be ignored, showing all data."""
        with auth_client.session_transaction() as session:
            user_id = session['user_id']

        seed_expenses(user_id, [(100.0, 'Food', '2026-01-01', 'Expense 1')])

        # One malformed, one valid
        response = auth_client.get('/profile?date_from=not-a-date&date_to=2026-12-31')

        assert response.status_code == 200
        # Since date_from is invalid, it's treated as None, showing all expenses up to 2026-12-31
        assert 'Expense 1' in response.get_data(as_text=True)
        assert '₹ 100.00' in response.get_data(as_text=True)

    def test_profile_invalid_both_dates(self, auth_client):
        """Both dates malformed should show all data."""
        with auth_client.session_transaction() as session:
            user_id = session['user_id']

        seed_expenses(user_id, [(100.0, 'Food', '2026-01-01', 'Expense 1')])

        response = auth_client.get('/profile?date_from=abc&date_to=xyz')

        assert response.status_code == 200
        assert 'Expense 1' in response.get_data(as_text=True)
        assert '₹ 100.00' in response.get_data(as_text=True)
