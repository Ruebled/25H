import time
import random
import board
import adafruit_dht
import RPi.GPIO as GPIO
import json
import requests
import busio
from datetime import datetime, timedelta
from adafruit_bme280 import basic as adafruit_bme280
import asyncio
import sys

# Sensor data pin is connected to GPIO 4
# sensor = adafruit_dht.DHT22(board.D4
# Uncomment for DHT11
sensor = adafruit_dht.DHT11(board.D4)

API_URL = "https://25h-endmfkd8efcvbzae.canadacentral-01.azurewebsites.net/new_daily_temperature"
HEADERS = {
    "Content-Type": "application/json",
    #"Authorization": "Bearer YOUR_API_TOKEN"
}

# Debounce settings
DEBOUNCE_TIME = 300  # in milliseconds, adjust as needed

# Variable to store the last time the button was pressed
last_pressed_time = 0

BUTTON_PIN = 26  # Replace with the GPIO pin number you are using



def get_temperature_and_humidity():
    """
    Retrieve temperature(Celsius) and humidity (%)

    Return:
    float temperature
    float humidity
    """
    try:
        # Print the values to the serial port
        temperature_c = sensor.temperature
        #temperature_f = temperature_c * (9 / 5) + 32
        humidity = sensor.humidity
        #print("Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))
        #print("Temp " + str(temperature_c) + "\nHum " + str(humidity))

        # return data read as json
        #return json.dumps({
        #    "temperature": temperature_c,
        #    "humidity": humidity
        #})
        return temperature_c, humidity

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        return None

    except Exception as error:
        sensor.exit()
        raise error

def get_barometric_pressure():
    """
    Retrieve barometric pressure (hPa)

    Return:
    float pressure
    """
    # Create I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create BME280 object
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

    # Optionally set the address (default is 0x77 or 0x76)
    # bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

    # Set the sea level pressure in hPa
    bme280.sea_level_pressure = 1013.25

    print("BME280 Sensor Readings:")
    print(f"Temperature: {bme280.temperature:.2f} °C")
    print(f"Humidity: {bme280.humidity:.2f} %")
    print(f"Pressure: {bme280.pressure:.2f} hPa")
    print(f"Altitude: {bme280.altitude:.2f} m")
    print("-" * 40)

    
async def send_to_api(data):
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
    }
    """
    try:
        response = await requests.post(API_URL, data, headers=HEADERS)
        if response.status_code == 200:
            print("Status code : 200")
            #print("Datele au fost trimise cu success:", response.json())
            return response
        else:
            print(f"Eroare la trimiterea datelor: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print("Eroare de conexiune la API:", str(e))
        return None


async def loading_animation():
    spinner = ['|', '/', '-', '\\']
    while True:
        for char in spinner:
            sys.stdout.write(f"\rLoading {char}")
            sys.stdout.flush()
            await asyncio.sleep(0.1)

# Function to read button press
async def button_callback(channel):
    global last_pressed_time
    current_time = time.time() * 1000  # Current time in milliseconds
    if current_time - last_pressed_time >= DEBOUNCE_TIME:
        print("Button pressed!")
        last_pressed_time = current_time  # Update the last pressed time

        sensor_data = get_temperature_and_humidity()
        print("Date citite: ", sensor_data)
        print("Wait for API response")

        # Start the loading animation in the background
        task = asyncio.create_task(loading_animation())

        # Save time before api request started
        before_request = time.time()

        # Call api by asyncronously waiting for its response
        response = await send_to_api(json.dumps({"temperatura" : sensor_data[0],
                                           "umiditate" : sensor_data[1]}))

        task.cancel()

        # Get time when the api responded
        after_request = time.time()

        print("Response:\n\n" + str(response.json()))

        print("API Response time of: " + str(after_request-before_request))
        time.sleep(1)

def initSensors():
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setup(2, GPIO.OUT, initial=GPIO.LOW);

    # Set the GPIO mode to BCM or BOARD
    GPIO.setmode(GPIO.BCM)

    # Pin configuration
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set up the pin as an input with a pull-up resistor

    # Set up an interrupt for the button press
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_callback, bouncetime=DEBOUNCE_TIME)

def main():
    initSensors()
    #presure = get_barometric_pressure()
    #print(presure)
    #while True:
    #    sensor_data = get_temperature_and_humidity()
    #    #if sensor_data:
    #    if GPIO.input(26) == 1:
    #        print("Date citite: ", sensor_data)
    #        response = send_to_api(json.dumps({"temperatura" : sensor_data[0],
    #                                           "umiditate" : sensor_data[1]}))
    #        print(str(response.json()))
    #    time.sleep(1)
    #time.sleep(2)

    
    try:
        print("Press the button...")
        # Keep the program running to listen for button presses
        while True:
            #button_callback(BUTTON_PIN)
            continue
            #time.sleep(0.1)  # Main loop sleep to reduce CPU usage

    except KeyboardInterrupt:
        print("\nProgram terminated.")
    finally:
        # Clean up the GPIO settings when exiting
        GPIO.cleanup()

if __name__ == "__main__":
    main()


#def exec_action(response):
#    """
#    Execute action as requested
#    """
#    data = (response.json())
#    print(response.json()['ventilator'])
#    if "on" in response.json()['ventilator']:
#        print("should be on")
#        GPIO.output(2, True)
#    else:
#        print("should be off")
#        GPIO.output(2, False)
