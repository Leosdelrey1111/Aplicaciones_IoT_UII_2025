import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del módulo LED de dos colores (KY-011)
RED_PIN = 15  # GPIO donde está conectado el pin rojo del KY-011
GREEN_PIN = 16  # GPIO donde está conectado el pin verde del KY-011

red_led = machine.Pin(RED_PIN, machine.Pin.OUT)
green_led = machine.Pin(GREEN_PIN, machine.Pin.OUT)

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Cambia esto a la IP de tu broker
MQTT_PORT = 1883
MQTT_TOPIC = 'sensor/led'

# Función para conectar el ESP32 a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print('Conectado a WiFi')

# Conectar al WiFi
connect_wifi()

# Función para manejar mensajes MQTT (puede ser útil para control remoto)
def mqtt_callback(topic, msg):
    print('Mensaje recibido:', topic, msg)
    if msg == b'RED':
        red_led.value(1)  # Encender el LED rojo
        green_led.value(0)  # Apagar el LED verde
        print("LED rojo encendido")
    elif msg == b'GREEN':
        red_led.value(0)  # Apagar el LED rojo
        green_led.value(1)  # Encender el LED verde
        print("LED verde encendido")
    elif msg == b'OFF':
        red_led.value(0)  # Apagar el LED rojo
        green_led.value(0)  # Apagar el LED verde
        print("LEDs apagados")

# Crear el cliente MQTT
client = MQTTClient('ESP32_led_client', MQTT_BROKER, port=MQTT_PORT)
client.set_callback(mqtt_callback)
client.connect()

# Publicar el estado del LED y recibir comandos
# Publicar el estado del LED y recibir comandos
try:
    while True:
        # Escuchar posibles comandos MQTT en el ciclo principal
        client.check_msg()

        # Encender el LED rojo
        red_led.value(1)
        green_led.value(0)
        print("LED rojo encendido")
        client.publish(MQTT_TOPIC, "LED rojo encendido")
        time.sleep(2)

        # Encender el LED verde
        red_led.value(0)
        green_led.value(1)
        print("LED verde encendido")
        client.publish(MQTT_TOPIC, "LED verde encendido")
        time.sleep(2)

        # Apagar ambos LEDs
        red_led.value(0)
        green_led.value(0)
        print("LEDs apagados")
        client.publish(MQTT_TOPIC, "LEDs apagados")
        time.sleep(2)

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    red_led.value(0)  # Apagar el LED rojo al salir
    green_led.value(0)  # Apagar el LED verde al salir
    client.disconnect()
