import paho.mqtt.client as mqtt
import json


def on_message(client, userdata, msg):
    print("✅ Received JSON from MQTT topic!\n")

    data = json.loads(msg.payload.decode())

    print("🔹 Censored Content:")
    print(data.get("censored_content", "[No censored content found]"))

    print("\n🔹 Bad Words Found:")
    for word in data.get("bad_words_list", []):
        print(f"- {word['original']} (replaced with {'*' * word['replacedLen']})")

    print("\n🔹 Total Bad Words:", data.get("bad_words_total", 0))


client = mqtt.Client()
client.on_message = on_message

client.connect("172.20.10.11", 1883)
client.subscribe("smartdevices/jsondata")
print("📡 MQTT Subscriber running. Waiting for messages...\n")
client.loop_forever()
