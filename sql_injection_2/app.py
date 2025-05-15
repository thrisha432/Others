from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('banking.db')
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

@app.route('/')
def home():
    return redirect('/search')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = None
    error = None

    if request.method == 'POST':
        query = request.form['query']
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Malicious query handling
            sql_query = f"SELECT name, city, branch FROM accounts WHERE name LIKE '{query}'"
            cursor.execute(sql_query)
            results = cursor.fetchall()

            if not results:
                error = "No results found for your query."
        except sqlite3.OperationalError as e:
            error = f"An error occurred: {e}"
        
        conn.close()

    return render_template('search.html', results=results, error=error)

@app.route('/details/<int:account_id>')
def details(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
    account = cursor.fetchone()
    conn.close()

    if not account:
        return render_template('error.html', message="Account not found.")

    return render_template('results.html', account=account)

if __name__ == '__main__':
    app.run(debug=True, host='10.114.56.189', port=5005)
