import machine
import time
import network
from umqtt.simple import MQTTClient
import dht

DHT_PIN = 2
sensor = dht.DHT11(machine.Pin(DHT_PIN))

WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Cambia esto según tu red
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/actuador/tyhumedad'


# Función para conectar el ESP32 a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 10  # Intentos máximos para conectar
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print('✅ Conectado a WiFi:', wlan.ifconfig())
    else:
        print('❌ Error: No se pudo conectar a WiFi')
        machine.reset()

# Función para reconectar MQTT en caso de error
def reconnect_mqtt():
    global client
    try:
        client.disconnect()
    except:
        pass
    print("🔄 Reintentando conexión MQTT...")
    time.sleep(2)
    client = MQTTClient('ESP32_ky013', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
    client.connect()
    

# Conectar al WiFi
connect_wifi()
connect_mqtt()

try:
    while True:
        try:
            sensor.measure()
            temperatura = sensor.temperatura()
            humedad = sensor.humidity()
            
            playload = f"{temperatura}`C, {humidity}%"
            
            print(f" Enviando - > {playload}")
            Client.publish(MQTT_TOPIC, playload)
            
        except OSError as e:
            print(f"error al leer el sensor o enviar")
            connect_mqtt()
except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    try:
        Client.disconnect()
        except:
            pass