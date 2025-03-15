from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración de Wi-Fi
ssid = 'LEO'  # Nombre de la red Wi-Fi
password = '94941890'  # Contraseña de la red Wi-Fi

# Configuración de MQTT
mqtt_server = '192.168.137.8'  # Dirección del broker Mosquitto
mqtt_port = 1883  # Puerto del broker Mosquitto
mqtt_topic = "sensores/vibracion"  # Tema MQTT para la vibración

# Conexión Wi-Fi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Conexión Wi-Fi establecida:', wlan.ifconfig())

# Configuración de pines
sensor_pin = Pin(14, Pin.IN)  # Pin de entrada del sensor de vibración
led_pin = Pin(12, Pin.OUT)  # Pin de salida para LED

# Función para conectar al broker MQTT
def conectar_mqtt():
    try:
        client.connect()
    except Exception as e:
        print("Error al conectar al broker MQTT:", e)
        time.sleep(5)
        conectar_mqtt()

# Función para publicar mensajes al broker MQTT
def publicar_mensaje(message):
    try:
        client.publish(mqtt_topic, message)
    except OSError as e:
        print("Error al publicar el mensaje:", e)
        try:
            if client.is_connected():
                client.disconnect()
        except Exception as ex:
            print("Error al intentar desconectar:", ex)
        time.sleep(5)
        conectar_mqtt()
        publicar_mensaje(message)

# Conectar a Wi-Fi
conectar_wifi()

# Configuración MQTT
client = MQTTClient("ESP32", mqtt_server)
conectar_mqtt()

try:
    while True:
        # Leer el estado del sensor de vibración
        sensor_state = sensor_pin.value()
        
        # Publicar el estado del sensor en el broker MQTT
        if sensor_state == 1:  # Vibración detectada
            message = "Vibración detectada"
            led_pin.value(1)  # Encender el LED
        else:  # Sin vibración
            message = "No hay vibración"
            led_pin.value(0)  # Apagar el LED

        # Enviar los datos al topic de MQTT
        publicar_mensaje(message)
        print(message)
        
        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

except KeyboardInterrupt:
    # Limpiar el LED y desconectar
    led_pin.value(0)
    try:
        if client.is_connected():
            client.disconnect()
    except Exception as e:
        print("Error al desconectar:", e)
    print("Programa terminado")
