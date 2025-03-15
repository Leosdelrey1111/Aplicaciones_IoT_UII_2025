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
mqtt_topic = "blhd/cmagnetismo"  # Tema MQTT para el sensor KY-021

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
sensor_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # Pin del sensor KY-021

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
client = MQTTClient("ESP32_KY021", mqtt_server)
conectar_mqtt()

try:
    while True:
        # Leer el estado del sensor KY-021
        sensor_state = sensor_pin.value()
        
        # Publicar el estado del sensor en el broker MQTT
        if sensor_state == 0:  # Imán detectado
            message = "¡Imán detectado!"
        else:  # No hay imán
            message = "No hay imán."

        # Enviar los datos al topic de MQTT
        publicar_mensaje(message)
        print(message)
        
        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

except KeyboardInterrupt:
    try:
        if client.is_connected():
            client.disconnect()
    except Exception as e:
        print("Error al desconectar:", e)
    print("Programa terminado")
