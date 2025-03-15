import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del pin del relé
RELAY_PIN = 15  # Cambia al GPIO que estés usando
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Cambia esto según tu red
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/actuador/rele'

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
    client = MQTTClient('ESP32_rele', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
    client.connect()

# Función para manejar mensajes MQTT entrantes
def mqtt_callback(topic, msg):
    print('📩 Mensaje recibido:', topic, msg)
    mensaje = msg.decode().strip().lower()

    if mensaje == "on":
        print("🔴 Relé ENCENDIDO")
        relay.value(1)  # Encender relé
    elif mensaje == "off":
        print("⚪ Relé APAGADO")
        relay.value(0)  # Apagar relé

# Conectar al WiFi
connect_wifi()

# Crear el cliente MQTT y suscribirse al tema
client = MQTTClient('ESP32_rele', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
client.set_callback(mqtt_callback)
client.connect()
client.subscribe(MQTT_TOPIC)

print("📡 Esperando comandos MQTT...")

# Bucle principal para alternar el relé cada 2 segundos y escuchar MQTT
try:
    while True:
        # Si se pierde la conexión WiFi, intentar reconectar
        if not network.WLAN(network.STA_IF).isconnected():
            print("⚠️ Conexión WiFi perdida. Reintentando...")
            connect_wifi()

        # Alternar el estado del relé cada 2 segundos
        relay.value(1)
        print("🔴 Encendiendo relé")
        client.publish(MQTT_TOPIC, "Relé encendido".encode())  # Enviar estado a MQTT
        time.sleep(2)

        relay.value(0)
        print("⚪ Apagando relé")
        client.publish(MQTT_TOPIC, "Relé apagado".encode())  # Enviar estado a MQTT
        time.sleep(2)

        # Verificar mensajes MQTT
        client.check_msg()

except KeyboardInterrupt:
    print("🚪 Saliendo del programa")
    client.disconnect()
