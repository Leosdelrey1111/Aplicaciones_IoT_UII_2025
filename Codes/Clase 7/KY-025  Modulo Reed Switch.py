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
mqtt_topic = "blhd/sensores/reed_switch"  # Tema MQTT para el Reed Switch

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
reed_switch_pin = Pin(13, Pin.IN)  # Conectar DO del Reed Switch a GPIO13

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
client = MQTTClient("ESP32_Reed_Switch", mqtt_server)
conectar_mqtt()

try:
    while True:
        reed_switch_state = reed_switch_pin.value()
        
        if reed_switch_state == 0:  # Reed Switch activado
            message = "Reed Switch activado"
            print(message)
        else:  # Reed Switch desactivado
            message = "Reed Switch desactivado"
            print(message)
        
        # Publicar el mensaje al broker MQTT
        publicar_mensaje(message)
        
        time.sleep(1)

except KeyboardInterrupt:
    print("Prueba finalizada.")
