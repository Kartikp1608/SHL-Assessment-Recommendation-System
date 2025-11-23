import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os

DATA_PATH = "/home/kartikpal/Desktop/SHL/individual_tests_full.csv"
EMB_PATH = "../embeddings/embeddings.npy"
META_PATH = "../embeddings/metadata.json"

df = pd.read_csv(DATA_PATH)

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = df["combined_text"].tolist()
ids = df["assessment_id"].tolist()
names = df["name"].tolist()
urls = df["url"].tolist()

print("Encoding", len(texts), "records...")

emb = model.encode(texts, batch_size=32, show_progress_bar=True)

os.makedirs("../embeddings", exist_ok=True)
np.save(EMB_PATH, emb)

metadata = [
    {"id": str(ids[i]), "name": names[i], "url": urls[i]}
    for i in range(len(ids))
]

with open(META_PATH, "w") as f:
    json.dump(metadata, f, indent=2)

print("DONE: Embeddings saved.")
