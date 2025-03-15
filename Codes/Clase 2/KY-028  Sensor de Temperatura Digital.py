import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

DIGITAL_PIN = 4  # Pin digital donde está conectado el DO del KY-028
MQTT_BROKER = "192.168.137.8"
MQTT_TOPIC = "blhd/sensor/temp-digital"
MQTT_CLIENT_ID = "temp_sensor_{}".format(int(time.time()))
WIFI_SSID = "LEO"
WIFI_PASSWORD = "94941890"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(10):
        if wlan.isconnected():
            print("Wi-Fi conectado:", wlan.ifconfig())
            return True
        time.sleep(1)
    print("No se pudo conectar a Wi-Fi")
    return False

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
        digital_value = sensor.value()  # 0 si la temperatura supera el umbral, 1 si está por debajo
        client.publish(MQTT_TOPIC, str(digital_value))
        print("Enviado:", digital_value)

if connect_wifi():
    client = connect_mqtt()
    sensor = Pin(DIGITAL_PIN, Pin.IN)  # Configurar DO como entrada digital

    while True:
        publish_data(client, sensor)
        time.sleep(2)  # Ajusta el tiempo de muestreo si es necesario
else:
    print("No se pudo conectar a Wi-Fi.")
