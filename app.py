from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model and login manager loader must be defined after initializing login_manager
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=True)  # Add this line
    otp = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), unique=True)
    amount = db.Column(db.Float)
    alert_threshold = db.Column(db.Float, default=0.8)

    def check_alert(self, current_spend):
        return current_spend >= (self.amount * self.alert_threshold)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return self.name

def add_default_categories():
    default_categories = [
        'Salary', 'Freelance', 'Investment', 'Food', 'Transportation', 
        'Utilities', 'Rent', 'Entertainment', 'Shopping', 'Healthcare', 
        'Education', 'Insurance', 'Savings', 'Other'
    ]
    with app.app_context():
        for category_name in default_categories:
            if not Category.query.filter_by(name=category_name).first():
                category = Category(name=category_name)
                db.session.add(category)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

@app.route('/')
@login_required
def index():
    two_months_ago = datetime.now() - timedelta(days=60)
    transactions = Transaction.query.filter(
        Transaction.date >= two_months_ago
    ).order_by(Transaction.date.desc()).all()
    
    budgets = Budget.query.all()
    categories = Category.query.all()
    
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expenses
    
    category_expenses = {}
    for transaction in transactions:
        if transaction.type == 'expense':
            if transaction.category not in category_expenses:
                category_expenses[transaction.category] = 0
            category_expenses[transaction.category] += transaction.amount
    
    budget_alerts = []
    for budget in budgets:
        current_spend = category_expenses.get(budget.category, 0)
        if budget.check_alert(current_spend):
            budget_alerts.append({
                'category': budget.category,
                'budget': budget.amount,
                'spent': current_spend
            })
    
    return render_template('index.html', 
                         transactions=transactions, 
                         budgets=budgets,
                         categories=categories,
                         balance=balance,
                         total_income=total_income,
                         total_expenses=total_expenses,
                         budget_alerts=budget_alerts)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        transaction_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        if transaction_date > datetime.now():
            flash('Cannot add future transactions!', 'error')
            return redirect(url_for('index'))
            
        transaction = Transaction(
            type=request.form['type'],
            amount=float(request.form['amount']),
            category=request.form['category'],
            description=request.form['description'],
            date=transaction_date
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
    except ValueError:
        flash('Invalid date format!', 'error')
    except:
        flash('Error adding transaction!', 'error')
    return redirect(url_for('index'))

@app.route('/add_category', methods=['POST'])
def add_category():
    try:
        category_name = request.form['category_name']
        if not Category.query.filter_by(name=category_name).first():
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
        else:
            flash('Category already exists!', 'error')
    except:
        flash('Error adding category!', 'error')
    return redirect(url_for('index'))

@app.route('/add_budget', methods=['POST'])
def add_budget():
    try:
        existing_budget = Budget.query.filter_by(category=request.form['category']).first()
        if existing_budget:
            existing_budget.amount = float(request.form['amount'])
            db.session.commit()
            flash('Budget updated successfully!', 'success')
        else:
            budget = Budget(
                category=request.form['category'],
                amount=float(request.form['amount']),
                alert_threshold=0.8
            )
            db.session.add(budget)
            db.session.commit()
            flash('Budget added successfully!', 'success')
    except:
        flash('Error adding budget!', 'error')
    return redirect(url_for('index'))

@app.route('/delete_transaction/<int:id>')
def delete_transaction(id):
    try:
        transaction = Transaction.query.get(id)
        if transaction:
            db.session.delete(transaction)
            db.session.commit()
            flash('Transaction deleted successfully!', 'success')
        else:
            flash('Transaction not found!', 'error')
    except:
        flash('Error deleting transaction!', 'error')
    return redirect(url_for('index'))

@app.route('/monthly_summary')
def monthly_summary():
    start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    monthly_transactions = Transaction.query.filter(
        Transaction.date.between(start_date, end_date)
    ).order_by(Transaction.date.desc()).all()
    
    # Category-wise expenses
    category_expenses = {}
    # Date-wise expenses
    date_expenses = {}
    
    for transaction in monthly_transactions:
        if transaction.type == 'expense':
            # Add to category expenses
            if transaction.category not in category_expenses:
                category_expenses[transaction.category] = 0
            category_expenses[transaction.category] += transaction.amount
            
            # Add to date expenses
            transaction_date = transaction.date.date()
            if transaction_date not in date_expenses:
                date_expenses[transaction_date] = {}
            if transaction.category not in date_expenses[transaction_date]:
                date_expenses[transaction_date][transaction.category] = 0
            date_expenses[transaction_date][transaction.category] += transaction.amount
    
    # Sort date_expenses by date
    date_expenses = dict(sorted(date_expenses.items(), reverse=True))
    
    budget_alerts = []
    budgets = Budget.query.all()
    for budget in budgets:
        current_spend = category_expenses.get(budget.category, 0)
        if budget.check_alert(current_spend):
            budget_alerts.append({
                'category': budget.category,
                'budget': budget.amount,
                'spent': current_spend
            })
    
    return render_template('monthly_summary.html',
                         category_expenses=category_expenses,
                         date_expenses=date_expenses,
                         budget_alerts=budget_alerts,
                         month=start_date.strftime('%B %Y'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(email=email)
            db.session.add(user)
        
        # Generate and store OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        user.otp = otp
        user.otp_expiry = datetime.now() + timedelta(minutes=5)
        db.session.commit()
        
        # Send OTP via email
        try:
            send_otp_email(email, otp)
            flash('OTP sent to your email!', 'success')
            return render_template('login.html', email_submitted=True, email=email, username=username)
        except Exception as e:
            flash('Error sending OTP. Please try again.', 'error')
            print(f"Email error: {str(e)}")  # For debugging
            
    return render_template('login.html', email_submitted=False)

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    email = request.form['email']
    entered_otp = request.form['otp']
    user = User.query.filter_by(email=email).first()
    
    if user and user.otp == entered_otp and user.otp_expiry > datetime.now():
        login_user(user)
        user.otp = None  # Clear OTP after successful verification
        user.otp_expiry = None
        db.session.commit()
        flash('Login successful!', 'success')
        return redirect(url_for('index'))
    else:
        if not user:
            flash('User not found!', 'error')
        elif user.otp_expiry <= datetime.now():
            flash('OTP has expired! Please request a new one.', 'error')
        else:
            flash('Invalid OTP! Please try again.', 'error')
        return redirect(url_for('login'))

def send_otp_email(email, otp):
    sender_email = "bhumijain7533@gmail.com"  # Replace with your email
    sender_password = "jxdwlokcqmkjruew"   # Replace with your app password
    
    msg = MIMEText(f'Your OTP for Expense Tracker login is: {otp}\nThis OTP will expire in 5 minutes.')
    msg['Subject'] = 'Expense Tracker Login OTP'
    msg['From'] = sender_email
    msg['To'] = email
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"OTP sent: {otp}")  # For debugging
            return True
    except Exception as e:
        print(f"Email error: {str(e)}")  # For debugging
        return False

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# Move this to the end of the file
if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        add_default_categories()
    app.run(debug=True)