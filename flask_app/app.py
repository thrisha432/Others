from flask import Flask, jsonify, render_template, request
import time
from ftplib import FTP
import os
import sqlite3
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 * 1024  # 4 GB

# FTP server details
FTP_SERVER = '10.114.58.99'
FTP_USER = 'emslab'
FTP_PASS = 'peach1395'
TEST_FILE_PATH = '/files/test_file.txt'  # Path to test file on the FTP server

# Database path
DB_PATH = '/var/www/flask_app/speedtest.db'

# Asia/Kolkata timezone
timezone = pytz.timezone('Asia/Kolkata')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_speedtest', methods=['POST'])
def start_speedtest():
    client_ip = request.remote_addr  # Capture the client IP
    result = download_speed_test(client_ip)
    if isinstance(result, str):
        return jsonify({'error': result})
    return jsonify(result)

def download_speed_test(client_ip):
    local_file = '/var/www/flask_app/downloaded_test_file.txt'
    try:
        ftp = FTP(FTP_SERVER)
        ftp.login(FTP_USER, FTP_PASS)

        # Get the size of the file from the FTP server in bytes
        file_size_bytes = ftp.size(TEST_FILE_PATH)
        if file_size_bytes is None:
            return "Unable to retrieve file size."

        # Convert file size to MB and round to 2 decimal places
        file_size_mb = round(file_size_bytes / 1048576, 2)  # 1 MB = 1048576 bytes

        start_time = time.time()
        with open(local_file, 'wb') as f:
            ftp.retrbinary(f'RETR {TEST_FILE_PATH}', f.write)
        end_time = time.time()

        if os.path.exists(local_file):
            elapsed_time = end_time - start_time
            if elapsed_time <= 0:
                elapsed_time = 1
            speed = file_size_mb / elapsed_time  # Speed in MBps

            # Round speed to 2 decimal places
            speed = round(speed, 2)

            # Get current timestamp in Asia/Kolkata timezone
            now = datetime.now(timezone)
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

            # Store result in the database
            store_result(client_ip, FTP_SERVER, speed, file_size_mb, timestamp)

            ftp.quit()
            return {
                'download_speed': f'{speed:.2f} MBps',
                'elapsed_time': f'{elapsed_time:.5f} seconds'
            }
        else:
            return "File was not downloaded."

    except Exception as e:
        return f"Error during download speed test: {str(e)}"

def store_result(source_ip, dest_ip, speed, file_size_mb, timestamp):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS speedtest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_ip TEXT NOT NULL,
                dest_ip TEXT NOT NULL,
                speed REAL NOT NULL,
                file_size TEXT NOT NULL,  -- Storing file size as TEXT to include "MB"
                timestamp TEXT NOT NULL
            )
        ''')

        # Insert data into the table
        cursor.execute('''
            INSERT INTO speedtest (source_ip, dest_ip, speed, file_size, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_ip, dest_ip, speed, f'{file_size_mb} MB', timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error storing result in database: {str(e)}")

if __name__ == '__main__':
    app.run(host='10.114.56.189', port=5001)
