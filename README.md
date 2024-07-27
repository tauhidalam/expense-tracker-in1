# Personal Finance Management System

## Overview

The Personal Finance Management System is a Flask-based web application that allows users to manage their finances by tracking expenses, income, credit cards, and funds. Users can view their financial status through dashboards, generate visual reports, and interact with various financial elements through a user-friendly interface.

## Features

- **User Authentication:**
  - User registration, login, and password reset functionalities.
  - User-specific data handling for security.

- **Expense Management:**
  - Add, view, and delete expenses.
  - Categorize expenses by type and source.
  - Track expenses using credit cards and funds.
  
- **Income Management:**
  - Add and view income entries.
  
- **Credit Card Management:**
  - Add, view, and delete credit cards.
  - Track credit card usage and outstanding balances.
  - Reset outstanding balances and available limits.

- **Fund Management:**
  - Add, view, and manage funds.
  - Track fund allocation and usage.

- **Dashboard:**
  - View summary of income, expenses, and funds.
  - Monitor available balance and credit card outstanding amounts.

- **Reports and Visualizations:**
  - Generate pie charts for expense categories, spend sources, credit card outstandings, and fund allocations.

- **Mobile Optimization:**
  - Enhanced mobile view with responsive design and interactive pop-ups for financial data.

## Installation

### Prerequisites

- Python 3.6 or higher
- Flask
- Flask-WTF
- Flask-SQLAlchemy
- Flask-Login
- Flask-Migrate
- SQLAlchemy
- Matplotlib
- Seaborn
- Pandas
- PostgreSQL (or other compatible SQL database)

### Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/tauhidalam/expense-tracker-in1.git
   cd expense-tracker-in1
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add the following:
   ```env
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database_url
   ```

5. **Initialize the Database:**
   ```bash
   flask db upgrade
   ```

6. **Run the Application:**
   ```bash
   flask run
   ```

## Usage

1. **Access the Application:**
   [Access app here](https://expense-tracker-in1.onrender.com/)


2. **User Registration:**
   - Register a new account by navigating to `/register`.

3. **User Login:**
   - Log in with your credentials at `/login`.

4. **Managing Expenses:**
   - Add, view, and delete expenses at `/add_expense` and `/view_expenses`.

5. **Managing Income:**
   - Add and view income entries at `/add_income`.

6. **Managing Credit Cards:**
   - Add, view, reset, and delete credit cards at `/add_credit_card`.

7. **Managing Funds:**
   - Add and manage funds at `/add_fund`.

8. **Viewing Dashboard:**
   - View your financial overview at `/dashboard`.

9. **Generating Reports:**
   - Generate and view plots at `/generate_plots`.

## Development

- **Database Migrations:**
  - Use `flask db migrate` to create new migrations.
  - Apply migrations with `flask db upgrade`.

- **Testing:**
  - Write tests using Flask's testing framework or any other preferred method.


## Contact

For any questions or issues, please contact [tauhidalam1998@gmail.com](mailto:tauhidalam1998@gmail.com).
