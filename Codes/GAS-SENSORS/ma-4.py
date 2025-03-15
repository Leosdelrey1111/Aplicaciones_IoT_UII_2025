from umqtt.simple import MQTTClient
from machine import ADC, Pin
import network
import time

# Configuración WiFi
WIFI_SSID = "LEO"
WIFI_PASSWORD = "94941890"

# Configuración MQTT
MQTT_BROKER = "192.168.59.200"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "sensor_gas"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "blhd/sensor/gasMQ4"

# Configuración del sensor MQ-4
sensor_gas = ADC(Pin(34))  # MQ-4 conectado al pin 34
sensor_gas.atten(ADC.ATTN_11DB)  # Configuración para leer valores hasta 3.3V

# Función para conectar a WiFi
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

# Función para conectar al broker MQTT
def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}")
    return client

# Función para leer la concentración de gas
def leer_concentracion_gas():
    valor = sensor_gas.read()  # Leer el valor analógico (0-4095)
    print(f"Valor del sensor MQ-4: {valor}")

    # Clasificación de la concentración de gas
    if valor < 500:
        return "No se detecto gas"
    elif valor < 2000:
        return "Gas moderado"
    else:
        return "Alto nivel de gas - ¡Peligro!"

# Conectar a WiFi y MQTT
if conectar_wifi():
    client = conectar_broker()

# Bucle principal
while True:
    # Leer la concentración de gas
    estado_gas = leer_concentracion_gas()
    print(f"Concentración de gas: {estado_gas}")

    # Publicar el estado en MQTT
    client.publish(MQTT_TOPIC_PUB, estado_gas)

    time.sleep(3)