from machine import Pin, PWM
import time
import network
from umqtt.simple import MQTTClient
import ubinascii
import machine

# Configuración de Wi-Fi
SSID = "LEO"
PASSWORD = "94941890"

# Configuración de MQTT
MQTT_BROKER = "192.168.137.8"
MQTT_PORT = 1883
MQTT_TOPIC = "led/rgb"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id()).decode()

# Conectar a Wi-Fi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a Wi-Fi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print("Conectado a Wi-Fi:", wlan.ifconfig())

# Configuración de pines PWM para el LED RGB
RED_PIN = PWM(Pin(21))   # Pin GPIO 15 para Rojo
GREEN_PIN = PWM(Pin(22)) # Pin GPIO 14 para Verde
BLUE_PIN = PWM(Pin(23))  # Pin GPIO 13 para Azul

for pin in [RED_PIN, GREEN_PIN, BLUE_PIN]:
    pin.freq(1000)

# Función para conectar al broker MQTT
def conectar_mqtt():
    global mqtt_client
    try:
        mqtt_client.connect()
        print("Conectado al broker MQTT")
    except Exception as e:
        print("Error al conectar a MQTT:", e)
        time.sleep(5)
        conectar_mqtt()

# Función para publicar mensajes en MQTT
def publicar_mensaje(message):
    try:
        mqtt_client.publish(MQTT_TOPIC, message)
    except OSError as e:
        print("Error al publicar el mensaje:", e)
        try:
            if mqtt_client.is_connected():
                mqtt_client.disconnect()
        except Exception as ex:
            print("Error al intentar desconectar:", ex)
        time.sleep(5)
        conectar_mqtt()
        publicar_mensaje(message)

# Función para cambiar el color del LED
def set_color(red, green, blue):
    RED_PIN.duty_u16(int(red * 65535 / 255))
    GREEN_PIN.duty_u16(int(green * 65535 / 255))
    BLUE_PIN.duty_u16(int(blue * 65535 / 255))

    # Enviar solo el color que está activo en formato texto
    if red > 0 and green == 0 and blue == 0:
        color_data = 'rojo'
        print("Color enviado:", color_data)
        publicar_mensaje(color_data)
    elif green > 0 and red == 0 and blue == 0:
        color_data = 'verde'
        print("Color enviado:", color_data)
        publicar_mensaje(color_data)
    elif blue > 0 and red == 0 and green == 0:
        color_data = 'azul'
        print("Color enviado:", color_data)
        publicar_mensaje(color_data)

# Iniciar conexiones
conectar_wifi()
mqtt_client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
conectar_mqtt()

# Bucle principal para cambiar colores y enviar datos MQTT
try:
    while True:
        set_color(255, 0, 0)  # Rojo
        time.sleep(1)
        set_color(0, 255, 0)  # Verde
        time.sleep(1)
        set_color(0, 0, 255)  # Azul
        time.sleep(1)

except KeyboardInterrupt:
    # Apagar LED y desconectar MQTT
    set_color(0, 0, 0)
    try:
        if mqtt_client.is_connected():
            mqtt_client.disconnect()
    except Exception as e:
        print("Error al desconectar:", e)

    print("Programa terminado")
