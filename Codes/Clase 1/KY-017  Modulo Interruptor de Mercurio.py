import machine
import time
import network
import ujson  # Para convertir datos a formato JSON
from umqtt.simple import MQTTClient

# Configuración del KY-017
MERCURY_PIN = 15  # Cambia este número según tu conexión
sensor = machine.Pin(MERCURY_PIN, machine.Pin.IN)

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT (Mosquitto en Node-RED)
MQTT_BROKER = '192.168.137.242'  # IP del servidor MQTT (Mosquitto)
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/sensor/mercurio'

# Función para conectar el ESP32 a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        time.sleep(1)
    
    print('✅ Conectado a WiFi:', wlan.ifconfig())

# Conectar al WiFi
connect_wifi()

# Crear el cliente MQTT
client = MQTTClient('ESP32_client', MQTT_BROKER, port=MQTT_PORT)
client.connect()
print("📡 Conectado al broker MQTT")

# Bucle principal de lectura del sensor y envío de datos en JSON
try:
    while True:
        estado = sensor.value()  # Leer el estado del sensor (0 o 1)

        # Formato de mensaje JSON para Node-RED
        datos = {
            "sensor": "KY-017",
            "estado": "inclinado" if estado == 0 else "vertical",
            "valor": estado,
            "timestamp": time.time()  # Marca de tiempo UNIX
        }

        # Convertir a JSON y enviar por MQTT
        mensaje_json = ujson.dumps(datos)
        print("📤 Enviando:", mensaje_json)
        client.publish(MQTT_TOPIC, mensaje_json)

        time.sleep(1)  # Espera antes de la siguiente lectura

except KeyboardInterrupt:
    print("⛔ Programa detenido por el usuario")
    client.disconnect()
