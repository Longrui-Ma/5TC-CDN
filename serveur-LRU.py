from flask import Flask, send_file, abort, jsonify, Response
import os
from collections import OrderedDict
import requests
import io

app = Flask(__name__)

# Les images se trouvant en local
LOCAL_FOLDER = './images'

# Limite du cache
CACHE_LIMIT = 4

# Strategie de caching : LRU
cache = OrderedDict()

@app.route('/<filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join(LOCAL_FOLDER, filename)

    # 1. Si le fichier est localement disponible, le servir directement
    if os.path.exists(file_path):
        return send_file(file_path)

    # 2. Si le fichier existe pas en local, vérifier dans le cache
    if filename in cache:
        update_cache(filename)  # Mettre à jour l'ordre LRU
        return Response(cache[filename], mimetype='image/jpeg')

    # 3. Si non disponible, demander au serveur principal
    image = fetch_from_primary_server(filename)
    if image:
        # Ajouter l'image au cache
        cache[filename] = image
        if len(cache) > CACHE_LIMIT:
            #supprimer le premier element le moins used
            cache.popitem(last=False)  

        return send_file(
        io.BytesIO(image), 
        mimetype='image/jpeg' 
        )

    # 4. Si l'image est introuvable, renvoyer une erreur 404
    abort(404, description="Image not found.")

def fetch_from_primary_server(filename):
    PRIMARY_SERVER_URL = 'http://204.8.8.1:80'
    try:
        response = requests.get(f"{PRIMARY_SERVER_URL}/{filename}")
        if response.status_code == 200:
            return response.content
        else:
            print(f"Erreur : L'image {filename} n'a pas pu être récupérée depuis le serveur principal (status: {response.status_code}).")
            return None
    except requests.RequestException as e:
        print(f"Erreur lors de la communication avec le serveur principal : {e}")
        return None

def update_cache(filename):
    if filename in cache:
        # marquer comme le plus récemment utilisé
        cache.move_to_end(filename)

@app.route('/cache', methods=['GET'])
def cache_status():
    """
    Affiche l'état du cache : liste des fichiers et leur ordre LRU.
    """
    return jsonify({
        "cache_files": list(cache.keys()),
        "cache_count": len(cache),
        "cache_limit": CACHE_LIMIT
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
