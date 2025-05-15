import pyspeedtest

st = pyspeedtest.SpeedTest('http://192.168.1.151:5001')
print("Testing download speed...")
download_speed = st.download() / 1_000_000  # Convert to Mbps
print(f"Download speed: {download_speed:.2f} Mbps")

print("Testing upload speed...")
upload_speed = st.upload() / 1_000_000  # Convert to Mbps
print(f"Upload speed: {upload_speed:.2f} Mbps")
