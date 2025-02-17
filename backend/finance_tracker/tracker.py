from backend.database import (
    create_user, get_user_by_email,
    add_expense, add_income, get_financial_report, verify_password
)

class FinanceTracker:
    def __init__(self):
        self.current_user_id = None

    def register(self, email, password, name, DOB, username = None):
        if not create_user(email, password, name, DOB, username):
            return "❌Email or username already exists"
        return "✅Registeration successful"

    def login(self, identifier, password):
        user = get_user_by_email(identifier)
        if user and verify_password(password, user[3]):
            self.current_user_id = user[0]
            return "✅Login successful"
        return "❌Invalid credentials"

    def add_expense(self, category, amount):
        if not self.current_user_id:
            return "❌Not logged in"
        add_expense(self.current_user_id, category, amount)

    def add_income(self, source, amount):
        if not self.current_user_id:
            return "❌Not logged in"
        add_income(self.current_user_id, source, amount)
        return "✅Income added"

    def view_report(self):
        if not self.current_user_id:
            return None
        return get_financial_report(self.current_user_id)