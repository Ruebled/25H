import time
import adafruit_dht
import requests

# Configurare DHT11
DHT_SENSOR = adafruit_dht.DHT11
DHT_PIN = 4  # Pinul GPIO la care este conectat senzorul

# Configurare API
API_URL = "https://api.example.com/data"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_TOKEN"
}

def read_dht11():
    """Citește datele de la senzorul DHT11."""
    humidity, temperature = adafruit_dht.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print("Temperature: " + temperature + "\nHumidity: " + humidity)
        return {
            "temperature": temperature,
            "humidity": humidity
        }
    else:
        print("Eroare la citirea senzorului DHT11.")
        return None

def send_to_api(data):
    """Trimite datele la API."""
    try:
        response = requests.post(API_URL, json=data, headers=HEADERS)
        if response.status_code == 200:
            print("Datele au fost trimise cu succes:", response.json())
        else:
            print(f"Eroare la trimiterea datelor: {response.status_code} - {response.text}")
    except Exception as e:
        print("Eroare de conexiune la API:", str(e))

def main():
    """Buclează citirea și trimiterea datelor la fiecare 30 de secunde."""
    while True:
        sensor_data = read_dht11()
        if sensor_data:
            print("Date citite:", sensor_data)
            send_to_api(sensor_data)
        time.sleep(30)

if __name__ == "__main__":
    main()

