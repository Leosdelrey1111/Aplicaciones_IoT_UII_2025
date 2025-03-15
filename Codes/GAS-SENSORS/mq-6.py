from umqtt.simple import MQTTClient
from machine import ADC, Pin
import network
import time

# 📡 Configuración de WiFi
WIFI_SSID = "LEO"
WIFI_PASSWORD = "94941890"

# 🌐 Configuración del broker MQTT
MQTT_BROKER = "192.168.59.200"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "sensor_gas_mq6"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "blhd/sensor/gasMQ6"

# 🎛️ Configuración de sensores
sensor_analogico = ADC(Pin(34))  # Entrada analógica
sensor_analogico.atten(ADC.ATTN_11DB)  # Rango de lectura de 0 a 3.3V
sensor_digital = Pin(27, Pin.IN)  # Entrada digital

# 📶 Conexión a WiFi
def conectar_wifi():
    print("🔄 Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    start_time = time.time()
    while not sta_if.isconnected():
        if time.time() - start_time > 10:
            print("\n❌ Error: Tiempo de espera agotado.")
            return False
        print(".", end="")
        time.sleep(0.5)

    print("\n✅ WiFi Conectada!")
    print("📡 IP:", sta_if.ifconfig()[0])
    return True

# 🔌 Conexión al broker MQTT con reconexión automática
def conectar_broker():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=60)
        client.connect()
        print(f"✅ Conectado a MQTT Broker: {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"❌ Error conectando a MQTT: {e}")
        return None

# 📊 Lectura del sensor de gas
def leer_concentracion_gas():
    valor_analogico = sensor_analogico.read()  # Lectura AO (0-4095)
    valor_digital = sensor_digital.value()  # Lectura DO (0 o 1)

    print(f"📊 Valor AO: {valor_analogico} | DO: {valor_digital}")

    # Definir niveles de gas en base a la lectura analógica
    if valor_analogico < 1000:
        estado_gas = "Bajo nivel de gas"
    elif valor_analogico < 2500:
        estado_gas = "Moderado - Precaución con el gas"
    else:
        estado_gas = "⚠️ ¡ALTO! Peligro: se detecta mucho gas"

    # Evaluar la salida digital
    if valor_digital == 1:
        estado_gas += " (No se detectó gas)"
    else:
        estado_gas += " (🚨 Se detecta gas, ¡¡¡CUIDADO!!!)"

    return estado_gas

# 🔄 Bucle principal con manejo de errores y reconexión
if conectar_wifi():
    client = conectar_broker()

while True:
    try:
        if not client:
            print("🔄 Reintentando conexión a MQTT...")
            client = conectar_broker()

        estado_gas = leer_concentracion_gas()
        print(f"📢 Publicando: {estado_gas}")

        if client:
            client.publish(MQTT_TOPIC_PUB, estado_gas)

    except OSError as e:
        print(f"❌ Error MQTT: {e}. Intentando reconectar...")
        client = conectar_broker()

    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    time.sleep(3)
