import time
import board
import adafruit_dht
import RPi.GPIO
import json
import requests

# Sensor data pin is connected to GPIO 4
# sensor = adafruit_dht.DHT22(board.D4
# Uncomment for DHT11
sensor = adafruit_dht.DHT11(board.D4)

API_URL = "https://localhost/process"
HEADERS = {
    "Content-Type": "application/json",
    #"Authorization": "Bearer YOUR_API_TOKEN"
}


def initSensors():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(2, GPIO.OUT, initial=GPIO.LOW);


def read_dht11():
    """
    Citește datele de la senzorul DHT11.

    Return(json):
    {
        temperature: 24.5
        humidity: 23
    }
    """
    try:
        # Print the values to the serial port
        temperature_c = sensor.temperature
        #temperature_f = temperature_c * (9 / 5) + 32
        humidity = sensor.humidity
        #print("Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))
        print("Temp " + str(temperature_c) + "\nHum " + str(humidity));

        # return data read as json
        return json.dumps({
            "temperature": temperature_c,
            "humidity": humidity
        })

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        return None

    except Exception as error:
        sensor.exit()
        raise error

def send_to_api(data):
    """
    Send temp and humidity data to the api and receive action response.
    SENT DATA:
    {
        temperature: 24.3,
        humidity: 24
    }
    RESPONSE DATA:
    {
        message: "Temperatura nu este optimala",
        ventilator: "off"
        termistor: "off"
        robinet: "off"
    }
    """
    try:
        response = requests.post(API_URL, data, headers=HEADERS)
        if response.status_code == 200:
            print("Datele au fost trimise cu success:", response.json())
            return response
        else:
            print(f"Eroare la trimiterea datelor: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print("Eroare de conexiune la API:", str(e))
        return None


def exec_action(response):
    """
    Execute action as requested
    """
    data = json.loads(response)
    if "on" in data.ventilator:
        GPIO.output(2, True)
    else:
        GPIO.output(2, False)


def main():
    while True:
        sensor_data = read_dht11()
        if sensor_data:
            print("Date citite: ", sensor_data)
            response = send_to_api(sensor_data)
            exec_action(response)
        time.sleep(1)


if __name__ == "__main__":
    main()

while True:
    try:
        # Print the values to the serial port
        temperature_c = sensor.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = sensor.humidity
        print("Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))
        print("temp " + str(temperature_c) + " hum " + str(humidity));

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        sensor.exit()
        raise error

    time.sleep(3.0)
