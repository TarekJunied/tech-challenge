import paho.mqtt.client as mqtt

MQTT_BROKER = "challenge.prekit.ch"
MQTT_PORT = 1883  # Standard port for unencrypted MQTT
MQTT_USER = "alpamayo"
MQTT_PASS = "alpamayo"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("#")  # Subscribe to all topics

def on_message(client, userdata, msg):
    print(f"\n📩 Topic: {msg.topic}")
    print(f"📦 Payload: {msg.payload.decode('utf-8')}")

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
