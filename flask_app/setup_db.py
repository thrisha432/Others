import sqlite3
import os

def create_database():
    # Specify the full path to the database file
    db_path = '/var/www/flask_app/speedtest.db'
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to (or create) the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table with schema matching app.py
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS speedtest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_ip TEXT NOT NULL,
            dest_ip TEXT NOT NULL,
            speed REAL NOT NULL,
            file_size TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    conn.commit()  # Save changes
    conn.close()   # Close the connection

if __name__ == '__main__':
    create_database()
