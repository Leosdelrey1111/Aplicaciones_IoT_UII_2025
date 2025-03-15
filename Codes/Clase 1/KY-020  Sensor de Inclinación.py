import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-020
INCLINE_SENSOR_PIN = 15  # Pin donde está conectado el sensor

sensor = machine.Pin(INCLINE_SENSOR_PIN, machine.Pin.IN)  # Configurar el sensor como entrada

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # ⚠️ Asegúrate de que la IP es correcta
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/sensor/inclinacion_ky020'

# Función para conectar el ESP32 a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print('Conectado a WiFi:', wlan.ifconfig())

# Verificar si WiFi sigue conectado
def is_wifi_connected():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

# Conectar al WiFi
connect_wifi()

# Crear el cliente MQTT con keepalive
client = MQTTClient('ESP32_client', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
client.connect()

try:
    while True:
        inclinacion = sensor.value()  # Leer el estado del sensor
        mensaje = "Inclinación detectada" if inclinacion == 0 else "Sin inclinación"
        print(mensaje)

        if is_wifi_connected():
            try:
                client.publish(MQTT_TOPIC, mensaje)
            except OSError as e:
                print(f"⚠️ Error en MQTT: {e}, intentando reconectar...")
                client.connect()  # Reintentar conexión
            
        else:
            print("⚠️ WiFi desconectado, no se envió el mensaje.")

        time.sleep(1)  # Espera antes de la siguiente lectura

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    client.disconnect()
