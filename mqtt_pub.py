import paho.mqtt.client as mqtt
import json

# Read data from output.json
with open("output.json") as f:
    data = json.load(f)

# Connect to your local Mosquitto broker
client = mqtt.Client()
client.connect("172.20.10.11", 1883)
client.loop_start()

client.publish("smartdevices/jsondata", json.dumps(data))
print("Data published to MQTT topic: smartdevices/jsondata")
client.loop_stop()
client.disconnect()
