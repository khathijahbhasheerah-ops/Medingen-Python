import pandas as pd
import json
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer

# ------------------------------------
# Config
# ------------------------------------
CSV_FILE = "products.csv"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "product_search"
}

# ------------------------------------
# Load product data
# ------------------------------------
df = pd.read_csv(CSV_FILE)

product_names = df["product_name"].tolist()

# ------------------------------------
# Generate TF-IDF vectors
# ------------------------------------
vectorizer = TfidfVectorizer(
    analyzer="word",
    ngram_range=(1, 2),    # capture "iphone 14", "galaxy s21"
    min_df=1,
    stop_words="english"
)

vectors = vectorizer.fit_transform(product_names)

# ------------------------------------
# Connect to MySQL
# ------------------------------------
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("DELETE FROM products_vectors")

# ------------------------------------
# Store vectors
# ------------------------------------
for i, row in df.iterrows():
    product_id = int(row["product_id"])
    name = row["product_name"]

    vector = vectors[i].toarray()[0].tolist()   # convert sparse → dense list
    vector_json = json.dumps(vector)

    cursor.execute("""
        INSERT INTO products_vectors (product_id, product_name, vector)
        VALUES (%s, %s, %s)
    """, (product_id, name, vector_json))

conn.commit()
conn.close()

print("All product vectors stored successfully in MySQL.")
