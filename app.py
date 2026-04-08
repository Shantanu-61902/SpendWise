from flask import Flask, render_template, request, redirect, url_for, flash
import db_operations
from config import CURRENCY

app = Flask(__name__)
app.secret_key = "abcd"

with app.app_context():
    db_operations.initialize_tables()


@app.context_processor
def inject_currency():
    return dict(CURRENCY=CURRENCY)


@app.route('/')
def dashboard():
    summary = db_operations.get_dashboard_summary()
    return render_template('dashboard.html', summary=summary)


@app.route('/add_income', methods=['POST'])
def add_income():
    amount = float(request.form['income_amount'])
    db_operations.add_income(amount)
    flash("Income added successfully!", "success")
    return redirect(url_for('dashboard'))


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        category_id = request.form['category']
        expense_date = request.form['date']
        payment_mode = request.form.get('payment_mode', 'Cash')

        result = db_operations.add_expense(title, amount, category_id, expense_date, payment_mode=payment_mode)

        # Trigger the popup if the limit is exceeded
        if result == "LIMIT_EXCEEDED":
            flash("Cannot add expense! This amount exceeds your available income balance.", "danger")
            return redirect(url_for('add_expense'))  # Redirect back to form
        elif result:
            flash("Expense added successfully!", "success")
            return redirect(url_for('view_expenses'))
        else:
            flash("Error adding expense.", "warning")

    categories = db_operations.get_all_categories()
    return render_template('add_expense.html', categories=categories)


@app.route('/view_expenses')
def view_expenses():
    expenses = db_operations.get_expenses()
    return render_template('view_expenses.html', expenses=expenses)


@app.route('/remove_expense/<int:expense_id>', methods=['POST'])
def remove_expense(expense_id):
    db_operations.delete_expense(expense_id)
    flash("Expense removed.", "success")
    return redirect(url_for('view_expenses'))


if __name__ == '__main__':
    app.run(debug=True)