import machine
import time
import network
from umqtt.simple import MQTTClient

# Pines del KY-023 (Joystick)
VRX_PIN = 32  # Eje X (Analógico)
VRY_PIN = 33  # Eje Y (Analógico)
SW_PIN = 25   # Botón (Digital)

# Configuración WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.46.200'  # Cambia esto según tu red
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/joystick'

# Configuración de los pines del Joystick
vrx = machine.ADC(machine.Pin(VRX_PIN))
vry = machine.ADC(machine.Pin(VRY_PIN))
vrx.atten(machine.ADC.ATTN_11DB)  # Ajusta para leer el rango completo
vry.atten(machine.ADC.ATTN_11DB)
sw = machine.Pin(SW_PIN, machine.Pin.IN, machine.Pin.PULL_UP)  # Botón con Pull-Up

# Función para conectar a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 10
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
    client = MQTTClient('ESP32_ky023', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
    client.connect()

# Función para normalizar valores de 0-4095 a -100 a 100
def normalizar(valor):
    return int(((valor - 2048) / 2048) * 100)  

# Función para obtener la dirección de X e Y
def obtener_direccion(x, y):
    if x < -50:
        dir_x = "IZQUIERDA"
    elif x > 50:
        dir_x = "DERECHA"
    else:
        dir_x = "CENTRO"

    if y < -50:
        dir_y = "ABAJO"
    elif y > 50:
        dir_y = "ARRIBA"
    else:
        dir_y = "CENTRO"

    return dir_x, dir_y

# Conectar a WiFi y MQTT
connect_wifi()
reconnect_mqtt()

try:
    while True:
        try:
            # Leer valores del Joystick
            x_value = normalizar(vrx.read())
            y_value = normalizar(vry.read())
            button_state = "PRESIONADO" if sw.value() == 0 else "NO PRESIONADO"

            # Obtener la dirección de movimiento
            dir_x, dir_y = obtener_direccion(x_value, y_value)

            # Formatear datos para enviar
            payload = f"X:{x_value},Y:{y_value},Botón:{button_state},DirX:{dir_x},DirY:{dir_y}"
            print(f"📤 Enviando -> {payload}")

            # Publicar en MQTT
            client.publish(MQTT_TOPIC, payload)

            time.sleep(0.5)  # Envía datos cada 500ms
            
        except OSError as e:
            print("⚠️ Error al leer el joystick o enviar datos")
            reconnect_mqtt()

except KeyboardInterrupt:
    print("⛔ Programa detenido por el usuario")
    try:
        client.disconnect()
    except:
        pass
