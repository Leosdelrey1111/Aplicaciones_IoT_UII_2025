from umqtt.simple import MQTTClient
from machine import Pin, ADC
import network
import time


WIFI_SSID = "LEO"
WIFI_PASSWORD = "94941890"


MQTT_BROKER = "192.168.137.191"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "sensor_mq135_esp32"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "blhd/sensor/mq135"

PIN_MQ135 = 34

mq135 = ADC(Pin(PIN_MQ135))
mq135.atten(ADC.ATTN_11DB)  # Configurar el rango de lectura (0-3.3V)

def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    start_time = time.time()
    while not sta_if.isconnected():
        if time.time() - start_time > 10:
            print("\nError al conectar a WiFi: Tiempo de espera agotado")
            return False
        print(".", end="")
        time.sleep(0.3)

    print("\nWiFi Conectada!")
    print("IP:", sta_if.ifconfig()[0])
    return True

# Función para conectar al broker MQTT
def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}")
    return client

# Función para obtener el nivel de gas en PPM (Aproximado)
def leer_mq135():
    valor_adc = mq135.read()  # Lee el valor analógico (0-4095 en ESP32)
    voltaje = valor_adc * (3.3 / 4095)  # Convierte a voltaje
    ppm = valor_adc * (1000 / 4095)  # Conversión estimada a PPM
    return ppm


if conectar_wifi():
    client = conectar_broker()

while True:
    try:
        ppm = leer_mq135()
        mensaje = f"Nivel CO2: {ppm:.2f} PPM"
        print(mensaje)
        
        client.publish(MQTT_TOPIC_PUB, mensaje) 
        
        time.sleep(.5)  
    except OSError as e:
        print(f"Error MQTT: {e}")
        client = conectar_broker()  # Reintentar conexión
