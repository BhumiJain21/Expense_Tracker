from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))  # 'expense' or 'income'
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.type} {self.amount}>'

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), unique=True)
    amount = db.Column(db.Float)
    alert_threshold = db.Column(db.Float, default=0.8)

    def check_alert(self, current_spend):
        return current_spend >= (self.amount * 0.8)  # Alert at 80% of budget
    def __repr__(self):
        return f'<Budget {self.category} {self.amount}>'