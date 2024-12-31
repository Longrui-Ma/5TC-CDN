"""
1. add file path hash (for DHT-like hash ring).
2. send hash to DHT-like hash ring.
"""
from flask import Flask, send_file, abort
import os
from hashlib import sha256
import hashlib
import requests


app = Flask(__name__)
# Directory containing the files
TXT_FOLDER = 'files1'
os.makedirs(TXT_FOLDER, exist_ok=True)  # Ensure the folder exists
DEFAULT_FILE = 'default.txt'  # Name of the default file to serve when a file is not found


def get_resource_hash(content):
    resource_hash = sha256(content).hexdigest()
    return resource_hash


def calculate_hash(image_path):
    return hashlib.sha256(image_path.encode()).hexdigest()


def prepare_hash_data(image_path):
    image_hash = calculate_hash(image_path)
    return {"hash": image_hash, "path": image_path}


def send_to_dht(image_path, dht_node_url):
    hash_data = prepare_hash_data(image_path)
    response = requests.post(f"{dht_node_url}/add_hash", json=hash_data)
    return response.status_code


@app.route('/<filename>')
def serve_file(filename):
    file_path = os.path.join(TXT_FOLDER, filename)

    if os.path.exists(file_path):  # If the file exists, serve it
        return send_file(file_path)  #, calculate_hash(file_path)
    else:  # If the file doesn't exist, serve the default file
        abort(404, description="Default file not found.")


if __name__ == '__main__':
    # TODO: send_to_dht after or before init CDN server.
    print(f"dedicated file directory: {TXT_FOLDER}")
    app.run(host='0.0.0.0', port=80)  # Run the server on port 80
