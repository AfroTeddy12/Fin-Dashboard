# Financial Dashboard

A comprehensive financial dashboard built with Python (Flask) and JavaScript to help you track your income, expenses, budgets, and financial goals.

## Features

### 📊 **Financial Tracking**
- **Income & Expense Management**: Add and categorize all your financial transactions
- **Real-time Analytics**: View your financial summary with total income, expenses, and net income
- **Transaction History**: Keep track of all your past transactions with detailed information

### 💰 **Budget Management**
- **Category-based Budgets**: Set monthly budgets for different spending categories
- **Budget Progress Tracking**: Visual progress bars show how much you've spent vs. your budget
- **Budget Alerts**: Color-coded indicators (green/yellow/red) based on spending progress

### 🎯 **Financial Goals**
- **Goal Setting**: Create financial goals with target amounts and deadlines
- **Progress Tracking**: Monitor your progress towards each goal with visual progress bars
- **Goal Updates**: Easily update your current savings amount for each goal

### 📈 **Data Visualization**
- **Income vs Expenses Chart**: 6-month comparison of your income and expenses
- **Category Breakdown**: Pie chart showing your spending distribution across categories
- **Interactive Charts**: Responsive charts that update automatically with your data

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Beautiful Interface**: Modern, clean design with smooth animations and hover effects
- **User-friendly**: Intuitive navigation and easy-to-use forms

## Technology Stack

- **Backend**: Python Flask with SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite (file-based, no setup required)
- **Charts**: Chart.js for data visualization
- **UI Framework**: Bootstrap 5 for responsive design
- **Icons**: Font Awesome for beautiful icons

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone or Download
Download the project files to your local machine.

### Step 2: Install Dependencies
Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
Start the Flask development server:

```bash
python app.py
```

### Step 4: Access the Dashboard
Open your web browser and navigate to:
```
http://localhost:5000
```

## How to Use

### Adding Transactions
1. Click the "Add Transaction" button in the sidebar
2. Fill in the transaction details:
   - **Description**: What the transaction was for
   - **Amount**: The dollar amount
   - **Category**: Select from predefined categories
   - **Type**: Choose "Income" or "Expense"
   - **Date**: When the transaction occurred
3. Click "Add Transaction"

### Setting Budgets
1. Click the "Set Budget" button in the sidebar
2. Choose a category and set your monthly budget amount
3. Select the month for the budget
4. Click "Set Budget"

### Creating Financial Goals
1. Click the "Add Goal" button in the sidebar
2. Enter your goal details:
   - **Goal Name**: What you're saving for
   - **Target Amount**: How much you want to save
   - **Current Amount**: How much you've saved so far
   - **Deadline**: When you want to reach your goal
3. Click "Add Goal"

### Updating Goal Progress
1. Find your goal in the "Financial Goals" section
2. Click the "Update" button
3. Enter your current saved amount
4. The progress bar will automatically update

## File Structure

```
Findashboard/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
└── static/
    └── js/
        └── dashboard.js  # JavaScript functionality
```

## API Endpoints

The application provides the following REST API endpoints:

### Transactions
- `GET /api/transactions` - Get all transactions
- `POST /api/transactions` - Add a new transaction
- `DELETE /api/transactions/<id>` - Delete a transaction

### Budgets
- `GET /api/budgets` - Get current month budgets
- `POST /api/budgets` - Add a new budget

### Goals
- `GET /api/goals` - Get all financial goals
- `POST /api/goals` - Add a new goal
- `PUT /api/goals/<id>` - Update goal progress

### Analytics
- `GET /api/analytics/summary` - Get financial summary
- `GET /api/analytics/chart-data` - Get chart data

## Database Schema

The application uses SQLite with three main tables:

### Transactions
- `id`: Primary key
- `description`: Transaction description
- `amount`: Transaction amount
- `category`: Spending category
- `transaction_type`: 'income' or 'expense'
- `date`: Transaction date
- `created_at`: Timestamp

### Budgets
- `id`: Primary key
- `category`: Budget category
- `amount`: Budget amount
- `month`: Month (YYYY-MM format)
- `created_at`: Timestamp

### Goals
- `id`: Primary key
- `name`: Goal name
- `target_amount`: Target savings amount
- `current_amount`: Current savings amount
- `deadline`: Goal deadline
- `created_at`: Timestamp

## Customization

### Adding New Categories
To add new spending categories, edit the select options in `templates/index.html` in both the transaction and budget forms.

### Changing Colors
The color scheme can be customized by modifying the CSS variables in the `<style>` section of `templates/index.html`.

### Database Location
The SQLite database file (`finance.db`) is automatically created in the project root directory when you first run the application.

## Troubleshooting

### Common Issues

1. **Port already in use**: If you get an error about port 5000 being in use, the application will automatically try port 5001.

2. **Database errors**: If you encounter database issues, delete the `finance.db` file and restart the application to create a fresh database.

3. **Charts not loading**: Make sure you have an internet connection as Chart.js is loaded from a CDN.

### Getting Help
If you encounter any issues:
1. Check the browser console for JavaScript errors
2. Check the terminal/command prompt for Python errors
3. Ensure all dependencies are installed correctly

## Future Enhancements

Potential features for future versions:
- User authentication and multiple user support
- Export data to CSV/PDF
- Recurring transactions
- Bill reminders
- Investment tracking
- Debt management
- Mobile app version

## License

This project is open source and available under the MIT License.

---

**Happy budgeting! 💰📊** 
