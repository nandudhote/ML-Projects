import RPi.GPIO as GPIO
import time
import subprocess
import paho.mqtt.client as mqtt
import requests

# GPIO setup
BUTTON_GPIO = 17     # GPIO pin for the first button (flash button)
SHUTDOWN_BUTTON_GPIO = 27  # GPIO pin for the shutdown button
GREEN_LED_GPIO = 2   # GPIO pin for the green LED
RED_LED_GPIO = 3     # GPIO pin for the red LED
ORANGE_LED_GPIO = 4  # GPIO pin for the orange LED

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SHUTDOWN_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GREEN_LED_GPIO, GPIO.OUT)
GPIO.setup(RED_LED_GPIO, GPIO.OUT)
GPIO.setup(ORANGE_LED_GPIO, GPIO.OUT)

# Initialize LEDs to be off
GPIO.output(GREEN_LED_GPIO, GPIO.LOW)
GPIO.output(RED_LED_GPIO, GPIO.LOW)
GPIO.output(ORANGE_LED_GPIO, GPIO.LOW)

# MQTT setup
MQTT_BROKER = "203.109.124.70"
MQTT_PORT = 18889
MQTT_TOPIC = "evoluzn_ota/control"
# URL to call to get the .bin file
FILE_API_URL = "http://203.109.124.70:1000/sp16"

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")
def on_message(client, userdata, msg):
    try:
        if msg.payload.decode() == "100":
            print("100 received via MQTT, downloading .bin file...")
            download_bin_file()
    except Exception as e:
        print(f"Error: {e}")

client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the MQTT loop in a separate thread
client.loop_start()

# Function to download the .bin file
def download_bin_file():
    try:
        response = requests.get(FILE_API_URL, stream=True)
        if response.status_code == 200:
            with open("STM32fileToUpload.bin", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Downloaded .bin file saved as STM32fileToUpload.bin")
            ledBlink(GREEN_LED_GPIO, 1)
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            ledBlink(GREEN_LED_GPIO, 1)

    except Exception as e:
        print(f"Error during file download: {e}")
        GPIO.output(RED_LED_GPIO, GPIO.HIGH)

# Function to check Wi-Fi connection using ifconfig
def check_wifi_connection():
    try:
        result = subprocess.run(["ifconfig", "wlan0"], stdout=subprocess.PIPE, text=True)
        if "inet " in result.stdout:
            print("Wi-Fi connected.")
            GPIO.output(ORANGE_LED_GPIO, GPIO.HIGH)
            return True
        else:
            print("Wi-Fi not connected.")
            return False
    except Exception as e:
        print(f"Error checking Wi-Fi connection: {e}")
        return False

# Function to blink the orange LED
def ledBlink(gpio, delay):
    GPIO.output(gpio, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(gpio, GPIO.LOW)
    time.sleep(delay)



# Function to flash the .bin file
def flash_bin_file():
    print("Flashing .bin file to STM32F103...")
    try:
        # Execute the flash command
        result = subprocess.run(["st-flash", "write", "STM32fileToUpload.bin", "0x08000000"], check=True)
        # If successful, turn on green LED
        GPIO.output(GREEN_LED_GPIO, GPIO.HIGH)
        GPIO.output(RED_LED_GPIO, GPIO.LOW)
        print("Flashing completed successfully.")
    except subprocess.CalledProcessError:
        # If the flashing fails, turn on red LED
        GPIO.output(GREEN_LED_GPIO, GPIO.LOW)
        GPIO.output(RED_LED_GPIO, GPIO.HIGH)
        print("Flashing failed.")

# Function to check if shutdown button is pressed continuously for 5 seconds
def check_shutdown_button():
    if GPIO.input(SHUTDOWN_BUTTON_GPIO) == GPIO.LOW:  # Button is pressed
        print("Shutdown button pressed. Holding for 5 seconds to shutdown...")
        time.sleep(5)  # Wait for 5 seconds
        if GPIO.input(SHUTDOWN_BUTTON_GPIO) == GPIO.LOW:  # Button is still pressed after 5 seconds
            ledBlink(GREEN_LED_GPIO, 0.5)
            ledBlink(RED_LED_GPIO, 0.5)
            ledBlink(GREEN_LED_GPIO, 0.5)
            ledBlink(RED_LED_GPIO, 0.5)
            print("Shutting down now.")
            subprocess.run(["sudo", "shutdown", "now"])
        else:
            print("Shutdown button released before 5 seconds.")

# Main loop to wait for button press
try:
    while True:
        # Check Wi-Fi connection
        if check_wifi_connection():
            GPIO.output(ORANGE_LED_GPIO, GPIO.HIGH)
        else:
            ledBlink(ORANGE_LED_GPIO, 0.5)

        # Check if the flash button is pressed
        button_state = GPIO.input(BUTTON_GPIO)
        if button_state == GPIO.LOW:  # Button pressed
            print("Flash button pressed, executing flash command.")
            # Turn off both LEDs before starting
            GPIO.output(GREEN_LED_GPIO, GPIO.LOW)
            GPIO.output(RED_LED_GPIO, GPIO.LOW)
            flash_bin_file()
            # Wait for the button to be released
            while GPIO.input(BUTTON_GPIO) == GPIO.LOW:
                time.sleep(0.1)

        # Check if the shutdown button is pressed continuously for 5 seconds
        check_shutdown_button()

        time.sleep(1)
except KeyboardInterrupt:
    print("Script interrupted by user.")
finally:
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
