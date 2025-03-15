import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-013
TEMP_PIN = 35  # GPIO donde está conectado
temp_sensor = machine.ADC(machine.Pin(TEMP_PIN))
temp_sensor.atten(machine.ADC.ATTN_11DB)  # Hasta 3.3V
temp_sensor.width(machine.ADC.WIDTH_12BIT)  # Resolución 12-bit (0-4095)

# Configuración de la red WiFi
WIFI_SSID = 'LEO'
WIFI_PASSWORD = '94941890'

# Configuración del broker MQTT
MQTT_BROKER = '192.168.137.242'  # Cambia esto según tu red
MQTT_PORT = 1883
MQTT_TOPIC = 'blhd/actuador/tanalogica'

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
    client = MQTTClient('ESP32_ky013', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
    client.connect()

# Función para leer la temperatura
def read_temperature():
    raw_value = temp_sensor.read()  # Leer valor del sensor
    voltage = (raw_value / 4095.0) * 3.3  # Convertir a voltaje (0-3.3V)
    temperature_c = (voltage - 0.5) * 100  # Conversión aproximada a °C
    return temperature_c

# Conectar al WiFi
connect_wifi()

# Crear cliente MQTT
client = MQTTClient('ESP32_ky013', MQTT_BROKER, port=MQTT_PORT, keepalive=60)
client.connect()

print("📡 Enviando temperatura a MQTT...")

# Bucle principal
try:
    while True:
        # Si se pierde la conexión WiFi, reconectar
        if not network.WLAN(network.STA_IF).isconnected():
            print("⚠️ Conexión WiFi perdida. Reintentando...")
            connect_wifi()

        temperature = read_temperature()
        mensaje = f"🌡️ Temperatura: {temperature:.2f} °C"
        print(mensaje)

        try:
            client.publish(MQTT_TOPIC, mensaje.encode())  # Convertir a bytes antes de enviar
        except OSError as e:
            print(f"⚠️ Error MQTT ({e}). Intentando reconectar...")
            reconnect_mqtt()

        time.sleep(2)  # Leer cada 2 segundos

except KeyboardInterrupt:
    print("🚪 Saliendo del programa")
    client.disconnect()
