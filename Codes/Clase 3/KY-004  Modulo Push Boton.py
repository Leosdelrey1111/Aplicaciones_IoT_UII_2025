import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del módulo de botón (KY-004)
BUTTON_PIN = 16  # GPIO donde está conectado el botón
button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Cambia esto a la IP de tu broker
MQTT_PORT = 1883
MQTT_TOPIC = 'sensor/boton'

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

# Crear el cliente MQTT
client = MQTTClient('ESP32_button_client', MQTT_BROKER, port=MQTT_PORT)
client.connect()

# Variable para almacenar el estado anterior del botón
estado_anterior = button.value()

# Publicar el estado del botón en el broker MQTT
try:
    while True:
        estado_actual = button.value()
        if estado_actual != estado_anterior:  # Si hay un cambio en el estado
            if estado_actual == 0:  # Botón presionado (0 en lógica pull-up)
                print("Botón presionado")
                client.publish(MQTT_TOPIC, "Botón presionado")
            else:  # Botón liberado
                print("Botón liberado")
                client.publish(MQTT_TOPIC, "Botón liberado")
            estado_anterior = estado_actual  # Actualizar el estado anterior
        time.sleep(0.1)  # Pequeña pausa para evitar rebotes

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    client.disconnect()