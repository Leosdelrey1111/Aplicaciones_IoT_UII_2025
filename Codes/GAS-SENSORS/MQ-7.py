from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración de Wi-Fi
SSID = 'LEO'  # Nombre de la red Wi-Fi
PASSWORD = '94941890'  # Contraseña de la red Wi-Fi

# 🌐 Configuración de MQTT
MQTT_SERVER = '192.168.196.200'  # Dirección del broker Mosquitto
MQTT_PORT = 1883  # Puerto del broker Mosquitto
MQTT_TOPIC = "blhd/sensores/mq7"  # Tema MQTT para el sensor MQ-7

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

# 🔧 Configuración de pines del sensor MQ-7
mq7_analog = ADC(Pin(34))  # Salida AO del MQ-7 a GPIO34
mq7_analog.atten(ADC.ATTN_11DB)  # Rango de 0-3.3V

mq7_digital = Pin(27, Pin.IN)  # Salida DO del MQ-7 a GPIO27

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
client = MQTTClient("ESP32_MQ7", MQTT_SERVER)
conectar_mqtt()

try:
    while True:
        # 📊 Leer valores del sensor MQ-7
        mq7_value = mq7_analog.read()  # Lectura analógica (0-4095)
        mq7_alert = mq7_digital.value()  # Lectura digital (0 = gas detectado, 1 = normal)

        # 📢 Crear mensaje
        if mq7_alert == 0:
            message = f"ALERTA: Gas CO detectado - Nivel: {mq7_value}"
        else:
            message = f"Normal - Nivel de gas: {mq7_value}"

        # 📡 Enviar datos por MQTT
        print(message)
        publicar_mensaje(message)

        time.sleep(2)  # Esperar 2 segundos antes de la siguiente lectura

except KeyboardInterrupt:
    print("Prueba finalizada.")
