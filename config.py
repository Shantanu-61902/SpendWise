import mysql.connector

# Update these with your actual MySQL credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'SHANTANU@123',
    'database': 'expense_tracker'
}

DEFAULT_USER_ID = 1
CURRENCY = "₹"
def get_cursor():
    """Helper function to get a database connection and cursor."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    return conn, cur