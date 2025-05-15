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

# Global Variables
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

def monitor_speed():
    global latest_speed, latest_downloaded_mb, elapsed_time, prev_size, prev_time, stop_monitoring, completion_time

    while not stop_monitoring:
        if start_time and os.path.exists(LOCAL_FILE_PATH):
            current_time = time.time()
            current_size = os.path.getsize(LOCAL_FILE_PATH)
           
            # Calculate actual time difference since last check
            time_diff = current_time - prev_time if prev_time else 5  # Default to 5s for first iteration
            prev_time = current_time
           
            # Calculate downloaded bytes since last check
            size_diff = current_size - prev_size
            prev_size = current_size  # Update previous size after calculation
           
            # Convert to MB
            latest_downloaded_mb = current_size / (1024 * 1024)
           
            # Calculate instantaneous speed (MB/s)
            if time_diff > 0:
                latest_speed = max(0, (size_diff / (1024 * 1024)) / time_diff)
            else:
                latest_speed = 0
               
            # Update elapsed time (using completion_time if download is done)
            if completion_time:
                elapsed_time = completion_time - start_time
            else:
                elapsed_time = current_time - start_time
           
        time.sleep(5)

@app.route("/start_http_speedtest", methods=["POST"])
def start_http_speedtest():
    global wget_process, start_time, current_url, monitoring_thread, stop_monitoring
    global prev_size, prev_time, completion_time, latest_speed, latest_downloaded_mb, elapsed_time

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

    try:
        # Clear any existing file
        if os.path.exists(LOCAL_FILE_PATH):
            os.remove(LOCAL_FILE_PATH)
           
        wget_command = ["wget", current_url, "-O", LOCAL_FILE_PATH, "--timeout=30"]
        wget_process = subprocess.Popen(wget_command, preexec_fn=os.setsid)

        # Start monitoring
        monitoring_thread = threading.Thread(target=monitor_speed)
        monitoring_thread.start()

        wget_process.wait()
        completion_time = time.time()  # Record actual completion time
        stop_monitoring = True
        monitoring_thread.join()  # Wait for monitoring thread to finish

        return finalize_results("Speed test completed successfully", force_update=True)

    except Exception as e:
        stop_monitoring = True
        if wget_process:
            try:
                os.killpg(os.getpgid(wget_process.pid), signal.SIGTERM)
            except:
                pass
        return jsonify({"error": "Internal Server Error", "message": str(e)})

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

    now = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
   
    return jsonify({
        "client_ip": CLIENT_IP,
        "url": current_url,
        "download_speed_mbps": round(latest_speed, 2),
        "download_time": round(elapsed_time, 2),
        "downloaded_data_mb": round(latest_downloaded_mb, 2),
        "timestamp": now,
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

