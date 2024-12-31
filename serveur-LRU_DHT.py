from flask import Flask, send_file, abort, jsonify, Response
import os
from collections import OrderedDict
import requests
import io
import requests


app = Flask(__name__)
# Les images se trouvant en local
LOCAL_FOLDER = './images'
# Limite du cache
CACHE_LIMIT = 4
# Strategie de caching : LRU
cache = OrderedDict()


class DHTNode:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.hash_ring = {}

    def add_server(self, server_ip):
        """Distribute hash range for each CDN node"""
        hash_value = hash(server_ip)
        self.hash_ring[hash_value] = server_ip

    def get_server(self, key):
        """Get CDN server from hash ring"""
        hash_value = hash(key)
        sorted_hashes = sorted(self.hash_ring.keys())
        for h in sorted_hashes:
            if hash_value <= h:
                return self.hash_ring[h]
        return self.hash_ring[sorted_hashes[0]]


def sync_to_neighbors(hash_data, neighbors):
    for neighbor_url in neighbors:
        response = requests.post(f"{neighbor_url}/add_hash", json=hash_data)
        if response.status_code != 200:
            print(f"Failed to sync with {neighbor_url}")


def add_hash_to_ring(dht_node, hash_data):
    image_hash = hash_data["hash"]
    image_path = hash_data["path"]
    # add hash to local ring
    dht_node.add_to_ring(image_hash, image_path)
    return "Hash added"


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
        mimetype='image/jpeg'  # Assurez-vous de définir le bon type MIME en fonction de l'image
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
        # Déplacer l'élément à la fin de l'OrderedDict pour le marquer comme le plus récemment utilisé
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

# TODO: open another port for DHT-like ring
# app = Flask(__name__)
# dht_storage = {}
#
# @app.route("/add_hash", methods=["POST"])
# def add_hash():
#     data = request.json
#     image_hash = data["hash"]
#     image_path = data["path"]
#     dht_storage[image_hash] = image_path
#     return "Hash added to DHT", 200
#
# if __name__ == "__main__":
#     app.run(port=8080)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
