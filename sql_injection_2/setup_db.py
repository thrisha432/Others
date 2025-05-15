import sqlite3

# Create database and table
conn = sqlite3.connect('banking.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    account_number TEXT NOT NULL UNIQUE,
    branch TEXT NOT NULL,
    city TEXT NOT NULL,
    balance REAL NOT NULL,
    ssn TEXT NOT NULL,
    email TEXT NOT NULL
)''')

# Insert sample data
accounts = [
    ('John Doe', '123456789', 'Downtown', 'New York', 1250.75, '123-45-6789', 'johndoe@example.com'),
    ('Jane Smith', '987654321', 'Uptown', 'Los Angeles', 2500.50, '987-65-4321', 'janesmith@example.com'),
    ('Alice Brown', '567890123', 'Central', 'Chicago', 1750.00, '567-89-0123', 'alicebrown@example.com'),
]

cursor.executemany('''INSERT INTO accounts (name, account_number, branch, city, balance, ssn, email)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', accounts)

conn.commit()
conn.close()
