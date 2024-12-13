from flask import Flask, send_file, abort
import os

app = Flask(__name__)

# Directory containing the text files
TXT_FOLDER = 'files'
os.makedirs(TXT_FOLDER, exist_ok=True)  # Ensure the folder exists


DEFAULT_FILE = 'default.txt'        # Name of the default file to serve when a file is not found


@app.route('/<filename>')
def serve_file(filename):
    # Ensure the file has a .txt extension
    if not filename.endswith('.txt'):
        abort(400, description="Only .txt files are allowed.")
    
    file_path = os.path.join(TXT_FOLDER, filename)
    
    if os.path.exists(file_path):   # If the file exists, serve it
        return send_file(file_path)
    else:                            # If the file doesn't exist, serve the default file
        abort(404, description="Default file not found.")

if __name__ == '__main__':
    # Run the server on port 80
    app.run(host='0.0.0.0', port=80)