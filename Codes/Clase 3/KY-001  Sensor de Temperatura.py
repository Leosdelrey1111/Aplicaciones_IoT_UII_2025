import machine
import time
import network
from umqtt.simple import MQTTClient
import onewire
import ds18x20

# Configuración del sensor DS18B20
DS18B20_PIN = 4  # Pin donde está conectado el sensor
ow = onewire.OneWire(machine.Pin(DS18B20_PIN))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()  # Escanear dispositivos 1-Wire

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Ejemplo: '192.168.1.10'
MQTT_PORT = 1883
MQTT_TOPIC = 'sensor/temperatura'

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

# Publicar la temperatura
try:
    while True:
        ds.convert_temp()  # Iniciar la conversión de temperatura
        time.sleep_ms(750)  # Esperar a que la conversión se complete
        for rom in roms:
            temp = ds.read_temp(rom)  # Leer la temperatura
            print("Temperatura:", temp, "°C")
            client.publish(MQTT_TOPIC, str(temp))  # Publicar la temperatura en MQTT
        
        # Esperar 5 segundos antes de la siguiente lectura
        time.sleep(5)

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    client.disconnect()