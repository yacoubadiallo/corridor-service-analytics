kdown
# ⛽ Corridor Service Analytics: Real-Time Multi-Service Pipeline
[![Spark](https://img.shields.io/badge/Apache_Spark-3.5.0-orange?style=flat&logo=apachespark)](https://spark.apache.org/)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-7.5.0-black?style=flat&logo=apachekafka)](https://kafka.apache.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0-green?style=flat&logo=mongodb)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Orchestrated-blue?style=flat&logo=docker)](https://www.docker.com/)

## 📝 Présentation
Ce projet déploie une **Architecture Lambda** complète pour le monitoring de l'expérience client au sein des stations-service au Mali. Le système analyse la performance de l'ensemble des pôles d'activité :
- ⛽ **Carburant** (Gestion de l'attente et qualité du service)
- 🛒 **Boutique & Restauration** (Disponibilité et accueil)
- 🧼 **Lavage Auto** (Satisfaction technique)
- ♨️ **Service Gaz** (Fluidité de l'approvisionnement)

L'objectif est de transformer des flux d'avis hétérogènes en insights actionnables pour optimiser les opérations en temps réel.



## 🏗️ Architecture Technique
L'infrastructure repose sur un environnement multi-conteneurs Docker simulant un écosystème Big Data industriel :

- **Ingestion (Edge)** : Producteur Python haute fréquence simulant les transactions et avis clients.
- **Broker (Kafka)** : Découplage des flux et persistance temporaire pour une résilience maximale.
- **Speed Layer (Spark Streaming)** : Analyse de sentiment en temps réel (Satisfait/Insatisfait) via PySpark.
- **Serving Layer (NoSQL)** : **MongoDB** pour le stockage des indicateurs chauds et **Streamlit** pour la visualisation.
- **Batch Layer (Data Lake)** : Archivage immuable en JSON converti au format **Parquet** pour des analyses historiques optimisées.

## 🚀 Déploiement

### 1. Lancement de l'infrastructure (Docker)
```bash
docker-compose up -d --build
2. Démarrage du Pipeline de Traitement
Bash
docker exec -it spark-master-1 spark-submit \
  --master spark://spark-master-1:7077,spark-master-2:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  /opt/spark/apps/sentiment_analysis.py
3. Compactage vers le Data Lake (Batch Layer)
Bash
docker exec -it spark-master-1 spark-submit /opt/spark/apps/compact_to_parquet.py
📊 Points d'accès Monitoring
Dashboard Streamlit : http://localhost:8501 (Visualisation des KPIs)

Spark Master UI : http://localhost:8080 (Gestion du cluster)

Mongo Express : http://localhost:8082 (Exploration des données)

💡 Défis Techniques Relevés
Haute Disponibilité : Configuration d'un cluster Spark avec 2 Masters (via Zookeeper) et 5 Workers.

Schéma Évolutif : Utilisation du format JSON pour capturer la diversité des avis sans contrainte de schéma rigide.

Optimisation Storage : Implémentation du format Parquet (format colonne) réduisant l'espace disque et accélérant les requêtes analytiques.


---

