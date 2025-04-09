import time
from datetime import datetime

from opcua import Client as OPCUAClient
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Global token container
influx_token = None

# MQTT constants (from OPC UA values)
MQTT_BROKER = "challenge.prekit.ch"
MQTT_PORT = 1883
MQTT_USER = "alpamayo"
MQTT_PASS = "alpamayo"
MQTT_TOPIC = "influxdb/token"

# OPC UA constants
OPCUA_URL = "opc.tcp://challenge.prekit.ch:4840"

# Your initials for measurement name
MEASUREMENT = "Tarek The Junied"

# Get InfluxDB config dynamically from OPC UA
def get_influx_config_from_opcua():
    client = OPCUAClient(OPCUA_URL)
    client.connect()

    url = client.get_node("ns=2;i=1").get_value()       # INFLUX_URL
    org = client.get_node("ns=2;i=2").get_value()       # INFLUX_ORG
    bucket = client.get_node("ns=2;i=3").get_value()    # INFLUX_BUCKET

    client.disconnect()
    return url, org, bucket

# MQTT handlers
def on_connect(client, userdata, flags, rc):
    print("🔌 Connected to MQTT, subscribing to topic...")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global influx_token
    payload = msg.payload.decode("utf-8")
    print(f"🔑 Token received via MQTT: {payload}")
    influx_token = payload
    client.disconnect()

def get_token_from_mqtt():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Main logging function
def log_watchdog():
    url, org, bucket = get_influx_config_from_opcua()
    print(f"📦 InfluxDB config: {url} | org={org}, bucket={bucket}")

    # Step 1: Get token from MQTT
    get_token_from_mqtt()

    # Step 2: Connect to OPC UA server
    opc_client = OPCUAClient(OPCUA_URL)
    print("🔗 Connecting to OPC UA server...")
    opc_client.connect()

    try:
        watchdog_node = opc_client.get_node("ns=2;i=6")  # WATCHDOG node
        influx = InfluxDBClient(url=url, token=influx_token, org=org)
        write_api = influx.write_api(write_options=SYNCHRONOUS)

        print("📡 Logging watchdog values to InfluxDB... (60s)")
        start = time.time()
        while time.time() - start < 60:
            try:
                value = watchdog_node.get_value()
                timestamp = datetime.utcnow()
                print(f"⏱️  {timestamp} | watchdog: {value}")

                point = Point(MEASUREMENT).field("value", value).time(timestamp, WritePrecision.NS)
                write_api.write(bucket=bucket, record=point)

                time.sleep(1)
            except Exception as e:
                print(f"⚠️  Error reading OPC UA or writing to Influx: {e}")
                time.sleep(2)
    finally:
        opc_client.disconnect()
        print("✅ Logging complete. OPC UA disconnected.")

if __name__ == "__main__":
    log_watchdog()
