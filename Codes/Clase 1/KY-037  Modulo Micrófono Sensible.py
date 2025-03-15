import network
import time
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración de la red Wi-Fi
wifi_ssid = "LEO"  # Cambia por tu SSID
wifi_password = "94941890"  # Cambia por tu contraseña

# Configuración del broker MQTT
mqtt_broker = "192.168.137.8"  # IP del broker
mqtt_port = 1883
mqtt_topic = "sensores/microfonoSencible"  # Tema MQTT para el micrófono

# Configuración del micrófono
mic_pin = 34  # GPIO de la ESP32 conectado a la salida del micrófono
adc = ADC(Pin(mic_pin))
adc.atten(ADC.ATTN_0DB)  # Configura la atenuación (0 a 3.3V)
adc.width(ADC.WIDTH_12BIT)  # Establece la resolución (12 bits = 4095 niveles)

# Conexión Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Conexión Wi-Fi exitosa:', wlan.ifconfig())

# Conexión MQTT
def connect_mqtt():
    try:
        client = MQTTClient("microfono_client", mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Enviar datos del micrófono por MQTT
def publish_data(client):
    if client is None:
        print("Cliente MQTT no disponible, reintentando conexión...")
        return
    
    try:
        mic_value = adc.read()  # Leer el valor del micrófono
        payload = str(mic_value)  # Convertir el valor a string
        client.publish(mqtt_topic, payload)
        print("Datos enviados:", payload)
    except Exception as e:
        print("Error al leer el micrófono o enviar datos:", e)

# Main
connect_wifi()
client = connect_mqtt()

while True:
    publish_data(client)
    time.sleep(0.1)  # Pequeña pausa antes de la siguiente lectura