import pandas as pd
from pymongo import UpdateOne
from app.db import db

CSV_URL = "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/samples/books.csv"

def ingest_books():
    df = pd.read_csv(CSV_URL)
    df = df.fillna("")  # Remove NaNs

    operations = []
    for _, row in df.iterrows():
        operations.append(
            UpdateOne(
                {"book_id": int(row.book_id)},
                {"$set": {
                    "book_id": int(row.book_id),
                    "goodreads_book_id": int(row.goodreads_book_id),
                    "title": row.title,
                    "authors": row.authors,
                    "original_publication_year": int(row.original_publication_year) if row.original_publication_year else None,
                    "average_rating": float(row.average_rating),
                    "ratings_count": int(row.ratings_count),
                    "image_url": row.image_url,
                    "small_image_url": row.small_image_url
                }},
                upsert=True
            )
        )
    if operations:
        db.books.bulk_write(operations)
        print(f"{len(operations)} books ingested/updated")

if __name__ == "__main__":
    ingest_books()
