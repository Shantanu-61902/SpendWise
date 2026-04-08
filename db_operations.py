from mysql.connector import Error
from config import get_cursor, DEFAULT_USER_ID

def initialize_tables():
    conn, cur = get_cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Assuming expenses and categories tables are created here or already exist
    conn.commit()
    cur.close()
    conn.close()

def add_income(amount, user_id=DEFAULT_USER_ID):
    conn, cur = get_cursor()
    sql = "INSERT INTO income (user_id, amount) VALUES (%s, %s)"
    try:
        cur.execute(sql, (user_id, amount))
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_dashboard_summary(user_id=DEFAULT_USER_ID):
    conn, cur = get_cursor()

    cur.execute("SELECT COALESCE(SUM(amount), 0) AS total_expense FROM expenses WHERE user_id = %s", (user_id,))
    exp = cur.fetchone()

    cur.execute("SELECT COALESCE(SUM(amount), 0) AS total_income FROM income WHERE user_id = %s", (user_id,))
    inc = cur.fetchone()

    cur.close()
    conn.close()

    DEFAULT_INCOME = 50000.0
    total_income = float(inc["total_income"]) if inc and float(inc["total_income"]) > 0 else DEFAULT_INCOME
    total_expense = float(exp["total_expense"]) if exp else 0.0

    remaining_income = total_income - total_expense

    return {
        "monthly_expense": total_expense,
        "monthly_income": remaining_income, # This acts as your dynamic balance
        "total_income_added": total_income
    }

def add_expense(title, amount, category_id, expense_date, description="", payment_mode="Cash", user_id=DEFAULT_USER_ID):
    conn, cur = get_cursor()
    try:
        # --- LIMIT CHECK LOGIC ---
        cur.execute("SELECT COALESCE(SUM(amount), 0) AS total_expense FROM expenses WHERE user_id = %s", (user_id,))
        exp = cur.fetchone()
        current_expenses = float(exp["total_expense"]) if exp else 0.0

        cur.execute("SELECT COALESCE(SUM(amount), 0) AS total_income FROM income WHERE user_id = %s", (user_id,))
        inc = cur.fetchone()
        DEFAULT_INCOME = 50000.0
        total_income = float(inc["total_income"]) if inc and float(inc["total_income"]) > 0 else DEFAULT_INCOME

        # Check if new expense exceeds the remaining limit
        new_total = current_expenses + float(amount)
        if new_total > total_income:
            return "LIMIT_EXCEEDED"
        # -------------------------

        sql = """
            INSERT INTO expenses (user_id, category_id, title, amount, expense_date, description, payment_mode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (user_id, category_id, title.strip(), float(amount), expense_date, description.strip(), payment_mode))
        conn.commit()
        return True

    except Error as e:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_all_categories():
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT * FROM categories ORDER BY name")
        return cur.fetchall()
    except Error:
        return []
    finally:
        cur.close()
        conn.close()

def get_expenses(user_id=DEFAULT_USER_ID, limit=500):
    conn, cur = get_cursor()
    sql = """
        SELECT e.id, c.name AS category, c.icon AS category_icon, 
               e.title, e.amount, e.expense_date, e.payment_mode
        FROM expenses e JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s ORDER BY e.expense_date DESC LIMIT %s
    """
    try:
        cur.execute(sql, [user_id, limit])
        return cur.fetchall()
    except Error:
        return []
    finally:
        cur.close()
        conn.close()

def delete_expense(expense_id):
    conn, cur = get_cursor()
    try:
        cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()
        return True
    except Error:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()