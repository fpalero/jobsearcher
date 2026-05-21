import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure

load_dotenv(Path(__file__).resolve().parent / ".env")

MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb://midzospa:3VcdcelzsTWGNkApcA6x8PsW@localhost:27017/jobsearcher?authSource=admin"
)

client = MongoClient(MONGO_URI)
db = client["jobsearcher"]

for col_name in ("jobs", "unified_jobs"):
    collection = db[col_name]
    existing = collection.index_information()
    if "unique_apply_link" in existing:
        print(f"  -> Indice 'unique_apply_link' ya existe en {col_name}")
        collection.drop_index("unique_apply_link")
        print(f"  -> Indice antiguo eliminado de {col_name}, creando con partialFilterExpression")

    # Clean duplicates: keep one doc per apply_link, remove extras
    pipeline = [
        {"$group": {"_id": "$apply_link", "ids": {"$push": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
    ]
    dup_cursor = collection.aggregate(pipeline)
    removed = 0
    for dup in dup_cursor:
        keep = dup["ids"][0]
        to_remove = dup["ids"][1:]
        collection.delete_many({"_id": {"$in": to_remove}})
        removed += len(to_remove)
    if removed:
        print(f"  -> Eliminados {removed} duplicados en {col_name}")

    try:
        collection.create_index(
            "apply_link",
            unique=True,
            partialFilterExpression={"apply_link": {"$exists": True, "$gt": ""}},
            name="unique_apply_link",
        )
        print(f"  -> Indice unico (parcial) creado en {col_name}.apply_link")
    except OperationFailure as e:
        print(f"  -> Error creando indice en {col_name}: {e}")

print("Indices asegurados.")
