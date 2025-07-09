// Global variables
let incomeExpenseChart;
let categoryChart;
let transactions = [];
let budgets = [];
let goals = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    setCurrentDate();
    loadDashboard();
    setDefaultDates();
});

// Set current date in navbar
function setCurrentDate() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('current-date').textContent = now.toLocaleDateString('en-US', options);
}

// Set default dates in forms
function setDefaultDates() {
    const today = new Date().toISOString().split('T')[0];
    const currentMonth = new Date().toISOString().slice(0, 7);
    
    document.getElementById('transactionDate').value = today;
    document.getElementById('budgetMonth').value = currentMonth;
    document.getElementById('goalDeadline').value = today;
}

// Load all dashboard data
async function loadDashboard() {
    try {
        await Promise.all([
            loadTransactions(),
            loadBudgets(),
            loadGoals(),
            loadSummary(),
            loadChartData()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showAlert('Error loading dashboard data', 'danger');
    }
}

// Load transactions
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        transactions = await response.json();
        displayRecentTransactions();
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

// Load budgets
async function loadBudgets() {
    try {
        const response = await fetch('/api/budgets');
        budgets = await response.json();
        displayBudgets();
    } catch (error) {
        console.error('Error loading budgets:', error);
    }
}

// Load goals
async function loadGoals() {
    try {
        const response = await fetch('/api/goals');
        goals = await response.json();
        displayGoals();
    } catch (error) {
        console.error('Error loading goals:', error);
    }
}

// Load summary data
async function loadSummary() {
    try {
        const response = await fetch('/api/analytics/summary');
        const summary = await response.json();
        
        document.getElementById('total-income').textContent = formatCurrency(summary.total_income);
        document.getElementById('total-expenses').textContent = formatCurrency(summary.total_expenses);
        document.getElementById('net-income').textContent = formatCurrency(summary.net_income);
        
        // Update net income color based on value
        const netIncomeElement = document.getElementById('net-income');
        if (summary.net_income >= 0) {
            netIncomeElement.className = 'card-title text-success mb-0';
        } else {
            netIncomeElement.className = 'card-title text-danger mb-0';
        }
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Load chart data
async function loadChartData() {
    try {
        const response = await fetch('/api/analytics/chart-data');
        const chartData = await response.json();
        createCharts(chartData);
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

// Create charts
function createCharts(chartData) {
    // Income vs Expenses Chart
    const incomeExpenseCtx = document.getElementById('incomeExpenseChart').getContext('2d');
    incomeExpenseChart = new Chart(incomeExpenseCtx, {
        type: 'bar',
        data: {
            labels: chartData.months,
            datasets: [
                {
                    label: 'Income',
                    data: chartData.income,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Expenses',
                    data: chartData.expenses,
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });

    // Category Chart
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    const categoryData = getCategoryData();
    
    categoryChart = new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: categoryData.labels,
            datasets: [{
                data: categoryData.values,
                backgroundColor: [
                    '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
                    '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Get category data for pie chart
function getCategoryData() {
    const categoryExpenses = {};
    
    transactions.forEach(transaction => {
        if (transaction.transaction_type === 'expense') {
            categoryExpenses[transaction.category] = 
                (categoryExpenses[transaction.category] || 0) + transaction.amount;
        }
    });
    
    return {
        labels: Object.keys(categoryExpenses),
        values: Object.values(categoryExpenses)
    };
}

// Display recent transactions
function displayRecentTransactions() {
    const container = document.getElementById('recent-transactions');
    const recentTransactions = transactions.slice(0, 5);
    
    if (recentTransactions.length === 0) {
        container.innerHTML = '<p class="text-muted">No transactions yet</p>';
        return;
    }
    
    container.innerHTML = recentTransactions.map(transaction => `
        <div class="transaction-item ${transaction.transaction_type === 'income' ? 'transaction-income' : 'transaction-expense'}">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="mb-1">${transaction.description}</h6>
                    <small class="text-muted">${transaction.category} • ${formatDate(transaction.date)}</small>
                </div>
                <div class="text-end">
                    <span class="fw-bold ${transaction.transaction_type === 'income' ? 'text-success' : 'text-danger'}">
                        ${transaction.transaction_type === 'income' ? '+' : '-'}${formatCurrency(transaction.amount)}
                    </span>
                </div>
            </div>
        </div>
    `).join('');
}

// Display budgets
function displayBudgets() {
    const container = document.getElementById('budget-list');
    
    if (budgets.length === 0) {
        container.innerHTML = '<p class="text-muted">No budgets set for this month</p>';
        return;
    }
    
    container.innerHTML = budgets.map(budget => {
        const spent = getCategorySpent(budget.category);
        const percentage = (spent / budget.amount) * 100;
        const statusClass = percentage > 100 ? 'danger' : percentage > 80 ? 'warning' : 'success';
        
        return `
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0">${budget.category}</h6>
                    <span class="text-muted">${formatCurrency(spent)} / ${formatCurrency(budget.amount)}</span>
                </div>
                <div class="progress">
                    <div class="progress-bar bg-${statusClass}" style="width: ${Math.min(percentage, 100)}%"></div>
                </div>
                <small class="text-muted">${percentage.toFixed(1)}% used</small>
            </div>
        `;
    }).join('');
}

// Display goals
function displayGoals() {
    const container = document.getElementById('goals-list');
    
    if (goals.length === 0) {
        container.innerHTML = '<p class="text-muted">No financial goals set</p>';
        return;
    }
    
    container.innerHTML = goals.map(goal => {
        const progress = (goal.current_amount / goal.target_amount) * 100;
        const daysLeft = Math.ceil((new Date(goal.deadline) - new Date()) / (1000 * 60 * 60 * 24));
        
        return `
            <div class="card goal-card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">${goal.name}</h6>
                        <button class="btn btn-sm btn-outline-primary" onclick="updateGoalProgress(${goal.id})">
                            Update
                        </button>
                    </div>
                    <div class="mb-2">
                        <span class="text-muted">${formatCurrency(goal.current_amount)} / ${formatCurrency(goal.target_amount)}</span>
                    </div>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-warning" style="width: ${Math.min(progress, 100)}%"></div>
                    </div>
                    <div class="d-flex justify-content-between">
                        <small class="text-muted">${progress.toFixed(1)}% complete</small>
                        <small class="text-muted">${daysLeft} days left</small>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Add transaction
async function addTransaction() {
    const form = document.getElementById('transactionForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const transactionData = {
        description: document.getElementById('transactionDescription').value,
        amount: parseFloat(document.getElementById('transactionAmount').value),
        category: document.getElementById('transactionCategory').value,
        transaction_type: document.getElementById('transactionType').value,
        date: document.getElementById('transactionDate').value
    };
    
    try {
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transactionData)
        });
        
        if (response.ok) {
            showAlert('Transaction added successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('transactionModal')).hide();
            form.reset();
            setDefaultDates();
            loadDashboard();
        } else {
            throw new Error('Failed to add transaction');
        }
    } catch (error) {
        console.error('Error adding transaction:', error);
        showAlert('Error adding transaction', 'danger');
    }
}

// Add budget
async function addBudget() {
    const form = document.getElementById('budgetForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const budgetData = {
        category: document.getElementById('budgetCategory').value,
        amount: parseFloat(document.getElementById('budgetAmount').value),
        month: document.getElementById('budgetMonth').value
    };
    
    try {
        const response = await fetch('/api/budgets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(budgetData)
        });
        
        if (response.ok) {
            showAlert('Budget set successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('budgetModal')).hide();
            form.reset();
            setDefaultDates();
            loadDashboard();
        } else {
            throw new Error('Failed to set budget');
        }
    } catch (error) {
        console.error('Error setting budget:', error);
        showAlert('Error setting budget', 'danger');
    }
}

// Add goal
async function addGoal() {
    const form = document.getElementById('goalForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const goalData = {
        name: document.getElementById('goalName').value,
        target_amount: parseFloat(document.getElementById('goalTargetAmount').value),
        current_amount: parseFloat(document.getElementById('goalCurrentAmount').value),
        deadline: document.getElementById('goalDeadline').value
    };
    
    try {
        const response = await fetch('/api/goals', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(goalData)
        });
        
        if (response.ok) {
            showAlert('Goal added successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('goalModal')).hide();
            form.reset();
            setDefaultDates();
            loadDashboard();
        } else {
            throw new Error('Failed to add goal');
        }
    } catch (error) {
        console.error('Error adding goal:', error);
        showAlert('Error adding goal', 'danger');
    }
}

// Update goal progress
async function updateGoalProgress(goalId) {
    const currentAmount = prompt('Enter current amount saved:');
    if (currentAmount === null || currentAmount === '') return;
    
    try {
        const response = await fetch(`/api/goals/${goalId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_amount: parseFloat(currentAmount)
            })
        });
        
        if (response.ok) {
            showAlert('Goal progress updated!', 'success');
            loadDashboard();
        } else {
            throw new Error('Failed to update goal');
        }
    } catch (error) {
        console.error('Error updating goal:', error);
        showAlert('Error updating goal', 'danger');
    }
}

// Get amount spent in a category for current month
function getCategorySpent(category) {
    const currentMonth = new Date().toISOString().slice(0, 7);
    return transactions
        .filter(t => t.category === category && 
                    t.transaction_type === 'expense' && 
                    t.date.startsWith(currentMonth))
        .reduce((sum, t) => sum + t.amount, 0);
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
    });
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
} 