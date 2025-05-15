from flask import Flask, jsonify, request
import subprocess
import time
import threading
import os
import signal
from datetime import datetime
import pytz

app = Flask(__name__)

# Constants
LOCAL_FILE_PATH = "/home/pi/Downloads/temp_downloaded_file"
timezone = pytz.timezone("Asia/Kolkata")
CLIENT_IP = "10.166.240.70"

# Global Variables with Thread Safety
wget_process = None
start_time = None
current_url = None
monitoring_thread = None
stop_monitoring = False
prev_size = 0
prev_time = 0
latest_speed = 0
latest_downloaded_mb = 0
elapsed_time = 0
completion_time = None
last_update_time = None
data_lock = threading.Lock()  # Thread lock for shared variables

def monitor_speed():
    global latest_speed, latest_downloaded_mb, elapsed_time, prev_size, prev_time, stop_monitoring, completion_time, last_update_time

    data_start_time = None  # Tracks when data first appears
    first_iteration = True  # Flag for initial state

    while not stop_monitoring:
        with data_lock:
            if start_time and os.path.exists(LOCAL_FILE_PATH):
                current_time = time.time()
                current_size = os.path.getsize(LOCAL_FILE_PATH)

                # Detect actual download start
                if current_size > 0 and data_start_time is None:
                    data_start_time = current_time
                    prev_time = current_time
                    prev_size = current_size
                    elapsed_time = 0  # Reset counter
                    first_iteration = False

                if data_start_time:
                    # Calculate time difference from actual start
                    time_diff = current_time - prev_time
                    elapsed_time = current_time - data_start_time  # Total time since data began
                    
                    # Calculate size difference
                    size_diff = current_size - prev_size
                    prev_size = current_size
                    prev_time = current_time

                    # Convert to MB and calculate speed
                    latest_downloaded_mb = current_size / (1024 * 1024)
                    latest_speed = (size_diff / (1024 * 1024)) / time_diff if time_diff > 0 else 0
                else:
                    # Pre-data state
                    elapsed_time = 0
                    latest_speed = 0
                    latest_downloaded_mb = 0

                # Sync timestamp with actual elapsed time
                last_update_time = datetime.now(timezone)

        time.sleep(1)

@app.route("/start_http_speedtest", methods=["POST"])
def start_http_speedtest():
    global wget_process, start_time, current_url, monitoring_thread, stop_monitoring
    global prev_size, prev_time, completion_time, latest_speed, latest_downloaded_mb, elapsed_time, last_update_time

    with data_lock:
        data = request.get_json()
        current_url = data["url"]
        start_time = time.time()
        prev_time = 0
        prev_size = 0
        latest_speed = 0
        latest_downloaded_mb = 0
        elapsed_time = 0
        stop_monitoring = False
        completion_time = None
        last_update_time = datetime.now(timezone)  # Initial timestamp

    try:
        if os.path.exists(LOCAL_FILE_PATH):
            os.remove(LOCAL_FILE_PATH)

        wget_command = ["wget", current_url, "-O", LOCAL_FILE_PATH, "--timeout=30"]
        wget_process = subprocess.Popen(wget_command, preexec_fn=os.setsid)

        monitoring_thread = threading.Thread(target=monitor_speed)
        monitoring_thread.start()

        wget_process.wait()
        completion_time = time.time()
        stop_monitoring = True
        monitoring_thread.join()

        return finalize_results("Speed test completed successfully", force_update=True)

    except Exception as e:
        stop_monitoring = True
        if wget_process:
            try:
                os.killpg(os.getpgid(wget_process.pid), signal.SIGTERM)
            except:
                pass
        return jsonify({"error": str(e)})
        
@app.route("/http_stop_speedtest", methods=["POST"])
def http_stop_speedtest():
    global wget_process, stop_monitoring, completion_time

    try:
        if wget_process and wget_process.poll() is None:
            completion_time = time.time()  # Record time when manually stopped
            os.killpg(os.getpgid(wget_process.pid), signal.SIGTERM)
            wget_process.wait()
            stop_monitoring = True
            return finalize_results("Speed test stopped manually", force_update=True)
        return jsonify({"error": "No active speed test running"})

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)})


@app.route("/get_speed_status", methods=["GET"])
def get_speed_status():
    if not start_time or stop_monitoring:
        return jsonify({"error": "No active download"})

    with data_lock:  # Thread-safe read
        timestamp = last_update_time.strftime("%Y-%m-%d %H:%M:%S") if last_update_time else datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({
            "client_ip": CLIENT_IP,
            "url": current_url,
            "download_speed_mbps": round(latest_speed, 2),
            "download_time": round(elapsed_time, 2),
            "downloaded_data_mb": round(latest_downloaded_mb, 2),
            "timestamp": timestamp,
            "message": "Live speed status"
        })

def finalize_results(message, force_update=False):
    global latest_downloaded_mb, elapsed_time, completion_time

    # Get the actual total file size
    if os.path.exists(LOCAL_FILE_PATH):
        total_downloaded_mb = os.path.getsize(LOCAL_FILE_PATH) / (1024 * 1024)
    else:
        total_downloaded_mb = latest_downloaded_mb

    # Use actual completion time for total elapsed time
    if completion_time:
        actual_elapsed_time = completion_time - start_time
    else:
        actual_elapsed_time = elapsed_time

    # Calculate average speed using total file size and total time
    if actual_elapsed_time > 0:
        average_speed = total_downloaded_mb / actual_elapsed_time
    else:
        average_speed = 0

    return jsonify({
        "client_ip": CLIENT_IP,
        "url": current_url,
        "download_speed_mbps": round(average_speed, 2),
        "download_time": round(actual_elapsed_time, 2),
        "downloaded_data_mb": round(total_downloaded_mb, 2),
        "timestamp": datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    })

if __name__ == "__main__":
    app.run(host= CLIENT_IP, port=5003)
