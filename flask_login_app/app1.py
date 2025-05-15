from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this for production

DB_PATH = '/var/www/flask_login_app/users.db'

# Function to get database connection
def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT password, role FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        if password == user[0]:
            session['username'] = username
            session['role'] = user[1]
            if user[1] == 'admin':
                return '/adminhttp'  # Redirect to admin dashboard
            else:
                return '/user_dashboard'   # Redirect to user dashboard
        else:
            return 'Invalid password'
    else:
        return 'Invalid username'


@app.route('/adminhttp')
def adminhttp():
    if 'username' in session and session['role'] == 'admin':
        username = session.get('username') 
        return render_template('adminhttp.html', username=username)  # Ensure this file exists in your templates directory
    return redirect(url_for('index'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'username' in session and session['role'] == 'user':
        username = session.get('username')
        return render_template('user_dashboard.html', username=username)   # Placeholder response
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='10.114.56.189', port=5005)
