from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_message():
    try:
        # Parse the incoming JSON request
        data = request.get_json()
        if not data or 'temperature' not in data or 'humidity' not in data:
            return jsonify({'error': 'Invalid data format'}), 400

        # Extract the temperature and humidity
        temperature = data['temperature']
        humidity = data['humidity']

        # Generate random response components based on temperature and humidity
        temp_status = "optimal" if 20 <= temperature <= 25 else "not optimal"
        predict_outcomes = [
            "we will burn to death",
            "everything will be fine",
            "prepare for the worst"
        ]
        predict = random.choice(predict_outcomes)

        ventilator_status = "on" if temperature > 24 else "off"
        termistor_status = "on" if humidity < 30 else "off"
        robinet_status = "on" if temperature > 25 or humidity > 50 else "off"

        # Construct the response
        response = {
            'message': f"temp is {temp_status}",
            'predict': predict,
            'ventilator': ventilator_status,
            'termistor': termistor_status,
            'robinet': robinet_status
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the server on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000)
