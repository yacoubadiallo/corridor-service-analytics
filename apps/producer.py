import json
import time
import random
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# Configuration du producteur avec tentative de reconnexion
def get_producer():
    while True:
        try:
            # On utilise 'kafka:9092' car le script tourne DANS un container Docker
            p = KafkaProducer(
                bootstrap_servers=['kafka:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(0, 10, 1)
            )
            print("Connecté à Kafka avec succès !")
            return p
        except NoBrokersAvailable:
            print("Kafka n'est pas encore prêt... Nouvelle tentative dans 5 secondes.")
            time.sleep(5)

producer = get_producer()

# Données contextuelles pour Corridor Mali
localisations = [
    "Bamako - Hamdallaye ACI", "Bamako - Badalabougou", "Bamako - Sotuba",
    "Ségou - Centre", "Sikasso - Entrée Ville", "Kayes - Plateau"
]
services = ["Pompe essence", "Boutique", "Lavage auto", "Service Gaz"]
commentaires = [
    {"txt": "Pompistes très accueillants à l'ACI, service rapide.", "note": 5},
    {"txt": "La boutique est mal approvisionnée en boissons fraîches.", "note": 2},
    {"txt": "Station propre et bien éclairée la nuit.", "note": 4},
    {"txt": "Attente trop longue pour le gaz ce matin à Sotuba.", "note": 1},
    {"txt": "Carburant de bonne qualité, ma moto roule mieux.", "note": 5},
    {"txt": "Le lavage auto a rayé ma carrosserie, déçu.", "note": 1}
]

print("Flux 'Corridor Mali - Customer Experience' démarré...")

try:
    while True:
        # Choix aléatoire d'un commentaire
        c = random.choice(commentaires)
        
        # Construction du message JSON
        data = {
            "id_client": f"ML-{random.randint(10000, 99999)}",
            "station": random.choice(localisations),
            "service": random.choice(services),
            "avis": c["txt"],
            "note": c["note"],
            "moyen_paiement": random.choice(["Orange Money", "Cash", "Carte"]),
            "timestamp": time.time()
        }
        
        # Envoi au topic 'corridor_reviews'
        producer.send('corridor_reviews', data)
        
        print(f"Donnée envoyée : {data['station']} | Note : {data['note']}| Paiement : {data['moyen_paiement']}")
        
        # Pause de 1.5 seconde entre chaque envoi
        time.sleep(1.5)

except KeyboardInterrupt:
    print("Arrêt du producteur.")
finally:
    producer.close()