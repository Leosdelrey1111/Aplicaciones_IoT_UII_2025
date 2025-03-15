import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

SENSOR_PIN = 4  
MQTT_BROKER = "192.168.137.8"
MQTT_TOPIC = "blhd/sensor/vibracion"
MQTT_CLIENT_ID = "vibration_sensor_{}".format(int(time.time()))
WIFI_SSID = "LEO"
WIFI_PASSWORD = "94941890"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    for _ in range(15):
        if wlan.isconnected():
            print("Wi-Fi conectado:", wlan.ifconfig())
            return wlan
        time.sleep(1)
    
    print("No se pudo conectar a Wi-Fi")
    return None

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("Conectado a MQTT")
        return client
    except Exception as e:
        print("Error MQTT:", e)
        return None

def publish_data(client, sensor):
    if client:
        try:
            state = sensor.value()
            client.publish(MQTT_TOPIC, str(state))
            print("Enviado:", state)
        except Exception as e:
            print("Error al publicar:", e)

wlan = connect_wifi()
if wlan:
    client = connect_mqtt()
    sensor = Pin(SENSOR_PIN, Pin.IN)
    
    while True:
        if not wlan.isconnected():
            print("Wi-Fi desconectado, reconectando...")
            wlan = connect_wifi()
        
        if not client:
            print("Reintentando conexión MQTT...")
            client = connect_mqtt()
        
        publish_data(client, sensor)
        time.sleep(1)
else:
    print("No se pudo conectar a Wi-Fi.")
