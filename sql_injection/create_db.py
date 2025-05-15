import sqlite3

# Connect to SQLite3 database (or create it if it doesn't exist)
conn = sqlite3.connect('users.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create the table for user credentials
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

# Insert some sample users into the database
users = [
    ('admin', 'admin123'),
    ('user1', 'password1'),
    ('user2', 'password2'),
    ('user3', 'password3'),
    ('user4', 'password4'),
    ('user5', 'password5'),
    ('user6', 'password6'),
    ('user7', 'password7'),
    ('user8', 'password8'),
    ('user9', 'password9')
]

# Insert each user into the table
cursor.executemany('INSERT INTO users (username, password) VALUES (?, ?)', users)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created and sample users added.")
