import pandas as pd
from pymongo import UpdateOne
from app.db import db

CSV_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/samples/book_tags.csv"

def ingest_book_tags():
    df = pd.read_csv(CSV_URL)
    df = df.fillna(0)

    operations = []
    for _, row in df.iterrows():
        operations.append(
            UpdateOne(
                {"goodreads_book_id": int(row.goodreads_book_id), "tag_id": int(row.tag_id)},
                {"$set": {
                    "goodreads_book_id": int(row.goodreads_book_id),
                    "tag_id": int(row.tag_id),
                    "count": int(row["count"])
                }},
                upsert=True
            )
        )
    if operations:
        db.book_tags.bulk_write(operations)
        print(f"{len(operations)} book_tags ingested/updated")

if __name__ == "__main__":
    ingest_book_tags()
