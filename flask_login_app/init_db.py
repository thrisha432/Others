import sqlite3

# Database file path
DB_PATH = '/var/www/flask_login_app/users.db'

def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create users table with username, password, and role
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # List of (username, password, role) tuples
    users = [
        ('admin1', 'pass1', 'admin'),
        ('admin2', 'pass2', 'admin'),
        ('admin3', 'pass3', 'admin'),
        ('admin4', 'pass4', 'admin'),
        ('admin5', 'pass5', 'admin'),
        ('user1', 'password1', 'user'),
        ('user2', 'password2', 'user'),
        ('user3', 'password3', 'user'),
        ('user4', 'password4', 'user'),
        ('user5', 'password5', 'user'),
        ('user6', 'password6', 'user'),
        ('user7', 'password7', 'user'),
        ('user8', 'password8', 'user'),
        ('user9', 'password9', 'user'),
        ('user10', 'password10', 'user'),
        ('user11', 'password11', 'user'),
        ('user12', 'password12', 'user'),
        ('user13', 'password13', 'user'),
        ('user14', 'password14', 'user'),
        ('user15', 'password15', 'user')
    ]

    # Clear existing users
    cursor.execute('DELETE FROM users')

    # Insert users into the table
    cursor.executemany('''
        INSERT INTO users (username, password, role) VALUES (?, ?, ?)
    ''', users)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_table()
    insert_users()
