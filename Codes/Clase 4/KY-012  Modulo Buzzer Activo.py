import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del buzzer activo
BUZZER_PIN = 15  # Cambia según tu conexión
buzzer = machine.Pin(BUZZER_PIN, machine.Pin.OUT)

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT (Node-RED con Mosquitto)
MQTT_BROKER = '192.168.137.242'  # Dirección de tu servidor Mosquitto
MQTT_PORT = 1883
MQTT_TOPIC_BUZZER = 'blhd/actuador/buzzer'  # Recibir comandos
MQTT_TOPIC_ESTADO = 'blhd/actuador/buzzer'  # Enviar estado a Node-RED

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
        machine.reset()  # Reiniciar el ESP32 si no se conecta

# Función para reconectar MQTT en caso de error
def reconnect_mqtt():
    global client
    try:
        client.disconnect()
    except:
        pass
    print("🔄 Reintentando conexión MQTT...")
    time.sleep(2)  # Pequeña espera antes de reconectar
    client = MQTTClient('ESP32_client', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC_BUZZER)

# Función para manejar mensajes MQTT entrantes
def mqtt_callback(topic, msg):
    global buzzer_active
    mensaje = msg.decode()
    print('📩 Mensaje recibido:', mensaje)
    
    if mensaje.lower() == "on":
        buzzer_active = True
        print("🔊 Buzzer activado")
    elif mensaje.lower() == "off":
        buzzer_active = False
        print("🔇 Buzzer desactivado")

# Conectar al WiFi
connect_wifi()

# Crear el cliente MQTT con keepalive
client = MQTTClient('ESP32_client', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
client.set_callback(mqtt_callback)
client.connect()
client.subscribe(MQTT_TOPIC_BUZZER)
print(f"📡 Suscrito al topic MQTT: {MQTT_TOPIC_BUZZER}")

# Variable de control del buzzer
buzzer_active = True  # Iniciar con el buzzer activado

# Bucle principal
try:
    while True:
        # Si se pierde la conexión WiFi, intentar reconectar
        if not network.WLAN(network.STA_IF).isconnected():
            print("⚠️ Conexión WiFi perdida. Reintentando...")
            connect_wifi()

        try:
            client.check_msg()  # Revisa si hay mensajes MQTT
        except OSError as e:
            print(f"⚠️ Error MQTT ({e}). Intentando reconectar...")
            reconnect_mqtt()

        # Hacer sonar el buzzer automáticamente si está activado
        if buzzer_active:
            buzzer.on()
            mensaje = "🔊 Buzzer encendido"
            print(mensaje)
            client.publish(MQTT_TOPIC_ESTADO, mensaje.encode())  # Enviar a Node-RED
            time.sleep(1)

            buzzer.off()
            mensaje = "🔇 Buzzer apagado"
            print(mensaje)
            client.publish(MQTT_TOPIC_ESTADO, mensaje.encode())  # Enviar a Node-RED
            time.sleep(1)

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    client.disconnect()
