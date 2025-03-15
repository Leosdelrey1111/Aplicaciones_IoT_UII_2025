import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor MQ-2
MQ2_PIN = 34  # GPIO donde conectaste la salida analógica del MQ-2
sensor_gas = machine.ADC(machine.Pin(MQ2_PIN))
sensor_gas.atten(machine.ADC.ATTN_11DB)  # Ajuste para rango de voltaje de 0 a 3.3V
sensor_gas.width(machine.ADC.WIDTH_12BIT)  # Resolución de 12 bits (0-4095)

# Umbral de detección de gas (ajústalo según pruebas)
UMBRAL_GAS = 2000  

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.59.200'  # Cambia esto según tu red
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/sensor/gasmq2'

# Función para conectar a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print('✅ Conectado a WiFi')

# Conectar al WiFi
connect_wifi()

# Función para manejar mensajes recibidos en MQTT
def mqtt_callback(topic, msg):
    print('📩 Mensaje recibido:', topic.decode(), msg.decode())

# Crear el cliente MQTT y configurar la conexión
client = MQTTClient('ESP32_client', MQTT_BROKER, port=MQTT_PORT)
client.set_callback(mqtt_callback)
client.connect()

# 📌 **Loop principal**
try:
    while True:
        valor = sensor_gas.read()  # Leer el valor del sensor (0-4095)
        print(f"Nivel de gas detectado: {valor}")

        # Enviar lectura al broker MQTT
        client.publish(MQTT_TOPIC, str(valor))

        # Comprobar si el nivel de gas supera el umbral
        if valor > UMBRAL_GAS:
            print("⚠️ ¡Alerta! Nivel alto de gas detectado ⚠️")
            client.publish(MQTT_TOPIC, "⚠️ ¡ALERTA GAS! ⚠️")

        time.sleep(5)  # Esperar 5 segundos antes de la siguiente lectura

except KeyboardInterrupt:
    print("🛑 Programa detenido por el usuario")
    client.disconnect()
