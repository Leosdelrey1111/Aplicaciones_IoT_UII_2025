import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del buzzer pasivo (requiere PWM)
BUZZER_PIN = 15  # Cambia según tu conexión
buzzer = machine.PWM(machine.Pin(BUZZER_PIN))

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT (Node-RED con Mosquitto)
MQTT_BROKER = '192.168.137.242'  # Dirección de tu servidor Mosquitto
MQTT_PORT = 1883
MQTT_TOPIC_BUZZER = 'blhd/actuador/buzzer'  # Recibir comandos
MQTT_TOPIC_ESTADO = 'blhd/actuador/buzzer/pass'  # Enviar estado a Node-RED

# Notas musicales (frecuencia en Hz)
NOTAS = {
    "C4": 261, "D4": 294, "E4": 329, "F4": 349, "G4": 392, "A4": 440, "B4": 493,
    "C5": 523, "D5": 587, "E5": 659, "F5": 698, "G5": 784, "A5": 880, "B5": 987
}

# Melodía a tocar
MELODIA = [
    ("C4", 0.3), ("E4", 0.3), ("G4", 0.3), ("C5", 0.6),
    ("G4", 0.3), ("A4", 0.3), ("G4", 0.6), ("E4", 0.3),
    ("C4", 0.3), ("D4", 0.3), ("E4", 0.6)
]

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
        print("🎵 Buzzer activado")
    elif mensaje.lower() == "off":
        buzzer_active = False
        print("🔇 Buzzer desactivado")

# Función para reproducir una melodía
def reproducir_melodia():
    for nota, duracion in MELODIA:
        if not buzzer_active:
            break  # Si se apaga el buzzer, detener la melodía
        frecuencia = NOTAS.get(nota, 0)
        if frecuencia > 0:
            buzzer.freq(frecuencia)  # Establecer frecuencia
            buzzer.duty(512)  # Activar sonido (duty cycle 50%)
            print(f"🎶 Reproduciendo nota: {nota}")
            client.publish(MQTT_TOPIC_ESTADO, f"🎶 Reproduciendo nota: {nota}".encode())
        time.sleep(duracion)
        buzzer.duty(0)  # Apagar el sonido entre notas
        time.sleep(0.1)  # Pequeño delay entre notas

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

        # Reproducir melodía automáticamente si está activado
        if buzzer_active:
            print("🎵 Reproduciendo melodía...")
            client.publish(MQTT_TOPIC_ESTADO, "🎵 Reproduciendo melodía...".encode())  # Enviar a Node-RED
            reproducir_melodia()
            time.sleep(2)  # Pausa antes de repetir

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    client.disconnect()
