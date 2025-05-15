from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('users.db')  # Path to your SQLite database
    conn.row_factory = sqlite3.Row  # This allows accessing rows as dictionaries
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Connect to the SQLite database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, check if the username exists
        username_query = f"SELECT * FROM users WHERE username = '{username}'"
        cursor.execute(username_query)
        user = cursor.fetchone()

        if user is None:
            error = "Invalid username"
        else:
            # Check if the password matches
            password_query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            cursor.execute(password_query)
            user_with_password = cursor.fetchone()

            if user_with_password is None:
                error = "Invalid password"
            else:
                # Successfully logged in
                return render_template('dashboard.html', username=username)  # Successful login
        
        conn.close()

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    return "<h1>Congratulations!! You're logged in successfully</h1>"

if __name__ == "__main__":
    app.run(debug=True, host="10.114.56.189", port=5004)
