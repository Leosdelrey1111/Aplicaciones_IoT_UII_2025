from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración de Wi-Fi
SSID = 'LEO'  # Nombre de la red Wi-Fi
PASSWORD = '94941890'  # Contraseña de la red Wi-Fi

# 🌐 Configuración de MQTT
MQTT_SERVER = '192.168.137.191'  # Dirección del broker Mosquitto
MQTT_PORT = 1883  # Puerto del broker Mosquitto
MQTT_TOPIC = "blhd/sensores/encoder"  # Tema MQTT para el sensor KY-040

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

# 🔗 Configuración de pines del encoder (KY-040)
clk_pin = Pin(16, Pin.IN, Pin.PULL_UP)  # Conectado al pin A (CLK)
dt_pin = Pin(17, Pin.IN, Pin.PULL_UP)   # Conectado al pin B (DT)

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
        reconnect_mqtt()

# 🔄 Función para reconectar al MQTT
def reconnect_mqtt():
    try:
        print("Intentando reconectar al broker MQTT...")
        client.connect()
    except Exception as e:
        print("Error al reconectar al broker MQTT:", e)
        time.sleep(5)
        reconnect_mqtt()

# 🚀 Conectar a Wi-Fi
conectar_wifi()

# 🔗 Configuración MQTT
client = MQTTClient("ESP32_Encoder", MQTT_SERVER)
conectar_mqtt()

# Variables para el seguimiento de la rotación
last_clk_state = 0
direction = 0
steps = 0  # Contador de pasos de rotación

try:
    while True:
        clk_state = clk_pin.value()
        dt_state = dt_pin.value()

        # Detecta la dirección de la rotación solo si hay un cambio en el pin CLK
        if clk_state != last_clk_state:
            if dt_state != clk_state:
                direction = 1  # Rotación en sentido horario
            else:
                direction = -1  # Rotación en sentido antihorario

            # Incrementa el contador de pasos de acuerdo a la dirección de rotación
            steps += direction

            # Asegura que el contador de pasos nunca sea negativo
            steps = max(steps, 0)

            # Crear el mensaje basado en la dirección
            if direction == 1:
                message = "Sentido horario"
            else:
                message = "Sentido antihorario"

            # 📡 Enviar datos por MQTT
            print(message)
            publicar_mensaje(message)

        last_clk_state = clk_state
        time.sleep(0.01)  # Espera para evitar lectura demasiado rápida

except KeyboardInterrupt:
    print("Programa finalizado.")
