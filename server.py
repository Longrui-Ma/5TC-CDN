from flask import Flask, send_file, abort
import os
import requests

app = Flask(__name__)

# Directory containing the text files
TXT_FOLDER = 'files_server'
os.makedirs(TXT_FOLDER, exist_ok=True)  # Ensure the folder exists


DEFAULT_FILE = 'default.txt'            # Name of the default file to serve when a file is not found
ORIGIN_SERVERS = ['http://201.8.8.1',
                  'http://202.8.8.1']   # central server from which to retrieve the images that are not locally available
MAX_FILES = 3

file_request_count = {}


@app.route('/<filename>')
def serve_file(filename):

    # keep track of request counts
    if filename in file_request_count:
        file_request_count[filename] += 1
    else:
        file_request_count[filename] = 1
    print(f"The file {filename} is requested for the {file_request_count[filename]}th time.")
    
    file_path = os.path.join(TXT_FOLDER, filename)
    default_path = os.path.join(TXT_FOLDER, DEFAULT_FILE)

    # serve 
    if os.path.exists(file_path):           # If the file exists, serve it
        return send_file(file_path)
    
    else:                                   # if not existant, fetch from origin
        print(f"File {filename} not on this server. Getting it from origin server.")
        
        while len(os.listdir(TXT_FOLDER)) >= MAX_FILES:
            delete_least_requested_file()

        for origin_server in ORIGIN_SERVERS:
            file_url = f"{origin_server}/{filename}"

            try:
                response = requests.get(file_url)

                if response.status_code == 200:             # file exists on origin server
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    return send_file(file_path)
            
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {filename} from origin server: {e}")

        # if the program reaches this code, it was impossible to obtain the requested file -> return default file
        if os.path.exists(default_path):
            print("Requested file not found on origin server. Returning local default file.")
            return send_file(default_path)
        else:
            abort(404, description="Default file not found on this server.")
                


def delete_least_requested_file():
    #least_requested_file = min(file_request_count, key=file_request_count.get)
    key_least_requested = list(file_request_count.keys())[0]
    for key in file_request_count.keys():
        if file_request_count[key] < file_request_count[key_least_requested]:
            key_least_requested = key

    lrf_file_path = os.path.join(TXT_FOLDER, key_least_requested)
    if os.path.exists(lrf_file_path):
        os.remove(lrf_file_path)
        print(f"Deleted least frequently requested file: {lrf_file_path}")
        del file_request_count[key_least_requested]


@app.route('/stats')
def get_stats():
    stats = "\n".join(f"{filename}: {count}" for filename, count in file_request_count.items())
    stats += "\n"
    return stats, 200, {'Content-Type': 'text/plain'}



if __name__ == '__main__':
    # Run the server on port 80
    app.run(host='0.0.0.0', port=80)