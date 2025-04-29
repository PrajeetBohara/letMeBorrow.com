from flask import Flask, request, jsonify
import os
import json
import re
from flask_cors import CORS  # Import Flask-CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Sample tools data (loaded from tools.json)
def load_tools():
    with open('tools.json', 'r') as f:
        return json.load(f)

@app.route('/get_tools', methods=['GET'])
def get_tools():
    tools = load_tools()  # Load tools dynamically from tools.json
    return jsonify(tools)

# Rentals part stays the same as before
if not os.path.exists('rentals.txt'):
    open('rentals.txt', 'w').close()

@app.route('/save_rental', methods=['POST'])
def save_rental():
    data = request.get_json()
    renter_name = data.get('renter_name')
    renter_email = data.get('renter_email')
    tool_id = data.get('tool_id')

    # Backend validation for missing or invalid data
    if not renter_name or not renter_email or not tool_id:
        return jsonify({'message': 'Missing required fields'}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", renter_email):
        return jsonify({'message': 'Invalid email format'}), 400

    try:
        tool_id = int(tool_id)
    except ValueError:
        return jsonify({'message': 'Invalid tool ID'}), 400

    with open('rentals.txt', 'a') as file:
        file.write(f"{renter_name},{renter_email},{tool_id}\n")

    return jsonify({'message': 'Rental saved successfully!'}), 200

if __name__ == '__main__':
    app.run(port=5000)
