from umqtt.simple import MQTTClient
from machine import Pin, ADC
import network
import time


WIFI_SSID = "LEO"
WIFI_PASSWORD = "94941890"


MQTT_BROKER = "192.168.137.191"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "pulse_sensor_esp32"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "blhd/sensor/pulso"


KY_039_PIN = 35  
sensor = ADC(Pin(KY_039_PIN))
sensor.atten(ADC.ATTN_11DB)  # Ajuste para lecturas de 0V a 3.6V

# Variables para detección de pulsaciones
umbral_pulso = 2000  
ultimo_latido = 0
bpm = 0
bpm_anterior = 0 
ventana_bpm = []
tamanio_ventana = 5

# Calcula promedio de los últimos valores en la lista para obtener una medición más estable y evitar picos o valores erráticos.
def promedio_movil(lista):
    if len(lista) == 0:
        return 0
    return sum(lista) // len(lista)

def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    start_time = time.time()
    while not sta_if.isconnected():
        if time.time() - start_time > 10:
            print("\nError al conectar a WiFi: Tiempo de espera agotado")
            return False
        print(".", end="")
        time.sleep(0.3)

    print("\nWiFi Conectada!")
    print("IP:", sta_if.ifconfig()[0])
    return True


def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}")
    return client

if conectar_wifi():
    client = conectar_broker()


while True:
    try:
       
        valor_pulso = sensor.read()
        
   
        tiempo_actual = time.ticks_ms()  # Obtener tiempo en milisegundos
        if valor_pulso > umbral_pulso:
            if time.ticks_diff(tiempo_actual, ultimo_latido) > 500:  # Evitar detección múltiple en 500ms
                intervalo = time.ticks_diff(tiempo_actual, ultimo_latido) / 1000  # Convertir a segundos
                bpm = int(60 / intervalo)
                ultimo_latido = tiempo_actual

                # Agregar valor al filtro de promedio móvil
                ventana_bpm.appen	d(bpm)
                if len(ventana_bpm) > tamanio_ventana:
                    ventana_bpm.pop(0)  # Elimina el valor más antiguo
                
                bpm_filtrado = promedio_movil(ventana_bpm)

                # Publicar solo si el BPM es diferente al anterior por más de 3 BPM
                if abs(bpm_filtrado - bpm_anterior) > 3:
                    print(f"Pulsaciones detectadas: {bpm_filtrado} BPM")
                    client.publish(MQTT_TOPIC_PUB, str(bpm_filtrado))
                    bpm_anterior = bpm_filtrado  # Actualizar valor anterior
        
        time.sleep(0.1)
        
    except Exception as e:
        print("Error en la conexión MQTT:", e)
        time.sleep(5)
        client = conectar_broker()  # Reintenta conexión si falla