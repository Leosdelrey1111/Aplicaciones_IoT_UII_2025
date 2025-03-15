import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del módulo láser
LASER_PIN = 15  # GPIO donde está conectado el KY-008
laser = machine.Pin(LASER_PIN, machine.Pin.OUT)

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Cambia esto a la IP de tu broker
MQTT_PORT = 1883
MQTT_TOPIC = 'sensor/laser'

# Función para conectar el ESP32 a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        print("Conectando a WiFi...")
        time.sleep(1)
    print('Conectado a WiFi:', wlan.ifconfig())

# Función para manejar mensajes MQTT
def mqtt_callback(topic, msg):
    print('Mensaje recibido:', topic, msg)
    if msg == b'ON':
        laser.value(1)  # Enciende el láser
        print("Láser encendido")
    elif msg == b'OFF':
        laser.value(0)  # Apaga el láser
        print("Láser apagado")

# Función para conectar MQTT
def connect_mqtt():
    client = MQTTClient('ESP32_laser_client', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
    client.set_callback(mqtt_callback)
    try:
        client.connect()
        print("Conectado al broker MQTT")
    except Exception as e:
        print("Error al conectar MQTT:", e)
        time.sleep(5)
        machine.reset()  # Reinicia el ESP32 en caso de error
    return client

# Conectar WiFi y MQTT
connect_wifi()
client = connect_mqtt()

# Bucle principal con manejo de reconexión
try:
    while True:
        if not network.WLAN(network.STA_IF).isconnected():
            print("WiFi desconectado. Intentando reconectar...")
            connect_wifi()

        try:
            laser.value(1)
            print("Láser encendido")
            client.publish(MQTT_TOPIC, "Láser encendido")
            time.sleep(5)

            laser.value(0)
            print("Láser apagado")
            client.publish(MQTT_TOPIC, "Láser apagado")
            time.sleep(5)
            
            client.check_msg()  # Escuchar comandos MQTT
        except OSError as e:
            print("Error MQTT, intentando reconectar:", e)
            client = connect_mqtt()
except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    laser.value(0)  # Apagar el láser al salir
    client.disconnect()
