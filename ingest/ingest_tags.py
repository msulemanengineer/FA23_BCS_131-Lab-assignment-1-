import pandas as pd
from pymongo import UpdateOne
from app.db import db

CSV_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/samples/tags.csv"

def ingest_tags():
    df = pd.read_csv(CSV_URL)
    df = df.fillna("")

    operations = []
    for _, row in df.iterrows():
        operations.append(
            UpdateOne(
                {"tag_id": int(row.tag_id)},
                {"$set": {
                    "tag_id": int(row.tag_id),
                    "tag_name": row.tag_name
                }},
                upsert=True
            )
        )
    if operations:
        db.tags.bulk_write(operations)
        print(f"{len(operations)} tags ingested/updated")

if __name__ == "__main__":
    ingest_tags()
