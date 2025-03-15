import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor LDR
LDR_PIN = 34  # GPIO36 (VP)
ldr = machine.ADC(machine.Pin(LDR_PIN))
ldr.atten(machine.ADC.ATTN_11DB)  # Permite leer hasta 3.3V
ldr.width(machine.ADC.WIDTH_12BIT)  # Resolución 12-bit (0-4095)

# Rango de calibración del LDR (ajustar según tus mediciones)
LDR_MIN = 200   # Valor con más luz
LDR_MAX = 4000  # Valor con menos luz

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Cambia esto según tu red
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/sensor/ldr'

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
    client.connect()

# Función para obtener la media de varias lecturas
def get_ldr_value(samples=10):
    total = 0
    for _ in range(samples):
        total += ldr.read()
        time.sleep(0.05)  # Pequeña pausa entre lecturas
    avg_value = total // samples  # Promedio de las lecturas
    
    # Normalizar a un porcentaje (0-100%)
    luz_percent = max(0, min(100, 100 - ((avg_value - LDR_MIN) / (LDR_MAX - LDR_MIN) * 100)))
    return avg_value, luz_percent

# Conectar al WiFi
connect_wifi()

# Crear el cliente MQTT con keepalive
client = MQTTClient('ESP32_client', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
client.connect()

# Bucle principal
try:
    while True:
        # Si se pierde la conexión WiFi, intentar reconectar
        if not network.WLAN(network.STA_IF).isconnected():
            print("⚠️ Conexión WiFi perdida. Reintentando...")
            connect_wifi()

        raw_value, luz_percent = get_ldr_value()
        mensaje = f"Luz detectada: {raw_value} (≈ {luz_percent:.1f}%)"
        print(mensaje)

        try:
            client.publish(MQTT_TOPIC, mensaje.encode())  # Convertir a bytes antes de enviar
        except OSError as e:
            print(f"⚠️ Error MQTT ({e}). Intentando reconectar...")
            reconnect_mqtt()

        time.sleep(1)  # Leer cada segundo

except KeyboardInterrupt:
    print("Programa detenido por el usuario")
    client.disconnect()
