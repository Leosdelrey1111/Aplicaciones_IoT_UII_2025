from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración de Wi-Fi
SSID = 'LEO'  # Nombre de la red Wi-Fi
PASSWORD = '94941890'  # Contraseña de la red Wi-Fi

# 🌐 Configuración de MQTT
MQTT_SERVER = '192.168.243.200'  # Dirección del broker Mosquitto
MQTT_PORT = 1883  # Puerto del broker Mosquitto
MQTT_TOPIC = "blhd/sensores/linea"  # Tema MQTT para el sensor KY-033

# 🔌 Conectar a Wi-Fi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print('Conexión Wi-Fi establecida:', wlan.ifconfig())

# 🔗 Configuración de pines del sensor KY-033
sensor_pin = Pin(12, Pin.IN)  # Asegúrate de usar el pin correcto (aquí se usa GPIO 12)

# 🔗 Función para conectar al broker MQTT
def conectar_mqtt():
    try:
        client.connect()
    except Exception as e:
        print("Error al conectar al broker MQTT:", e)
        time.sleep(5)
        conectar_mqtt()

# 📤 Función para publicar mensajes al broker MQTT
def publicar_mensaje(message):
    try:
        client.publish(MQTT_TOPIC, message)
    except OSError as e:
        print("Error al publicar el mensaje:", e)
        try:
            if client.is_connected():
                client.disconnect()
        except Exception as ex:
            print("Error al intentar desconectar:", ex)
        time.sleep(5)
        conectar_mqtt()
        publicar_mensaje(message)

# 🚀 Conectar a Wi-Fi
conectar_wifi()

# 🔗 Configuración MQTT
client = MQTTClient("ESP32_LineSensor", MQTT_SERVER)
conectar_mqtt()

try:
    while True:
        # Lee el valor del sensor
        sensor_value = sensor_pin.value()

        # Crear el mensaje basado en el estado del sensor
        if sensor_value == 1:
            message = "Línea detectada"
        else:
            message = "Sin línea detectada"

        # 📡 Enviar datos por MQTT
        print(message)
        publicar_mensaje(message)

        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

except KeyboardInterrupt:
    print("Prueba finalizada.")
