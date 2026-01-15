import json
import mysql.connector
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------------
# Load TF-IDF model at cold start
# ------------------------------
vectorizer = joblib.load("tfidf_vectorizer.joblib")

# ------------------------------
# DB Config
# ------------------------------
DB_CONFIG = {
    "host": "YOUR_RDS_ENDPOINT",
    "user": "admin",
    "password": "YOUR_PASSWORD",
    "database": "product_search"
}

# ------------------------------
# Lambda Handler
# ------------------------------
def lambda_handler(event, context):

    query = event.get("queryStringParameters", {}).get("query")

    if not query:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "query parameter is required"})
        }

    # ------------------------------
    # Generate query vector
    # ------------------------------
    query_vector = vectorizer.transform([query]).toarray()

    # ------------------------------
    # Load product vectors
    # ------------------------------
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT product_id, product_name, vector FROM products_vectors")
    rows = cursor.fetchall()

    conn.close()

    product_vectors = []
    metadata = []

    for row in rows:
        product_vectors.append(json.loads(row["vector"]))
        metadata.append({
            "product_id": row["product_id"],
            "product_name": row["product_name"]
        })

    product_vectors = np.array(product_vectors)

    # ------------------------------
    # Cosine similarity
    # ------------------------------
    similarities = cosine_similarity(query_vector, product_vectors)[0]

    # ------------------------------
    # Top-5 matches
    # ------------------------------
    top_indices = similarities.argsort()[-5:][::-1]

    results = []
    for i in top_indices:
        results.append({
            "product_id": metadata[i]["product_id"],
            "product_name": metadata[i]["product_name"],
            "score": float(similarities[i])
        })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "query": query,
            "results": results
        })
    }
