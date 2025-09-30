import paho.mqtt.client as mqtt
import ssl
import time

def on_connect(client, userdata, flags, rc, xyz):
    print(xyz)
    if rc == 0:
        print("Connected successfully")
        # client.subscribe("test/subscribe_topic")  # Subscribe to a topic
    else:
        print("Connection failed with code", rc)

def on_message(client, userdata, message):
    print(f"Received message on {message.topic}: {message.payload.decode()}")

# def on_subscribe(client, userdata, mid, granted_qos,xyz):
#     print("Subscribed successfully")

client_id = "basicPubSub"
ca_cert = "cert.pem"
client_cert = "test_lte.cert.pem"
client_key = "test_lte.private.key"
broker = "a6kvi1np2cmrt-ats.iot.ap-south-1.amazonaws.com"
port = 8883

client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)
client.tls_set(ca_certs=ca_cert, certfile=client_cert, keyfile=client_key)

client.on_connect = on_connect
client.on_message = on_message
# client.on_subscribe = on_subscribe

try:
    client.connect(broker, port=port)
    client.loop_start()
    print("MQTT client started")
except Exception as e:
    print("Connection error:", e)
    raise
