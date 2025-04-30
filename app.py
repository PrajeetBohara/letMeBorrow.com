from flask import Flask, request, jsonify
import os
import json
import re
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# Ensure required files exist
for filename in ['users.json', 'tools.json', 'owners.json', 'rentals.txt', 'messages.txt']:
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            if filename.endswith('.json'):
                json.dump([], f)
            else:
                f.write('')

app = Flask(__name__)
CORS(app)


# Load tools from tools.json
def load_tools():
    with open('tools.json', 'r') as f:
        return json.load(f)


@app.route('/get_tools', methods=['GET'])
def get_tools():
    tools = load_tools()
    return jsonify(tools)


@app.route('/get_owners')
def get_owners():
    with open('owners.json') as f:
        owners = json.load(f)
    return jsonify(owners)


@app.route('/save_rental', methods=['POST'])
def save_rental():
    data = request.get_json()
    renter_name = data.get('renter_name')
    renter_email = data.get('renter_email')
    tool_id = data.get('tool_id')
    rental_duration = data.get('rental_duration')

    # Basic validation
    if not renter_name or not renter_email or not tool_id or not rental_duration:
        return jsonify({'message': 'Missing required fields'}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", renter_email):
        return jsonify({'message': 'Invalid email format'}), 400

    try:
        tool_id = int(tool_id)
        rental_duration = int(rental_duration)
    except ValueError:
        return jsonify({'message': 'Invalid tool ID or duration'}), 400

    with open('rentals.txt', 'a') as file:
        file.write(f"{renter_name},{renter_email},{tool_id},{rental_duration}\n")

    return jsonify({'message': 'Rental saved successfully!'}), 200


@app.route('/contact', methods=['POST'])
def handle_contact():
    data = request.get_json()
    if not data.get("name") or not data.get("email") or not data.get("message"):
        return jsonify({"error": "Missing fields"}), 400

    try:
        with open('messages.txt', 'a') as f:
            f.write(
                f"Name: {data['name']}\n"
                f"Email: {data['email']}\n"
                f"Phone: {data.get('phone', 'N/A')}\n"
                f"Reason: {data.get('reason', 'N/A')}\n"
                f"Message: {data['message']}\n"
                f"{'-'*30}\n"
            )
        return jsonify({"message": "Message received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400

    with open('users.json', 'r') as f:
        users = json.load(f)

    if any(user['email'] == email for user in users):
        return jsonify({'success': False, 'message': 'Email already registered'}), 409

    hashed_password = generate_password_hash(password)
    users.append({'name': name, 'email': email, 'password': hashed_password})

    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

    return jsonify({'success': True, 'message': 'Signup successful'}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Missing email or password'}), 400

    with open('users.json', 'r') as f:
        users = json.load(f)

    for user in users:
        if user['email'] == email and check_password_hash(user['password'], password):
            return jsonify({'success': True, 'user': {'name': user['name'], 'email': user['email']}}), 200

    return jsonify({'success': False, 'message': 'Invalid email or password'}), 401


if __name__ == '__main__':
    app.run(port=5000)
