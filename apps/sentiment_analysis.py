from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, when
from pyspark.sql.types import *
from pyspark.ml.feature import Tokenizer, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline

# Initialisation de la Session Spark
spark = SparkSession.builder \
    .appName("CorridorLambdaArchitecture") \
    .config("spark.mongodb.output.uri", "mongodb://mongodb:27017/corridor_db.results") \
    .getOrCreate()

# Désactiver les logs trop verbeux pour mieux voir tes résultats
spark.sparkContext.setLogLevel("WARN")

# Schéma des données Corridor Mali
schema = StructType([
    StructField("id_client", StringType()),
    StructField("station", StringType()),
    StructField("service", StringType()),
    StructField("avis", StringType()),
    StructField("note", IntegerType()),
    StructField("moyen_paiement", StringType()),
    StructField("timestamp", DoubleType())
])

print("Lecture du flux Kafka en cours...")

# 1. Ingestion Kafka (Source unique)
# Note : On utilise 'kafka:9092' pour le réseau interne Docker
df_kafka = spark.read.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "corridor_reviews") \
    .option("startingOffsets", "earliest") \
    .load()

# Extraction et conversion du JSON
raw_df = df_kafka.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")).select("data.*")

# ============================================================
# COUCHE 1 : BATCH LAYER (Archivage pour le long terme)
# ============================================================
# Sauvegarde des données brutes en JSON dans le volume /data
# Cela permet de recalculer les modèles plus tard sur l'historique
print("Archivage des données (Batch Layer)...")
raw_df.write.format("json").mode("append").save("/opt/spark/data/corridor_history")

# ============================================================
# COUCHE 2 : SPEED LAYER (Analyse Machine Learning)
# ============================================================
print("Analyse de sentiments par Régression Logistique...")

# Préparation des étiquettes (Labeling) : Note >= 3 -> 1 (Positif), sinon 0 (Négatif)
labeled_df = raw_df.withColumn("label", when(col("note") >= 3, 1.0).otherwise(0.0))

# Construction du Pipeline ML
tokenizer = Tokenizer(inputCol="avis", outputCol="words")
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=100)
idf = IDF(inputCol="rawFeatures", outputCol="features")
lr = LogisticRegression(featuresCol="features", labelCol="label")

pipeline = Pipeline(stages=[tokenizer, hashingTF, idf, lr])

# Entraînement sur le flux actuel (Simulation d'apprentissage continu)
model = pipeline.fit(labeled_df)
predictions = model.transform(labeled_df)

# Mise en forme finale pour MongoDB
final_results = predictions.select(
    "id_client", "station", "service", "avis", 
    "note", "moyen_paiement", "prediction"
).withColumn("sentiment", when(col("prediction") == 1.0, "Satisfait").otherwise("Insatisfait"))

# ============================================================
# COUCHE 3 : SERVING LAYER (Stockage MongoDB)
# ============================================================
# ============================================================
# COUCHE 3 : SERVING LAYER (Stockage MongoDB)
# ============================================================
print("Envoi des résultats vers MongoDB...")
final_results.write \
    .format("mongodb") \
    .option("connection.uri", "mongodb://mongodb:27017") \
    .option("database", "corridor_db") \
    .option("collection", "results") \
    .mode("append") \
    .save()
print("""
PIPELINE LAMBDA EXÉCUTÉ AVEC SUCCÈS !
----------------------------------------
1. Batch Layer : Données brutes archivées dans /data/corridor_history
2. Speed Layer : Classification ML effectuée sur les avis.
3. Serving Layer : Résultats disponibles dans MongoDB (corridor_db.results).
""")