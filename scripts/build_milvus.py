from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType, Collection, utility
)
import numpy as np
import pandas as pd
import json
import os

DATA_PATH = "/home/kartikpal/Desktop/SHL/data/cleaned_dataset.csv"
EMB_PATH = "/home/kartikpal/Desktop/SHL/embeddings/embeddings.npy"
META_PATH = "/home/kartikpal/Desktop/SHL/embeddings/metadata.json"

MILVUS_PATH = "/home/kartikpal/Desktop/SHL/data/milvus.db"  
COLLECTION_NAME = "shl_assessments"

# Connect to Milvus Lite
connections.connect("default", uri=MILVUS_PATH)

# Delete collection if exists
if COLLECTION_NAME in utility.list_collections():
    utility.drop_collection(COLLECTION_NAME)

# Define schema
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=50, is_primary=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
    FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=200),
    FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=500)
]

schema = CollectionSchema(fields, "SHL assessment collection")

# Create collection
collection = Collection(COLLECTION_NAME, schema)

# Load embeddings + metadata
emb = np.load(EMB_PATH).tolist()
meta = json.load(open(META_PATH))

ids = [m["id"] for m in meta]
names = [m["name"] for m in meta]
urls = [m["url"] for m in meta]

entities = [ids, emb, names, urls]

# Insert into Milvus
collection.insert(entities)

# Create index
collection.create_index(
    field_name="embedding",
    index_params={
        "index_type": "AUTOINDEX",
        "metric_type": "COSINE",
        "params": {}
    }
)


collection.load()

print("Milvus setup complete. Vector count:", collection.num_entities)
