import paho.mqtt.client as mqtt
import random
import time

# MQTT settings
MQTT_BROKER = "203.109.124.70"
MQTT_PORT = 18889  # Usually 1883 for non-SSL connections
# MQTT_USERNAME = "your_username"
# MQTT_PASSWORD = "your_password"
PUBLISH_TOPIC = "oeeStatF0BF0D/status"
SUBSCRIBE_TOPIC = "oeeStatF0BF0D/control"

# Device data (initial values)
device_id = "oeeStatF0BF0D"
voltage = 230.56
current = 2.5
power = voltage * current  # Calculated power
load_status = 1  # Initial load status
responseOn200Flag = False

# Tolerance for voltage and current
tolerance_percentage = 0.02  # 2% tolerance

# Function to introduce a random tolerance in the voltage and current values
def apply_tolerance(value, tolerance_percentage):
    tolerance = value * tolerance_percentage
    return round(value + random.uniform(-tolerance, tolerance), 2)

# MQTT callback function when connected to broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the control topic
    client.subscribe(SUBSCRIBE_TOPIC)
    print(f"Subscribed to {SUBSCRIBE_TOPIC}")

# MQTT callback function when a message is received
def on_message(client, userdata, msg):
    global responseOn200Flag
    global load_status, voltage
    received_message = msg.payload.decode("utf-8")
    print(f"Received message: {received_message}")
    
    # Handle control commands based on received message
    if received_message == "200":
        responseOn200Flag = True
    elif received_message == "100":
        load_status = 1  # Set load status to 1 (ON)
    elif received_message == "0":
        load_status = 0  # Set load status to 0 (OFF)

# MQTT setup
client = mqtt.Client()
# client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start MQTT client loop
client.loop_start()

# Main loop to publish data every 1 second
try:
    while True:
        # Apply tolerance to voltage and current
        voltage_with_tolerance = apply_tolerance(voltage, tolerance_percentage)
        current_with_tolerance = apply_tolerance(current, tolerance_percentage)
        power = voltage_with_tolerance * current_with_tolerance  # Recalculate power
        
        if responseOn200Flag is True:
            # Construct the message to publish
            message = f"{'300'}:{voltage_with_tolerance}:{current_with_tolerance}:{round(power, 2)}:{load_status}"
            responseOn200Flag = False
        else:
            # Construct the message to publish
            message = f"{device_id}:{voltage_with_tolerance}:{current_with_tolerance}:{round(power, 2)}:{load_status}"
        
        
        # Publish the message
        client.publish(PUBLISH_TOPIC, message)
        print(f"Published: {message}")
        
        # Wait for 1 second before publishing again
        time.sleep(1)

except KeyboardInterrupt:
    print("Program interrupted by user")

finally:
    client.loop_stop()
    client.disconnect()
