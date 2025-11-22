import pandas as pd
from pymongo import UpdateOne
from app.db import db

CSV_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/samples/ratings.csv"

def ingest_ratings():
    df = pd.read_csv(CSV_URL)
    df = df.fillna(0)

    operations = []
    for _, row in df.iterrows():
        operations.append(
            UpdateOne(
                {"user_id": int(row.user_id), "book_id": int(row.book_id)},
                {"$set": {
                    "user_id": int(row.user_id),
                    "book_id": int(row.book_id),
                    "rating": int(row.rating)
                }},
                upsert=True
            )
        )
    if operations:
        db.ratings.bulk_write(operations)
        print(f"{len(operations)} ratings ingested/updated")

if __name__ == "__main__":
    ingest_ratings()
