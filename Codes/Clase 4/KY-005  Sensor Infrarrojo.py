import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del receptor IR
IR_PIN = 15  # Pin donde está conectado el receptor IR
ir_receiver = machine.Pin(IR_PIN, machine.Pin.IN)

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Cambia esto según tu red
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/sensor/ir'

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

# Función para manejar mensajes MQTT entrantes
def mqtt_callback(topic, msg):
    print('📩 Mensaje recibido:', topic, msg)

# Conectar al WiFi
connect_wifi()

# Crear el cliente MQTT con keepalive
client = MQTTClient('ESP32_client', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
client.set_callback(mqtt_callback)
client.connect()

# Función para recibir señales del receptor IR
def recibir_senal():
    tiempo_inicial = time.ticks_us()
    
    while ir_receiver.value() == 0:  # Esperar pulso inicial
        pass
    
    while ir_receiver.value() == 1:  # Medir duración del pulso
        pass
    
    duracion = time.ticks_diff(time.ticks_us(), tiempo_inicial)
    return duracion

# Bucle principal
try:
    while True:
        # Si se pierde la conexión WiFi, intentar reconectar
        if not network.WLAN(network.STA_IF).isconnected():
            print("⚠️ Conexión WiFi perdida. Reintentando...")
            connect_wifi()
        
        if ir_receiver.value() == 0:  # Si se recibe una señal
            duracion = recibir_senal()
            mensaje = f"Señal IR recibida: {duracion} us"
            print(mensaje)

            try:
                client.publish(MQTT_TOPIC, mensaje.encode())  # Convertir a bytes antes de enviar
            except OSError as e:
                print(f"⚠️ Error MQTT ({e}). Intentando reconectar...")
                reconnect_mqtt()

            time.sleep(0.2)  # Evitar lecturas repetidas

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    client.disconnect()
