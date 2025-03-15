from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración de Wi-Fi
ssid = 'LEO'  # Nombre de la red Wi-Fi
password = '94941890'  # Contraseña de la red Wi-Fi

# Configuración de MQTT
mqtt_server = '192.168.46.200'  # Dirección del broker Mosquitto
mqtt_port = 1883  # Puerto del broker Mosquitto
mqtt_topic = "blhd/sensores/infrarrojos"  # Tema MQTT para el emisor IR KY-005

# Conexión Wi-Fi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Conexión Wi-Fi establecida:', wlan.ifconfig())

# Configuración de pines
ky005_pin = Pin(15, Pin.OUT)  # Pin del emisor infrarrojo KY-005

# Función para conectar al broker MQTT
def conectar_mqtt():
    try:
        client.connect()
    except Exception as e:
        print("Error al conectar al broker MQTT:", e)
        time.sleep(5)
        conectar_mqtt()

# Función para publicar mensajes al broker MQTT
def publicar_mensaje(message):
    try:
        client.publish(mqtt_topic, message)
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

# Conectar a Wi-Fi
conectar_wifi()

# Configuración MQTT
client = MQTTClient("ESP32_KY005", mqtt_server)
conectar_mqtt()

try:
    while True:
        # Enviar señal infrarroja
        ky005_pin.value(1)  # Activar emisión IR
        message = "Enviando señal IR..."
        publicar_mensaje(message)
        print(message)
        time.sleep(0.5)  # Mantener encendido por 500ms

   
except KeyboardInterrupt:
    print("Prueba finalizada.")
