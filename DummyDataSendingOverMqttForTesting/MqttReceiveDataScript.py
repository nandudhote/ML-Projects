from flask import Flask
import paho.mqtt.client as mqtt
import time
import threading
from openpyxl import Workbook
from datetime import datetime
import signal
import sys
import os

# Initialize Flask app
app = Flask(_name_)

# MQTT settings
broker = "203.109.124.70"
port = 18889
topic_publish = "tubeF0BF30/control"
topic_subscribe = "tubeF0BF30/#"

# Initialize the Excel workbook and sheet
wb = Workbook()
ws = wb.active
ws.append(['Timestamp', 'Response'])

# Ensure the directory for saving the file exists
file_path = "mqtt_responses.xlsx"
if not os.path.exists(file_path):
    wb.save(file_path)

# Event to stop threads
stop_event = threading.Event()
mqttc = mqtt.Client()

# Create a lock to manage thread-safe file access
file_lock = threading.Lock()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic_subscribe)

def on_message(client, userdata, msg):
    response = msg.payload.decode('utf-8')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Locking the file writing to avoid race conditions
    with file_lock:
        ws.append([timestamp, response])
        wb.save(file_path)  # Ensure the file is saved in the same directory

def publish_data():
    while not stop_event.is_set():  # Check for the stop event
        try:
            message = "T:02:01:S"
            mqttc.publish(topic_publish, message)
            print(f"Published: {message}")
            time.sleep(10)
        except KeyboardInterrupt:
            print("Publishing stopped.")
            break

def start_mqtt():
    mqttc.connect(broker, port, 60)  # Connect to the broker
    mqttc.loop_start()  # Start the MQTT loop to handle incoming messages

@app.route('/')
def index():
    return "MQTT Publisher and Flask Server Running!"

def graceful_shutdown(signal, frame):
    print("Shutting down...")
    stop_event.set()  # Set the stop event to signal threads to stop
    mqttc.loop_stop()  # Stop MQTT loop
    sys.exit(0)  # Exit the program

signal.signal(signal.SIGINT, graceful_shutdown)

if _name_ == "_main_":
    # Start the MQTT client and data publishing threads
    threading.Thread(target=start_mqtt).start()
    threading.Thread(target=publish_data).start()
    app.run(debug=True, use_reloader=False)