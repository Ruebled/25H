import time
import json
import board
import adafruit_dht
import RPi.GPIO as GPIO
import requests
import busio
from datetime import datetime, timedelta
from adafruit_bme280 import basic as adafruit_bme280
import logging

# Configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Pin configuration
BUTTON_PIN = 26  # Replace with the GPIO pin number you are using
SENSOR_PIN = board.D4  # GPIO pin for the DHT sensor
API_URL = "https://25h-endmfkd8efcvbzae.canadacentral-01.azurewebsites.net/new_daily_temperature"
HEADERS = {"Content-Type": "application/json"}
DEBOUNCE_TIME = 300  # in milliseconds

# Initialize the DHT sensor
sensor = adafruit_dht.DHT11(SENSOR_PIN)

# Variable to store the last time the button was pressed
last_pressed_time = 0

def get_temperature_and_humidity():
    """
    Retrieve temperature (Celsius) and humidity (%).
    
    Returns:
        tuple: (temperature, humidity)
    """
    try:
        temperature_c = sensor.temperature
        humidity = sensor.humidity

        if temperature_c is not None and humidity is not None:
            return temperature_c, humidity
        else:
            logging.error("Failed to read temperature or humidity.")
            return None
    except RuntimeError as error:
        logging.warning(f"RuntimeError: {error.args[0]}")
        time.sleep(2.0)
        return None
    except Exception as error:
        logging.error(f"Unexpected error: {error}")
        sensor.exit()
        raise

def get_barometric_pressure():
    """
    Retrieve barometric pressure (hPa) from the BME280 sensor.
    
    Returns:
        float: pressure
    """
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    bme280.sea_level_pressure = 1013.25  # Standard sea level pressure

    pressure = bme280.pressure
    logging.info(f"BME280 Readings -> Pressure: {pressure:.2f} hPa")
    return pressure

def send_to_api(data):
    """
    Send temperature and humidity data to the API and receive action response.
    
    Args:
        data (str): JSON string of sensor data.
    
    Returns:
        Response: API response object or None if the request fails.
    """
    try:
        response = requests.post(API_URL, data, headers=HEADERS)
        if response.status_code == 200:
            logging.info("Data successfully sent to API.")
            return response
        else:
            logging.error(f"API call failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to API: {e}")
        return None

def button_callback(channel):
    """
    Callback function for button press event.
    """
    global last_pressed_time
    current_time = time.time() * 1000  # Current time in milliseconds

    if current_time - last_pressed_time >= DEBOUNCE_TIME:
        logging.info("Button pressed!")
        last_pressed_time = current_time  # Update the last pressed time

        sensor_data = get_temperature_and_humidity()
        if sensor_data:
            logging.info(f"Readings: {sensor_data}")
            response = send_to_api(json.dumps({"temperatura": sensor_data[0], "umiditate": sensor_data[1]}))
            if response:
                logging.info(f"API Response: {response.json()}")
        time.sleep(1)

def init_sensors():
    """
    Initialize GPIO settings and button callback.
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_callback, bouncetime=DEBOUNCE_TIME)

def main():
    """
    Main function to run the program.
    """
    init_sensors()
    logging.info("Program started. Press the button to record data.")

    try:
        # Keep the program running to listen for button presses
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("\nProgram terminated by user.")
    finally:
        GPIO.cleanup()
        logging.info("GPIO cleaned up.")

if __name__ == "__main__":
    main()
