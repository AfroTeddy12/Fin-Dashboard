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
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(7), nullable=False)  # YYYY-MM format
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
        'date': t.date.strftime('%Y-%m-%d')
    } for t in transactions])

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    transaction = Transaction(
        description=data['description'],
        amount=float(data['amount']),
        category=data['category'],
        transaction_type=data['transaction_type'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date()
    )
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction added successfully', 'id': transaction.id})

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
    
    transactions = Transaction.query.filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    net_income = total_income - total_expenses
    
    # Category breakdown
    category_expenses = {}
    for t in transactions:
        if t.transaction_type == 'expense':
            category_expenses[t.category] = category_expenses.get(t.category, 0) + t.amount
    
    return jsonify({
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'category_expenses': category_expenses,
        'current_month': current_month
    })

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 