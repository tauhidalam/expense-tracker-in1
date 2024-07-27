from flask import Flask, render_template, redirect, url_for, flash, session, request, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, FloatField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional , ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
import matplotlib.pyplot as plt
import re
import matplotlib
matplotlib.use('Agg')
import io
from io import BytesIO
import base64
import seaborn as sns
import pandas as pd
from flask_migrate import Migrate

app = Flask(__name__)
secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')
print(f'SECRET_KEY: {secret_key}')  # Add this line for debugging
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    def set_password(self, password):
        self.password = generate_password_hash(password)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    spend_source = db.Column(db.String(50), nullable=False)
    credit_card_name = db.Column(db.String(150), nullable=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('fund.id'), nullable=True)


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(150), nullable=False)

class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    credit_limit = db.Column(db.Float, nullable=False)
    available_limit = db.Column(db.Float, nullable=False)  # Existing field
    outstanding = db.Column(db.Float, nullable=False, default=0.0)  # New field

class Fund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    allocation_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fund_type = db.Column(db.String(64), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_current_month(form, field):
    now = datetime.now()
    if field.data.month != now.month or field.data.year != now.year:
        raise ValidationError('Date must be within the current month.')
    

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

class ExpenseForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', default=datetime.today, validators=[DataRequired(),validate_current_month])
    description = StringField('Description', validators=[DataRequired(), Length(max=200)])
    amount = FloatField('Amount', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Home', 'Home'), ('Self', 'Self'), ('Debt', 'Debt'), ('Others', 'Others')])
    spend_source = SelectField('Spend Source', choices=[('Cash', 'Cash'), ('Online/UPI', 'Online/UPI'), ('Cashback', 'Cashback'), ('Credit Card', 'Credit Card'), ('Funds', 'Funds')])
    credit_card_name = SelectField('Credit Card Name', choices=[], validators=[Optional()])
    fund_id = SelectField('Fund', coerce=int, validators=[Optional()])
    submit = SubmitField('Add Expense')

class IncomeForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired(),validate_current_month])
    amount = FloatField('Amount', validators=[DataRequired()])
    source = SelectField('Source of Income', choices=[('Salary', 'Salary'), ('Cashbacks', 'Cashbacks'), ('Others', 'Others')], validators=[DataRequired()])
    submit = SubmitField('Add Income')

class CreditCardForm(FlaskForm):
    name = StringField('Credit Card Name', validators=[DataRequired()])
    credit_limit = FloatField('Credit Limit', validators=[DataRequired()])
    submit = SubmitField('Add Credit Card')

class FundForm(FlaskForm):
    allocation_date = DateField('Allocation Date', validators=[DataRequired(),validate_current_month])
    amount = FloatField('Amount', validators=[DataRequired()])
    fund_type = SelectField('Fund Type', choices=[('Savings', 'Savings'), ('Emergency Fund', 'Emergency Fund'), ('Repairing Fund', 'Repairing Fund'), ('Others', 'Others')])
    submit = SubmitField('Add Fund')

class SortingForm(FlaskForm):
    sort_order = SelectField('Sort Order', choices=[('asc', 'Ascending'), ('desc', 'Descending')], validators=[DataRequired()])
    submit = SubmitField('Sort')

class FilterForm(FlaskForm):
    month = SelectField('Month', choices=[(i, f'{i:02d}') for i in range(1, 13)], coerce=int, default=datetime.now().month)
    year = IntegerField('Year', default=datetime.now().year)
    submit = SubmitField('Filter')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        input_data = form.username.data
        user = None
        if re.match(r"[^@]+@[^@]+\.[^@]+", input_data):
            user = User.query.filter_by(email=input_data).first()
        else:
            user = User.query.filter_by(username=input_data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            session['user_id'] = user.id  # Ensure session is set properly
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            return redirect(url_for('reset_password', email=user.email))
        flash('If your email is registered, you will receive a password reset link.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html', form=form)


@app.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid email address.', 'warning')
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been reset successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


def generate_pie_chart(data, labels, title):
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title(title)
    
    # Save it to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    
    # Encode the buffer to base64
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_base64


@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).limit(10).all()
    funds = Fund.query.filter_by(user_id=user.id).all()
    credit_cards = CreditCard.query.filter_by(user_id=user.id).all()
    incomes = Income.query.filter_by(user_id=user.id).all()

    # Get the current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Calculate total income for the current month
    total_income = sum(
        income.amount for income in incomes
        if income.date.month == current_month and income.date.year == current_year
    )

    # Calculate total expenses for the current month
    total_expenses = sum(
        expense.amount for expense in expenses
        if expense.date.month == current_month and expense.date.year == current_year
        and expense.spend_source in ['Cash', 'Online/UPI', 'Cashback']
    )

    # Calculate total funds for the current month
    total_funds = sum(
        fund.amount for fund in funds
        if fund.allocation_date.month == current_month and fund.allocation_date.year == current_year
    )

    # Calculate total available amount
    total_available = total_income - total_expenses - total_funds

    # Determine the background color based on the balance
    if total_available > 15000:
        balance_color = 'green'
    elif total_available > 5000:
        balance_color = 'lightcoral'
    else:
        balance_color = 'darkred'

    # Calculate total credit card outstanding
    total_outstanding = sum(card.outstanding for card in credit_cards)

    # Determine the background color based on the total outstanding balance
    if total_outstanding > 50000:
        outstanding_color = 'darkred'
    elif total_outstanding > 30000:
        outstanding_color = 'lightcoral'
    else:
        outstanding_color = 'green'

    # Render the dashboard without plots
    return render_template('dashboard.html', expenses=expenses, funds=funds, credit_cards=credit_cards, 
                           total_available=total_available, balance_color=balance_color,
                           total_outstanding=total_outstanding, outstanding_color=outstanding_color)

@app.route('/generate_plots', methods=['POST'])
@login_required
def generate_plots():
    user = current_user
    expenses = Expense.query.filter_by(user_id=user.id).all()

    # Restrict generating plots if no expense is recorded
    if not expenses:
        flash('No expenses recorded. Please add expenses to generate plots.', 'warning')
        return redirect(url_for('dashboard'))  # Or any appropriate route

    credit_cards = CreditCard.query.filter_by(user_id=user.id).all()
    funds = Fund.query.filter_by(user_id=user.id).all()

    # Create new plots
    category_plot_url = create_category_plot(expenses)
    spend_source_plot_url = create_spend_source_plot(expenses)

    # Prepare data for new pie charts
    credit_card_outstanding = [card.outstanding for card in credit_cards]
    credit_card_labels = [card.name for card in credit_cards]
    fund_amounts = [fund.amount for fund in funds]
    fund_labels = [fund.fund_type for fund in funds]

    # Check if there are any outstanding balances
    if any(credit_card_outstanding):
        credit_card_plot_url = generate_pie_chart(credit_card_outstanding, credit_card_labels, "Credit Card Outstandings")
    else:
        credit_card_plot_url = None

    if any(fund_amounts):
        fund_plot_url = generate_pie_chart(fund_amounts, fund_labels, "Funds Allocation")
    else:
        fund_plot_url= None

    # Render only the plots page with plot URLs
    return render_template('plots.html', 
                           category_plot_url=category_plot_url, 
                           spend_source_plot_url=spend_source_plot_url,
                           credit_card_plot_url=credit_card_plot_url, 
                           fund_plot_url=fund_plot_url)



@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    user_id = current_user.id

    # Fetch credit cards and funds for the user
    credit_cards = CreditCard.query.filter_by(user_id=user_id).all()
    form.credit_card_name.choices = [(card.id, card.name) for card in credit_cards]
    funds = Fund.query.filter_by(user_id=user_id).all()
    form.fund_id.choices = [(fund.id, f"{fund.fund_type} - {fund.amount}") for fund in funds]

    if form.validate_on_submit():
        credit_card_id = form.credit_card_name.data if form.spend_source.data == 'Credit Card' else None
        fund_id = form.fund_id.data if form.spend_source.data == 'Funds' else None

        expense = Expense(
            user_id=user_id,
            date=form.date.data,
            description=form.description.data,
            amount=form.amount.data,
            category=form.category.data,
            spend_source=form.spend_source.data,
            credit_card_name=credit_card_id,
            fund_id=fund_id
        )
        db.session.add(expense)

        if credit_card_id:
            credit_card = CreditCard.query.get(credit_card_id)
            if credit_card:
                credit_card.available_limit -= form.amount.data  # Update available limit
                credit_card.outstanding += form.amount.data  # Update outstanding balance

        if fund_id:
            fund = Fund.query.get(fund_id)
            if fund:
                fund.amount -= form.amount.data
                if fund.amount <= 0:
                    db.session.delete(fund)

        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('add_expense'))

    # Set the default values and disable fields as necessary
    if form.spend_source.data != 'Credit Card':
        form.credit_card_name.data = None
        form.credit_card_name.render_kw = {'disabled': True}
    if form.spend_source.data != 'Funds':
        form.fund_id.data = None
        form.fund_id.render_kw = {'disabled': True}

    return render_template('add_expense.html', form=form)

@app.route('/view_expenses', methods=['GET', 'POST'])
@login_required
def view_expenses():
    # Instantiate forms
    sort_form = SortingForm()
    filter_form = FilterForm()

    user_id = current_user.id
    sort_order = 'desc'  # Default sorting order
    month = datetime.now().month
    year = datetime.now().year

    # Handle form submissions
    if sort_form.validate_on_submit():
        sort_order = sort_form.sort_order.data

    if filter_form.validate_on_submit():
        month = filter_form.month.data
        year = filter_form.year.data

    # Query expenses based on filters and sorting
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    if sort_order == 'asc':
        expenses = Expense.query.filter_by(user_id=user_id).filter(
            Expense.date.between(start_date, end_date)
        ).order_by(Expense.date.asc()).all()
    else:
        expenses = Expense.query.filter_by(user_id=user_id).filter(
            Expense.date.between(start_date, end_date)
        ).order_by(Expense.date.desc()).all()

    # Handle delete request
    if request.method == 'POST' and 'delete_expense' in request.form:
        expense_id = int(request.form['delete_expense'])
        expense = Expense.query.get(expense_id)
        if expense and expense.user_id == user_id:
            # Revert changes to related models if necessary
            if expense.credit_card_name:
                credit_card = CreditCard.query.filter_by(name=expense.credit_card_name, user_id=user_id).first()
                if credit_card:
                    credit_card.available_limit += expense.amount
                    db.session.add(credit_card)

            if expense.spend_source == 'fund':
                fund = Fund.query.filter_by(name=expense.fund_name, user_id=user_id).first()
                if fund:
                    fund.amount += expense.amount
                    db.session.add(fund)

            db.session.delete(expense)
            db.session.commit()
            flash('Expense deleted successfully!', 'success')
            return redirect(url_for('view_expenses'))

    return render_template(
        'view_expenses.html',
        expenses=expenses,
        sort_form=sort_form,
        filter_form=filter_form
    )


@app.route('/add_income', methods=['GET', 'POST'])
@login_required
def add_income():
    form = IncomeForm()
    user_id = current_user.id

    if form.validate_on_submit():
        income = Income(
            user_id=user_id,
            date=form.date.data,
            amount=form.amount.data,
            source=form.source.data
        )
        db.session.add(income)
        db.session.commit()
        flash('Income added successfully!', 'success')
        return redirect(url_for('add_income'))

    # Handle delete requests
    if request.method == 'POST' and 'delete_income' in request.form:
        income_id = int(request.form['delete_income'])
        income = Income.query.get(income_id)
        if income:
            db.session.delete(income)
            db.session.commit()
            flash('Income entry deleted successfully!', 'success')
            return redirect(url_for('add_income'))

    # Fetch recent income entries for the current user
    recent_incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc()).limit(10).all()
    return render_template('add_income.html', form=form, recent_incomes=recent_incomes)
@app.route('/add_credit_card', methods=['GET', 'POST'])
@login_required
def add_credit_card():
    form = CreditCardForm()
    user_id = current_user.id

    if form.validate_on_submit():
        credit_limit = form.credit_limit.data

        credit_card = CreditCard(
            user_id=user_id,
            name=form.name.data,
            credit_limit=credit_limit,
            available_limit=credit_limit,  # Initialize available limit
            outstanding=0.0  # Initialize outstanding balance
        )
        db.session.add(credit_card)
        db.session.commit()
        flash('Credit Card added successfully!', 'success')
        return redirect(url_for('add_credit_card'))

    # Handle reset outstanding balance request
    if request.method == 'POST' and 'reset_outstanding' in request.form:
        card_id = int(request.form['reset_outstanding'])
        credit_card = CreditCard.query.get(card_id)
        if credit_card:
            # Reset outstanding balance and update available limit
            credit_card.outstanding = 0.0
            credit_card.available_limit = credit_card.credit_limit
            db.session.commit()
            flash('Outstanding balance reset successfully!', 'success')
            return redirect(url_for('add_credit_card'))

    # Handle delete credit card request
    if request.method == 'POST' and 'delete_credit_card' in request.form:
        card_id = int(request.form['delete_credit_card'])
        credit_card = CreditCard.query.get(card_id)
        if credit_card:
            db.session.delete(credit_card)
            db.session.commit()
            flash('Credit Card deleted successfully!', 'success')
            return redirect(url_for('add_credit_card'))

    # Fetch all credit cards for the current user
    credit_cards = CreditCard.query.filter_by(user_id=user_id).all()

    # Fetch all expenses for each credit card
    credit_card_expenses = {}
    for card in credit_cards:
        credit_card_expenses[card.id] = Expense.query.filter(
            Expense.user_id == user_id,
            Expense.credit_card_name.cast(Integer) == card.id
        ).all()

    return render_template('add_credit_card.html', form=form, credit_cards=credit_cards, credit_card_expenses=credit_card_expenses)

@app.route('/add_fund', methods=['GET', 'POST'])
@login_required
def add_fund():
    form = FundForm()
    user_id = current_user.id

    # Fetch all funds for the current user
    user_funds = Fund.query.filter_by(user_id=user_id).all()

    if form.validate_on_submit():
        fund_type = form.fund_type.data
        amount = form.amount.data
        allocation_date = form.allocation_date.data

        # Calculate total income and total expenses
        total_income = sum(i.amount for i in Income.query.filter_by(user_id=user_id).all())
        total_expenses = sum(expense.amount for expense in Expense.query.filter_by(user_id=user_id) if expense.spend_source in ['Cash', 'Online/UPI', 'Cashback'])

        # Calculate user balance
        available_balance = total_income - total_expenses

        # Check if sufficient balance is available
        if available_balance < amount:
            flash('Insufficient balance to add fund.', 'danger')
        else:
            # Check if a fund of the same type already exists
            existing_fund = Fund.query.filter_by(user_id=user_id, fund_type=fund_type).first()
            if existing_fund:
                # Update the existing fund's amount and allocation date
                existing_fund.amount += amount
                existing_fund.allocation_date = allocation_date
            else:
                # Create a new fund
                fund = Fund(
                    user_id=user_id,
                    allocation_date=allocation_date,
                    amount=amount,
                    fund_type=fund_type
                )
                db.session.add(fund)

            # Deduct the fund amount from the available balance
            available_balance -= amount

            # Commit the transaction
            db.session.commit()
            flash('Fund added/updated successfully!', 'success')
            return redirect(url_for('add_fund'))

    # Handle reset requests
    if request.method == 'POST' and 'reset_fund' in request.form:
        fund_id = int(request.form['reset_fund'])
        fund = Fund.query.get(fund_id)
        if fund:
            # Reset the fund's amount
            fund.amount = 0.0
            db.session.commit()
            flash('Fund amount reset successfully!', 'success')
            return redirect(url_for('add_fund'))

    return render_template('add_fund.html', form=form, user_funds=user_funds)


@app.route('/export_report', methods=['GET', 'POST'])
@login_required
def export_report():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        entry_type = request.form.get('entry_type', 'all')

        # Format the date range and entry type for the filename
        date_format = '%Y-%m-%d'
        formatted_start_date = datetime.strptime(start_date, date_format).strftime('%Y%m%d') if start_date else 'startdate'
        formatted_end_date = datetime.strptime(end_date, date_format).strftime('%Y%m%d') if end_date else 'enddate'
        entry_type_clean = entry_type.replace(' ', '_').lower()  # Clean entry type for filename

        filename = f'report_{formatted_start_date}_to_{formatted_end_date}_{entry_type_clean}.xlsx'

        # Generate the report
        report_file = generate_report(start_date, end_date, entry_type)

        if report_file:
            return send_file(
                report_file,
                download_name=filename,  # Dynamic filename based on parameters
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    return render_template('export_report.html', report_url=None)

    

def generate_report(start_date, end_date, entry_type):
    user_id = current_user.id
    
    # Fetch data based on entry_type and date range
    if entry_type == 'all':
        expenses = Expense.query.filter_by(user_id=user_id).filter(Expense.date.between(start_date, end_date)).all()
        incomes = Income.query.filter_by(user_id=user_id).filter(Income.date.between(start_date, end_date)).all()
        funds = Fund.query.filter_by(user_id=user_id).filter(Fund.allocation_date.between(start_date, end_date)).all()
    elif entry_type == 'expenses':
        expenses = Expense.query.filter_by(user_id=user_id).filter(Expense.date.between(start_date, end_date)).all()
        incomes = []
        funds = []
    elif entry_type == 'incomes':
        incomes = Income.query.filter_by(user_id=user_id).filter(Income.date.between(start_date, end_date)).all()
        expenses = []
        funds = []
    elif entry_type == 'funds':
        funds = Fund.query.filter_by(user_id=user_id).filter(Fund.allocation_date.between(start_date, end_date)).all()
        expenses = []
        incomes = []
    else:
        return None

    # Create an Excel writer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Add data to sheets
        if expenses:
            df_expenses = pd.DataFrame([model_to_dict(e) for e in expenses])
            df_expenses.to_excel(writer, sheet_name='Expenses', index=False)

        if incomes:
            df_incomes = pd.DataFrame([{
                'date': i.date.strftime('%Y-%m-%d'),
                'amount': i.amount,
                'source': i.source
            } for i in incomes])
            df_incomes.to_excel(writer, sheet_name='Incomes', index=False)

        if funds:
            df_funds = pd.DataFrame([{
                'fund_type': f.fund_type,
                'amount': f.amount,
                'allocation_date': f.allocation_date.strftime('%Y-%m-%d')
            } for f in funds])
            df_funds.to_excel(writer, sheet_name='Funds', index=False)

    # Reset the stream position to the beginning
    output.seek(0)
    
    return output

def model_to_dict(model_instance):
    return {
        'date': model_instance.date.strftime('%Y-%m-%d'),
        'description': model_instance.description,
        'amount': model_instance.amount,
        'spend_source': model_instance.spend_source
    }

#plots and graphs

def create_category_plot(expenses):
    if not expenses:
        return None  # Return None or a placeholder image if no data

    # Create a DataFrame from expenses data
    data = [{'category': e.category, 'amount': e.amount} for e in expenses]
    df = pd.DataFrame(data)

    # Handle NaN values
    df['amount'].fillna(0, inplace=True)  # Replace NaN amounts with 0
    df = df.dropna(subset=['category'])  # Drop rows where 'category' is NaN

    if df.empty:
        return None  # Return None or a placeholder image if DataFrame is empty

    # Plot using Seaborn
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plot = sns.barplot(x='category', y='amount', data=df, palette='viridis')
    plt.title('Expenses by Category')
    plt.xlabel('Category')
    plt.ylabel('Amount')

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # Clear the plot for the next one
    plt.clf()

    return plot_url

def create_spend_source_plot(expenses):
    if not expenses:
        return None  # Return None or a placeholder image if no data

    # Create a DataFrame from expenses data
    data = [{'spend_source': e.spend_source, 'amount': e.amount} for e in expenses]
    df = pd.DataFrame(data)

    # Handle NaN values
    df['amount'].fillna(0, inplace=True)  # Replace NaN amounts with 0
    df = df.dropna(subset=['spend_source'])  # Drop rows where 'spend_source' is NaN

    if df.empty:
        return None  # Return None or a placeholder image if DataFrame is empty

    # Plot using Seaborn
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plot = sns.barplot(x='spend_source', y='amount', data=df, palette='viridis')
    plt.title('Expenses by Spend Source')
    plt.xlabel('Spend Source')
    plt.ylabel('Amount')

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # Clear the plot for the next one
    plt.clf()

    return plot_url

if __name__ == '__main__':
    db_file = 'expense_tracker.db'
    if not os.path.exists(db_file):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
