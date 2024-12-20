from flask import Flask, Response, abort, jsonify, send_file
import os
from collections import deque

app = Flask(__name__)

# Les images se trouvant en local
LOCAL_FOLDER = './images'

# Limite du cache
CACHE_LIMIT = 4

# Stratégie de caching : FIFO
cache_queue = deque(maxlen=CACHE_LIMIT)
cache_data = {}  # Stockage des données binaires en mémoire

@app.route('/<filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join(LOCAL_FOLDER, filename)

     # 1. Si le fichier est localement disponible, le servir directement
    if os.path.exists(file_path):
        return send_file(file_path)

    # 2. Sinon, vérifier dans le cache
    if filename in cache_data:
        return Response(cache_data[filename], mimetype='image/jpeg')  

    # 3. Si non disponible, demander au serveur principal
    image = fetch_from_primary_server(filename)
    if image:
        if filename in cache_data:
            cache_queue.remove(filename)  
        elif len(cache_queue) >= CACHE_LIMIT:
            oldest = cache_queue.popleft()  
            del cache_data[oldest]  

        cache_queue.append(filename)  
        cache_data[filename] = image  

        return Response(image, mimetype='image/jpeg') 

    # 4. Si l'image est introuvable, renvoyer une erreur 404
    abort(404, description="Image not found.")

def fetch_from_primary_server(filename):
    """
    Simule une requête au serveur principal pour obtenir une image.
    Retourne les données de l'image sous forme binaire.
    """
    import requests

    PRIMARY_SERVER_URL = 'http://204.8.8.1:80'
    try:
        response = requests.get(f"{PRIMARY_SERVER_URL}/{filename}")
        if response.status_code == 200:
            return response.content  
        else:
            return None
    except requests.RequestException as e:
        print(f"Erreur lors de la communication avec le serveur principal : {e}")
        return None

@app.route('/cache', methods=['GET'])
def cache_status():
    """
    Affiche l'état du cache : liste des fichiers et leur ordre FIFO.
    """
    return jsonify({
        "cache_files": list(cache_queue),
        "cache_count": len(cache_queue),
        "cache_limit": CACHE_LIMIT
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
