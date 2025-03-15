from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración de Wi-Fi
SSID = 'LEO'  # Nombre de la red Wi-Fi
PASSWORD = '94941890'  # Contraseña de la red Wi-Fi

# 🌐 Configuración de MQTT
MQTT_SERVER = '192.168.243.200'  # Dirección del broker Mosquitto
MQTT_PORT = 1883  # Puerto del broker Mosquitto
MQTT_TOPIC = "blhd/sensores/led7C"  # Tema MQTT para el LED

# 🔌 Conectar a Wi-Fi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print('Conexión Wi-Fi establecida:', wlan.ifconfig())

# 🔗 Configuración de pines del LED
pin_led = Pin(15, Pin.OUT)  # Asegúrate de usar el pin correcto (aquí se usa GPIO 15)

# 🔗 Función para conectar al broker MQTT
def conectar_mqtt():
    try:
        client.connect()
    except Exception as e:
        print("Error al conectar al broker MQTT:", e)
        time.sleep(5)
        conectar_mqtt()

# 📤 Función para publicar mensajes al broker MQTT
def publicar_mensaje(message):
    try:
        client.publish(MQTT_TOPIC, message)
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

# 🚀 Conectar a Wi-Fi
conectar_wifi()

# 🔗 Configuración MQTT
client = MQTTClient("ESP32_LED", MQTT_SERVER)
conectar_mqtt()

# Función para simplemente encender el LED y dejarlo cambiar de color automáticamente
def cycle_colors():
    # Imprimir cuando comienza el ciclo
    print("INICIO DEL CICLO: El LED se está encendiendo y comenzará a cambiar de color.")
    publicar_mensaje("INICIO DEL CICLO: LED encendido y cambiando de color automáticamente.")
    
    # Enciende el LED durante 10 segundos (ajusta este tiempo según necesites)
    pin_led.on()
    time.sleep(10)  # Ajusta el tiempo de espera a lo que prefieras

    # Imprimir cuando se apaga el LED
    print("FIN DEL CICLO: El LED se apagará ahora después de esperar.")
    publicar_mensaje("FIN DEL CICLO: LED apagado después de ciclo.")

    pin_led.off()   # Apaga el LED después de esperar
    time.sleep(3)   # Espera entre ciclos

# Ciclo para permitir que el LED cambie de color
try:
    while True:
        cycle_colors()

except KeyboardInterrupt:
    print("Prueba finalizada.")
