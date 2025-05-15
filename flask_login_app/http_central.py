from flask import Flask, jsonify, request
import requests
import sqlite3
from datetime import datetime
import pytz
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Asia/Kolkata timezone
timezone = pytz.timezone('Asia/Kolkata')

# Database setup
DATABASE = '/var/www/flask_login_app/http_central.db'  # Updated to use http_central.db

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS speedtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_ip TEXT NOT NULL,
                download_time REAL NOT NULL,
                file_size_mb REAL NOT NULL,
                download_speed_mbps REAL NOT NULL,
                url TEXT NOT NULL,
                central_system_ip TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/start_speedtest', methods=['POST'])
def start_speedtest():
    data = request.get_json()
    node_ip = data.get('node_ip')
    if not node_ip:
        return jsonify({"error": "Node IP is required"}), 400

    try:
        # Ensure to send a POST request to the correct endpoint on the node
        response = requests.post(f'http://{node_ip}:5003/start_http_speedtest', json=data)

        # Check if response is successful
        if response.status_code == 200:
            try:
                result = response.json()
            except ValueError:
                # If the response is not valid JSON, log the raw response for debugging
                return jsonify({"error": "Invalid JSON response", "response_text": response.text}), 500

            # Add the central system IP and timestamp to the result
            result['central_system_ip'] = '10.114.56.189'
            now = datetime.now(timezone)
            result['timestamp'] = now.strftime('%Y-%m-%d %H:%M:%S')

            # Save the result into the database
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO speedtest_results (
                        node_ip, download_time, file_size_mb, download_speed_mbps, url, central_system_ip, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result['client_ip'],  # 'client_ip' is the IP from the RPi
                    result['download_time'],
                    result['downloaded_data_mb'],  # Adjusted from 'file_size_mb' based on the final RPi code
                    result['download_speed_mbps'],
                    result['url'],  # Use the 'url' from the RPi response
                    result['central_system_ip'],
                    result['timestamp']
                ))
                conn.commit()

            return jsonify(result)

        else:
            # If the status code is not 200, return an error message
            return jsonify({"error": f"Failed to get valid response from node. Status code: {response.status_code}"}), 500

    except requests.RequestException as e:
        return jsonify({"error": "Failed to contact node", "message": str(e)}), 500


@app.route('/get_speed_status', methods=['GET'])
def get_speed_status():
    node_ip = request.args.get('node_ip')
    if not node_ip:
        return jsonify({"error": "Node IP is required"}), 400

    try:
        # Send request to node to get speed test status
        response = requests.get(f'http://{node_ip}:5003/get_speed_status')

        # Check if response is successful
        if response.status_code == 200:
            try:
                result = response.json()
            except ValueError:
                return jsonify({"error": "Invalid JSON response", "response_text": response.text}), 500

            # Add central system IP and timestamp
            result['central_system_ip'] = '10.114.56.189'
            now = datetime.now(timezone)
            result['timestamp'] = now.strftime('%Y-%m-%d %H:%M:%S')

            # Save result in the database
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO speedtest_results (
                        node_ip, download_time, file_size_mb, download_speed_mbps, url, central_system_ip, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result['client_ip'],  
                    result['download_time'],
                    result['downloaded_data_mb'],  
                    result['download_speed_mbps'],
                    result['url'],  
                    result['central_system_ip'],
                    result['timestamp']
                ))
                conn.commit()

            return jsonify(result)

        else:
            return jsonify({"error": f"Failed to get valid response from node. Status code: {response.status_code}"}), 500

    except requests.RequestException as e:
        return jsonify({"error": "Failed to contact node", "message": str(e)}), 500

@app.route('/stop_speedtest', methods=['POST'])
def stop_speedtest():
    data = request.get_json()
    node_ip = data.get('node_ip')  # Get the node IP from the request

    if not node_ip:
        return jsonify({"error": "Node IP is required"}), 400

    try:
        # Ensure to send a POST request to the correct endpoint on the node
        response = requests.post(f'http://{node_ip}:5003/http_stop_speedtest', json=data)

        # Check if response is successful
        if response.status_code == 200:
            try:
                result = response.json()
            except ValueError:
                # If the response is not valid JSON, log the raw response for debugging
                return jsonify({"error": "Invalid JSON response", "response_text": response.text}), 500

            # Add the central system IP and timestamp to the result
            result['central_system_ip'] = '10.114.56.189'
            now = datetime.now(timezone)
            result['timestamp'] = now.strftime('%Y-%m-%d %H:%M:%S')

            # Save the result into the database
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO speedtest_results (
                        node_ip, download_time, file_size_mb, download_speed_mbps, url, central_system_ip, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result['client_ip'],  # 'client_ip' is the IP from the RPi
                    result['download_time'],
                    result['downloaded_data_mb'],  # Adjusted from 'file_size_mb' based on the final RPi code
                    result['download_speed_mbps'],
                    result['url'],  # Use the 'url' from the RPi response
                    result['central_system_ip'],
                    result['timestamp']
                ))
                conn.commit()

            return jsonify(result)

        else:
            # If the status code is not 200, return an error message
            return jsonify({"error": f"Failed to stop speed test on node. Status code: {response.status_code}"}), 500

    except requests.RequestException as e:
        return jsonify({"error": "Failed to contact node", "message": str(e)}), 500

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(host='10.114.56.189', port=5003, debug=True)
