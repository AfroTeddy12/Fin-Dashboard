from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

# Database Models
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(7), nullable=False)  # YYYY-MM format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # 'checking', 'savings', 'investment'
    balance = db.Column(db.Float, default=0.0)
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color for UI
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Transaction routes
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return jsonify([{
        'id': t.id,
        'description': t.description,
        'amount': t.amount,
        'category': t.category,
        'transaction_type': t.transaction_type,
        'account_id': t.account_id,
        'account_name': Account.query.get(t.account_id).name if Account.query.get(t.account_id) else 'Unknown',
        'date': t.date.strftime('%Y-%m-%d')
    } for t in transactions])

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        print(f"Adding transaction with data: {data}")
        
        transaction = Transaction(
            description=data['description'],
            amount=float(data['amount']),
            category=data['category'],
            transaction_type=data['transaction_type'],
            account_id=int(data['account_id']),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        )
        
        print(f"Created transaction object: {transaction.description}, {transaction.amount}, {transaction.date}")
        
        # Add transaction to session
        db.session.add(transaction)
        
        # Update account balance
        account = Account.query.get(transaction.account_id)
        if account:
            if transaction.transaction_type == 'income':
                account.balance += transaction.amount
            else:
                account.balance -= transaction.amount
            print(f"Updated account {account.name} balance to {account.balance}")
        
        # Commit the transaction
        db.session.commit()
        print(f"Transaction committed successfully with ID: {transaction.id}")
        
        return jsonify({'message': 'Transaction added successfully', 'id': transaction.id})
    except Exception as e:
        print(f"Error adding transaction: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted successfully'})

# Budget routes
@app.route('/api/budgets', methods=['GET'])
def get_budgets():
    current_month = date.today().strftime('%Y-%m')
    budgets = Budget.query.filter_by(month=current_month).all()
    return jsonify([{
        'id': b.id,
        'category': b.category,
        'amount': b.amount,
        'month': b.month
    } for b in budgets])

@app.route('/api/budgets', methods=['POST'])
def add_budget():
    data = request.json
    budget = Budget(
        category=data['category'],
        amount=float(data['amount']),
        month=data['month']
    )
    db.session.add(budget)
    db.session.commit()
    return jsonify({'message': 'Budget added successfully', 'id': budget.id})

# Account routes
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    accounts = Account.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'account_type': a.account_type,
        'balance': a.balance,
        'color': a.color
    } for a in accounts])

@app.route('/api/accounts', methods=['POST'])
def add_account():
    data = request.json
    account = Account(
        name=data['name'],
        account_type=data['account_type'],
        color=data.get('color', '#3B82F6')
    )
    db.session.add(account)
    db.session.commit()
    return jsonify({'message': 'Account added successfully', 'id': account.id})

@app.route('/api/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    account = Account.query.get_or_404(account_id)
    data = request.json
    
    if 'name' in data:
        account.name = data['name']
    if 'account_type' in data:
        account.account_type = data['account_type']
    if 'color' in data:
        account.color = data['color']
    if 'balance' in data:
        account.balance = float(data['balance'])
    
    db.session.commit()
    return jsonify({'message': 'Account updated successfully'})

@app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    account.is_active = False
    db.session.commit()
    return jsonify({'message': 'Account deleted successfully'})

# Goal routes
@app.route('/api/goals', methods=['GET'])
def get_goals():
    goals = Goal.query.all()
    return jsonify([{
        'id': g.id,
        'name': g.name,
        'target_amount': g.target_amount,
        'current_amount': g.current_amount,
        'deadline': g.deadline.strftime('%Y-%m-%d'),
        'progress': (g.current_amount / g.target_amount * 100) if g.target_amount > 0 else 0
    } for g in goals])

@app.route('/api/goals', methods=['POST'])
def add_goal():
    data = request.json
    goal = Goal(
        name=data['name'],
        target_amount=float(data['target_amount']),
        deadline=datetime.strptime(data['deadline'], '%Y-%m-%d').date()
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify({'message': 'Goal added successfully', 'id': goal.id})

@app.route('/api/goals/<int:goal_id>', methods=['PUT'])
def update_goal_progress(goal_id):
    data = request.json
    goal = Goal.query.get_or_404(goal_id)
    goal.current_amount = float(data['current_amount'])
    db.session.commit()
    return jsonify({'message': 'Goal progress updated successfully'})

# Analytics routes
@app.route('/api/analytics/summary')
def get_summary():
    current_month = date.today().strftime('%Y-%m')
    
    # Get transactions for current month
    start_date = datetime.strptime(f"{current_month}-01", '%Y-%m-%d').date()
    end_date = date.today()
    
    print(f"Filtering transactions from {start_date} to {end_date}")
    
    transactions = Transaction.query.filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    # Debug: Print all transactions to see what's in the database
    all_transactions = Transaction.query.all()
    print(f"All transactions in database: {len(all_transactions)}")
    for t in all_transactions:
        print(f"Transaction: {t.description}, Amount: {t.amount}, Date: {t.date}, Type: {t.transaction_type}")
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    net_income = total_income - total_expenses
    
    # Category breakdown
    category_expenses = {}
    for t in transactions:
        if t.transaction_type == 'expense':
            category_expenses[t.category] = category_expenses.get(t.category, 0) + t.amount
    
    summary_data = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'category_expenses': category_expenses,
        'current_month': current_month
    }
    
    print(f"Summary API called - Transactions found: {len(transactions)}")
    print(f"Summary data: {summary_data}")
    
    return jsonify(summary_data)

@app.route('/api/analytics/chart-data')
def get_chart_data():
    # Get last 6 months of data
    months = []
    income_data = []
    expense_data = []
    
    for i in range(5, -1, -1):
        target_date = date.today().replace(day=1)
        for _ in range(i):
            if target_date.month == 1:
                target_date = target_date.replace(year=target_date.year - 1, month=12)
            else:
                target_date = target_date.replace(month=target_date.month - 1)
        
        month_str = target_date.strftime('%Y-%m')
        months.append(target_date.strftime('%B %Y'))
        
        start_date = target_date
        if target_date.month == 12:
            end_date = target_date.replace(year=target_date.year + 1, month=1) - date.resolution
        else:
            end_date = target_date.replace(month=target_date.month + 1) - date.resolution
        
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        month_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
        month_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
        
        income_data.append(month_income)
        expense_data.append(month_expenses)
    
    return jsonify({
        'months': months,
        'income': income_data,
        'expenses': expense_data
    })

# Data management routes
@app.route('/api/data/wipe', methods=['DELETE'])
def wipe_all_data():
    try:
        # Delete all data from all tables
        Transaction.query.delete()
        Budget.query.delete()
        Goal.query.delete()
        # Reset account balances to 0 instead of deleting accounts
        accounts = Account.query.all()
        for account in accounts:
            account.balance = 0.0
        db.session.commit()
        return jsonify({'message': 'All data has been wiped successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to wipe data'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 