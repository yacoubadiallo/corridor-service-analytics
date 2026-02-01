# Corridor Lambda Architecture

Projet de traitement de flux de données massives (Avis clients) en temps réel.

## Architecture
- **Ingestion** : Kafka (Node.js producer)
- **Speed Layer** : Spark Structured Streaming (Python)
- **ML** : Sentiment Analysis (Logistic Regression)
- **Storage** : MongoDB & Parquet (Data Lake)

## Installation
1. `docker-compose up -d`
2. `docker exec -it spark-master-1 spark-submit --packages ... apps/sentiment_analysis.py`
