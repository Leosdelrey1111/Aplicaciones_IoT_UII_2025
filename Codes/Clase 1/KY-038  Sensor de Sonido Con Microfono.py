import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-038
DIGITAL_PIN = 15  # Pin digital del KY-038
ANALOG_PIN = 32   # Pin analógico del KY-038 (usa un ADC válido en ESP32)

sound_sensor = machine.Pin(DIGITAL_PIN, machine.Pin.IN)
adc = machine.ADC(machine.Pin(ANALOG_PIN))
adc.atten(machine.ADC.ATTN_11DB)  # Ajustar la atenuación para un rango de 0-3.3V

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192. 	.137.242'  # Cambia según tu red
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/sensor/sonido'
MQTT_CLIENT_ID = "ESP32_sonido"

# Función para conectar el ESP32 a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("Conectado a WiFi:", wlan.ifconfig())
    else:
        print("Error al conectar WiFi")

# Conectar al WiFi
connect_wifi()

# Función para conectar a MQTT con reintento automático
def connect_mqtt():
    global client
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print("Conectado al broker MQTT")
        return True
    except OSError as e:
        print(f"Error al conectar MQTT: {e}")
        return False

# Inicializar cliente MQTT
if not connect_mqtt():
    time.sleep(5)  # Esperar antes de reintentar
    connect_mqtt()

# Bucle principal
while True:
    try:
        digital_value = sound_sensor.value()
        analog_value = adc.read()  # Valor entre 0-4095

        if digital_value == 0:
            estado_sonido = "⚡ Ruido Detectado!"
        else:
            estado_sonido = "🔇 Sin ruido detectado"

        print(estado_sonido)
        print(f"Nivel de sonido (analógico): {analog_value}")

        # Intentar publicar en MQTT
        try:
            client.publish(MQTT_TOPIC, f"{estado_sonido} | Nivel: {analog_value}")
        except OSError as e:
            print(f"MQTT Error: {e}")
            connect_mqtt()  # Reintentar conexión si falla

        time.sleep(1)  # Esperar 1 segundo entre lecturas

    except KeyboardInterrupt:
        print("Programa detenido")
        client.disconnect()
        break

