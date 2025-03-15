from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración de Wi-Fi
ssid = 'LEO'  # Nombre de la red Wi-Fi
password = '94941890'  # Contraseña de la red Wi-Fi

# Configuración de MQTT
mqtt_server = '192.168.196.200'  # Dirección del broker Mosquitto
mqtt_port = 1883  # Puerto del broker Mosquitto
mqtt_topic = "blhd/sensores/impacto"  # Tema MQTT para el Sensor de Impacto

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
impacto_pin = Pin(14, Pin.IN)  # Conectar el Sensor de Impacto al GPIO14

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
client = MQTTClient("ESP32_Impacto", mqtt_server)
conectar_mqtt()

try:
    while True:
        impacto_state = impacto_pin.value()  # Leer el valor del sensor de impacto
        
        if impacto_state == 0:  # Impacto detectado (sensor en LOW)
            message = "Impacto detectado"
            print(message)
            publicar_mensaje(message)
        else:  # No hay impacto (sensor en HIGH)
            message = "No hay impacto"
            print(message)
            publicar_mensaje(message)

        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

except KeyboardInterrupt:
    print("Prueba finalizada.")
