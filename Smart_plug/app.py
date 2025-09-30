import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime
import time

# MQTT settings
broker = "203.109.124.70"
port = 18889
mqttc = mqtt.Client()

# SQLite DB setup
DB_FILE = "device_data.db"

# Create table if not exists
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_type TEXT,
            device_id TEXT,
            device_status TEXT,
            power REAL,
            voltage REAL,
            current REAL,
            inserttimestamp TEXT
        );
    """)
    conn.commit()
    conn.close()

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe("#")  # Subscribe to all topics
    else:
        print(f"❌ Failed to connect with return code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("⚠️ Disconnected from broker. Reconnecting...")
        try:
            mqttc.reconnect()
        except:
            pass

def on_message(client, userdata, message):
    try:
        payload = message.payload.decode()
        topic = message.topic

        # Connect to SQLite DB
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        # Initialize fields
        device_type = None
        device_id = None
        device_status = None
        power = None
        voltage = None
        current = None

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:00')

        if "plug" in topic:
            payload_str = payload.strip("{}")
            split_payload = payload_str.split(":")

            device_type = "plug"

            if len(split_payload) >= 6:
                device_id = split_payload[1]
                voltage = split_payload[2]
                current = split_payload[3]
                power = split_payload[4]
                device_status = split_payload[5]

            if device_id and device_id != '300':
                query = """
                    INSERT INTO device_data (device_type, device_id, device_status, power, voltage, current, inserttimestamp) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                val = (device_type, device_id, device_status, power, voltage, current, current_time)
                cursor.execute(query, val)
                connection.commit()
                print(f"✅ Data inserted for device ID: {device_id}")

        connection.close()

    except Exception as e:
        print(f"❌ Error processing message: {e}")

# Start MQTT and DB
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_disconnect = on_disconnect

def mqtt_connect():
    try:
        print("🔌 Connecting to MQTT broker...")
        mqttc.connect(broker, port)
        mqttc.loop_start()
    except Exception as e:
        print(f"❌ MQTT connection error: {e}")

# Initialize and start
if __name__ == "__main__":
    init_db()
    mqtt_connect()
    print("🚀 System running...")

    # Keep the program alive
    while True:
        time.sleep(1)
