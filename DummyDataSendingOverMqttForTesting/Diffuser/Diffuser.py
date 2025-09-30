import paho.mqtt.client as mqttClient
from time import sleep

class MQTTClient:
    def __init__(self, dev_Id, pmax, broker_address, port):
        self.dev_Id = dev_Id
        self.pmax = pmax
        self.broker_address = broker_address
        self.port = port
        self.connected = False
        self.client = mqttClient.Client("Diffuser")
        self.client.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            self.connected = True
        else:
            print("Connection failed")

    def run(self):
        self.client.connect(self.broker_address, port=self.port)
        self.client.loop_start()

        while not self.connected:
            sleep(0.1)

        try:
            while True:
                sleep(0.1)
                # value = "Data From Mqtt - >" + "pmax:" + str(self.pmax)
                self.client.publish(self.dev_Id + "/status", DiffuserData)

        except KeyboardInterrupt:
            self.client.disconnect()
            self.client.loop_stop()

# Usage example
dev_Id = "DiffuserAABBDD"
# pmax = 1000
DiffuserData = dev_Id + ":1:12:34:15:45"
# broker_address = "203.109.124.70"
broker_address = "107.180.94.60"
port = 18889

mqtt_client = MQTTClient(dev_Id, DiffuserData, broker_address, port)
mqtt_client.run()