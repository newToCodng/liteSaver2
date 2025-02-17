import sqlite3
from contextlib import contextmanager
from datetime import datetime
import bcrypt

DATABASE_NAME = "finance.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
    finally:
        conn.close()

def initialize_database():
    with get_db() as conn:
        cursor = conn.cursor()
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            DOB DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Expenses Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        # Income Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        source TEXT NOT NULL,
        amount REAL NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        conn.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# User Operations
def create_user(email, password, name, DOB, username = None):
    # Ensure the DOB is in 'YYYY-MM-DD' format
    if isinstance(DOB, str):
        try:
            DOB = datetime.strptime(DOB, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD format.")

    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO users (email, username, password, name, DOB)
            VALUES (?, ?, ?, ?, ?)    
            ''', (email, username, hash_password(password), name, DOB))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_user_by_email(email):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone()

# Transaction Operations
def add_expense(user_id, category, amount):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (user_id, category, amount)
            VALUES (?, ?, ?)
        ''', (user_id, category, amount))
        conn.commit()

def add_income(user_id, source, amount):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO income (user_id, source, amount)
            VALUES (?, ?, ?)
        ''', (user_id, source, amount))
        conn.commit()

# Report Generation
def get_financial_report(user_id):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            # Total Income
            cursor.execute('SELECT SUM(amount) FROM income WHERE user_id = ?', (user_id,))
            total_income = cursor.fetchone()[0] or 0.0

            #Total Expenses
            cursor.execute('SELECT SUM(amount) FROM expenses WHERE user_id = ?', (user_id))
            total_expenses = cursor.fetchone()[0] or 0.0

            # Categories
            cursor.execute('''
                SELECT category, SUM(amount)
                FROM expenses
                WHERE user_id = ?
                GROUP BY category
            ''', (user_id,))
            categories = dict(cursor.fetchall())

            return {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "category_breakdown": categories,
                "net_balance": total_income - total_expenses
            }
    except Exception as e:
        print(f"Error occured: {e}")
        return "❌Error while generating report"

