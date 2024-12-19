from flask import Flask, send_file, abort
import os

app = Flask(__name__)

# Répertoire images
IMAGE_FOLDER = './images'

@app.route('/<filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join(IMAGE_FOLDER, filename)
    
    if os.path.exists(file_path):  # Si l'image existe, la retourner
        return send_file(file_path)
    else:  # Si l'image n'existe pas
        abort(404, description="Image not found on the main server.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
