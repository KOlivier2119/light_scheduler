import paho.mqtt.client as mqtt
import serial
import time
import os

# Serial port configuration
SERIAL_PORT = '/dev/ttyACM0'  # Correct port for Ubuntu (adjust as needed)
BAUD_RATE = 9600
ser = None

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"[INFO] Serial port {SERIAL_PORT} opened successfully.")
except serial.SerialException as e:
    print(f"[WARNING] Could not open serial port {SERIAL_PORT}: {e}")

# MQTT configuration
MQTT_BROKER = '157.173.101.159'
MQTT_PORT = 1883
MQTT_TOPIC = 'relay/schedule'
COMMAND_FILE = 'relay_cmd.txt'

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[INFO] Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"[ERROR] Connection failed with code {rc}")

def on_message(client, userdata, msg):
    command = msg.payload.decode().strip()
    print(f"[MQTT] Received message: {command} at {time.strftime('%H:%M')}")
    
    # Save command to file
    with open(COMMAND_FILE, 'w') as f:
        f.write(command)
    
    # Send to Arduino only if serial port is open
    if ser and ser.is_open:
        if command == '1':
            ser.write(b"ON\n")
            print(f"[SERIAL] Sent to Arduino: ON at {time.strftime('%H:%M')}")
        elif command == '0':
            ser.write(b"OFF\n")
            print(f"[SERIAL] Sent to Arduino: OFF at {time.strftime('%H:%M')}")
        else:
            print(f"[WARNING] Unknown command received: {command}")
    else:
        print("[WARNING] Serial port not available. Cannot send command.")

# Set up MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[INFO] Stopping...")
    client.loop_stop()
    client.disconnect()
    if ser and ser.is_open:
        ser.close()
        print("[INFO] Serial port closed.")
