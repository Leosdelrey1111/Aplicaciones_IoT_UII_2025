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
MQTT_CLIENT_ID = "sensor_gas_mq5"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "blhd/sensor/gas_MQ5"

sensor_analogico = ADC(Pin          (34)) 
sensor_analogico.atten(ADC.ATTN_11DB)

sensor_digital = Pin(15, Pin.IN)

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

def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}")
    return client

def leer_concentracion_gas():
    valor_analogico = sensor_analogico.read() 
    estado_digital = sensor_digital.value() 

    print(f"Valor del sensor MQ-5 (AO): {valor_analogico}")
    print(f"Estado del sensor MQ-5 (DO): {estado_digital}")

    if estado_digital == 0: 
        return "ALERTA: Alto nivel de gas detectado"
    elif valor_analogico < 400:
        return "Aire limpio"
    elif valor_analogico < 1000:
        return "Gas presente en el ambiente"
    else:
        return "ALERTA: Concentración alta de gas"

if conectar_wifi():
    client = conectar_broker()

while True:
    estado_gas = leer_concentracion_gas()
    print(f"Concentración de gas: {estado_gas}")

    client.publish(MQTT_TOPIC_PUB, estado_gas)

    time.sleep(3)