from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración de Wi-Fi
SSID = 'LEO'  # Nombre de la red Wi-Fi
PASSWORD = '94941890'  # Contraseña de la red Wi-Fi

# 🌐 Configuración de MQTT
MQTT_SERVER = '192.168.137.191'  # Dirección del broker Mosquitto
MQTT_PORT = 1883  # Puerto del broker Mosquitto
MQTT_TOPIC = "blhd/sensores/hall"  # Tema MQTT para el sensor KY-035

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

# 🔗 Configuración del pin analógico para el sensor KY-035
sensor_pin = ADC(Pin(34))  # Utiliza el pin 34 para la lectura analógica
sensor_pin.atten(ADC.ATTN_0DB)  # Configura el rango de lectura (0-1.1V)

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
client = MQTTClient("ESP32_HallSensor", MQTT_SERVER)
conectar_mqtt()

try:
    while True:
        # Leer el valor del sensor (valor entre 0 y 4095)
        sensor_value = sensor_pin.read()

        # Crear el mensaje basado en el valor del sensor
        if sensor_value > 2000:
            message = "Campo magnético detectado"
        else:
            message = "Sin campo magnético"

        # 📡 Enviar datos por MQTT
        print(f"Valor del sensor Hall: {sensor_value} - {message}")
        publicar_mensaje(message)

        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

except KeyboardInterrupt:
    print("Prueba finalizada.")
