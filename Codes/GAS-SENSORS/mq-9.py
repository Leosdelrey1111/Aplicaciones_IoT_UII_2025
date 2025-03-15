from umqtt.simple import MQTTClient
from machine import Pin, ADC
import network
import time

WIFI_SSID = "LEO"
WIFI_PASSWORD = "94941890"

MQTT_BROKER = "192.168.137.191"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "mq9_sensor_esp32"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "blhd/sensores/mq9"

gas_sensor_pin = ADC(Pin(34))  # Conectado al pin A0 (analógico)
gas_sensor_pin.atten(ADC.ATTN_0DB)  # Establece el rango de 0 a 1.1V

# Umbrales para detección de gases peligrosos
UMBRAL_CO = 1500  # Umbral para Monóxido de Carbono
UMBRAL_GASES = 3500  # Umbral para Gases Inflamables

def leer_sensor():
    return gas_sensor_pin.read()  # Lee el valor analógico del sensor

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

if conectar_wifi():
    client = conectar_broker()

while True:
    try:
        sensor_value = leer_sensor()

        # Mostrar el valor de la lectura analógica
        print(f"Valor analógico del sensor MQ-9: {sensor_value}")

        # Detección de gases peligrosos
        if sensor_value > UMBRAL_CO:
            message = "¡ALERTA! Alta concentración de Monóxido de Carbono detectada."
        elif sensor_value > UMBRAL_GASES:
            message = "¡ALERTA! Gases inflamables detectados."
        else:
            message = "Concentración de gas dentro del rango seguro."

        # Publicar el mensaje en MQTT
        print(message)
        client.publish(MQTT_TOPIC_PUB, message)

        time.sleep(.5)  # Espera 1 segundo antes de la siguiente lectura

    except Exception as e:
        print("Error en la conexión MQTT:", e)
        time.sleep(1)
        client = conectar_broker()  # Reintenta conexión si falla
