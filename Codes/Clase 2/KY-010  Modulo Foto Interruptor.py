import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-001 (Sensor de temperatura)
TEMP_SENSOR_PIN = 34  # Pin analógico donde está conectado el sensor
sensor = machine.ADC(machine.Pin(TEMP_SENSOR_PIN))
sensor.width(machine.ADC.WIDTH_10BIT)  # Resolución de 10 bits (0-1023)
sensor.atten(machine.ADC.ATTN_0DB)  # Rango de 0-3.3V

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Ejemplo: '192.168.1.10'
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/sensor/temperature'

# Función para conectar el ESP32 a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print('Conectado a WiFi')

# Conectar al WiFi
connect_wifi()

# Función para publicar mensajes en el broker MQTT
def mqtt_callback(topic, msg):
    print('Mensaje recibido:', topic, msg)

# Crear el cliente MQTT
client = MQTTClient('ESP32_client', MQTT_BROKER, port=MQTT_PORT)
client.set_callback(mqtt_callback)
client.connect()

# Función para convertir el valor del sensor a temperatura en grados Celsius
def read_temperature():
    # Leemos el valor del sensor
    raw_value = sensor.read()
    # Convertimos el valor (0-1023) a temperatura en grados Celsius
    # Esto depende de la calibración del sensor, pero generalmente con un sensor como el KY-001,
    # se utiliza una fórmula que convierte el valor de ADC a temperatura aproximada.
    voltage = (raw_value / 1023) * 3.3  # Convertimos el valor a voltaje (0-3.3V)
    temperature = (voltage - 0.5) * 100  # Fórmula aproximada para obtener la temperatura en Celsius
    return temperature

# Publicar la temperatura en el broker MQTT
try:
    while True:
        # Leer la temperatura del sensor
        temp = read_temperature()
        print("Temperatura:", temp, "°C")
        
        # Publicar la temperatura en el broker MQTT
        client.publish(MQTT_TOPIC, str(temp))
        
        # Esperar 2 segundos antes de la siguiente lectura
        time.sleep(2)

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    client.disconnect()
