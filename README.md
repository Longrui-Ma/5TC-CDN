L'architecture du projet sur GNS3 se trouve dans le dossier CDN-BGP-GNS3.
Le dossier my-portofolio est un site web qu'on avait implementé au debut du projet pour le mettre dans nos serveurs, finalement on ne l'a pas utilisé.
Dans le dossier codes-serveur se trouve le fichier origin-serveur.py qui est le code pour notre serveur d'origine, le fichier serveur-FIFO qui est le code pour les edge serveurs avec comme stratégie de caching FIFO, et le fichier serveur-LRU avec une stratégie de caching LRU. La stratégie LRU a été maintenue.

Architecture sur GNS3:
![image](https://github.com/user-attachments/assets/0862d433-84a9-4b94-bb6d-edc2d8ee30e2)

## Description:
Ce projet a pour but de créer un 
serveur de distribution de contenu (CDN) pour la gestion et la diffusion d'images. Le serveur récupère les images à partir d'un serveur principal et les met en cache pour une diffusion rapide aux clients, tout en optimisant les performances à l'aide d'une stratégie de cache FIFO ou LRU. Le projet utilise Flask comme serveur web pour gérer les requêtes HTTP et mettre en œuvre la logique du cache, avec des fichiers d'images récupérés soit localement, soit depuis un serveur distant.

## Fonctionnalités

- Gestion des routes et des requêtes HTTP : Le serveur est capable de répondre aux requêtes GET pour les images. Si l'image est déjà dans le cache, elle est servie directement. Si l'image est absente, elle est récupérée du serveur principal.
- Système de cache : Le cache est implémenté avec une RLU
- Stratégie de gestion des images : Lorsqu'une image est demandée, elle est d'abord recherchée localement. Si elle n'est pas trouvée, une requête est envoyée au serveur principal pour récupérer l'image, puis elle est ajoutée au cache et envoyée au client.
- Contrôle du cache : Il est possible de consulter l'état du cache via une route dédiée qui retourne les fichiers présents dans le cache, leur nombre, ainsi que la limite du cache.
- Optimisation de la performance : Le système minimise les temps de réponse pour les clients en servant les images depuis le cache, réduisant ainsi la charge sur le serveur principal.


