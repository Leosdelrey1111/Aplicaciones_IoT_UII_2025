from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient
import ujson  # Importar ujson para manejar JSON en MicroPython

# Configuración de Wi-Fi
ssid = 'LEO'  # Nombre de la red Wi-Fi
password = '94941890'  # Contraseña de la red Wi-Fi

# Configuración de MQTT
mqtt_server = '192.168.46.200'  # Dirección del broker Mosquitto
mqtt_topic = "blhd/sensores/magnetico"  # Tópico único

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
sensor_digital = Pin(14, Pin.IN)  # Salida digital del sensor
sensor_analogico = ADC(Pin(34))  # Entrada analógica del sensor
sensor_analogico.atten(ADC.ATTN_11DB)  # Rango completo (0-3.3V)

# Cliente MQTT
client = MQTTClient("ESP32", mqtt_server)

# Función para conectar al broker MQTT con reintentos
def conectar_mqtt():
    global client
    try:
        print("Conectando al broker MQTT...")
        client.connect()
        print("Conectado al broker MQTT")
    except Exception as e:
        print("Error al conectar al broker MQTT:", e)
        time.sleep(5)
        client = MQTTClient("ESP32", mqtt_server)  # Reiniciar cliente MQTT
        conectar_mqtt()

# Función para publicar mensajes al broker MQTT con reintento en caso de error
def publicar_mensaje(topic, message):
    try:
        # Convertir mensaje a una cadena JSON antes de enviarlo
        message_str = ujson.dumps(message)
        client.publish(topic, message_str)  # Publicar como string JSON
        print(f"📤 Publicado en {topic}: {message_str}")  # Mostrar mensaje enviado
    except OSError as e:
        print("Error al publicar el mensaje:", e)
        time.sleep(5)
        conectar_mqtt()  # Reconectar MQTT
        client.publish(topic, message_str)

# Conectar a Wi-Fi
conectar_wifi()

# Conectar al broker MQTT
conectar_mqtt()

try:
    while True:
        # Leer valores del sensor
        digital_state = sensor_digital.value()  # 0 o 1
        analog_value = sensor_analogico.read()  # Valor entre 0 y 4095
        
        # Determinar estado digital
        estado_magnetico = "Detectado" if digital_state == 1 else "No detectado"
        
        # Crear un mensaje en formato JSON
        mensaje_json = {
            "estado_digital": estado_magnetico,
            "valor_analogico": analog_value
        }
        
        # Publicar datos en MQTT
        publicar_mensaje(mqtt_topic, mensaje_json)
        
        # Mostrar datos en consola
        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

except KeyboardInterrupt:
    print("Programa terminado")
