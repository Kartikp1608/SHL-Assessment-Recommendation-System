from pymilvus import connections, Collection

connections.connect("default", uri="/home/kartikpal/Desktop/SHL/data/milvus.db")

col = Collection("shl_assessments")
print("Fields:")
for f in col.schema.fields:
    print(" -", f.name, f.dtype)

print("Total:", col.num_entities)
