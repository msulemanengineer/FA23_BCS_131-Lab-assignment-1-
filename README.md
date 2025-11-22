# GoodBooks API (MongoDB + FastAPI)

## **1. Setup**

### **Requirements**

- Python 3.10+
- MongoDB (local or Docker)
- `pip install -r requirements.txt`

### **Environment Variables (.env)**

```
MONGO_URI=mongodb://localhost:27017
DB_NAME=goodbooks
API_KEY=dev-key
```

### **Run MongoDB + API**

```bash
docker compose up --build
```

### **Ingest Data**

```bash
python -m ingest.ingest_books
python -m ingest.ingest_ratings
python -m ingest.ingest_tags
python -m ingest.ingest_book_tags
python -m ingest.ingest_to_read
```

## **2. API Endpoints Examples**

### **List Books**

```http
GET /books?q=orwell&year_from=1930&year_to=1950&sort=avg&order=desc&page=1&page_size=5
```

**Response**

```json
{
  "items": [
    {
      "book_id": 170,
      "goodreads_book_id": 7613,
      "title": "Animal Farm",
      "authors": "George Orwell",
      "original_publication_year": 1945,
      "average_rating": 3.98,
      "ratings_count": 273849,
      "image_url": "...",
      "small_image_url": "..."
    }
  ],
  "page": 1,
  "page_size": 5,
  "total": 3
}
```

### **Get Book by ID**

```http
GET /books/170
```

**Response**

```json
{
  "book_id": 170,
  "goodreads_book_id": 7613,
  "title": "Animal Farm",
  "authors": "George Orwell",
  "original_publication_year": 1945,
  "average_rating": 3.98,
  "ratings_count": 273849,
  "image_url": "...",
  "small_image_url": "..."
}
```

### **Get Book Tags**

```http
GET /books/170/tags
```

**Response**

```json
[
  { "tag_id": 42, "tag_name": "political-fiction", "count": 17 },
  { "tag_id": 15, "tag_name": "classics", "count": 25 }
]
```

### **Get User To-Read List**

```http
GET /users/2001/to-read
```

**Response**

```json
[
  { "user_id": 2001, "book_id": 170 },
  { "user_id": 2001, "book_id": 171 }
]
```

### **Post a Rating (Protected)**

```http
POST /ratings
x-api-key: dev-key
Content-Type: application/json

{
  "user_id": 2001,
  "book_id": 170,
  "rating": 5
}
```

**Response**

```json
{ "upserted": true, "matched": 0 }
```

### **cURL Examples**

```bash
curl -X GET "http://localhost:8000/books?q=orwell&page=1&page_size=5"

curl -X POST "http://localhost:8000/ratings"   -H "x-api-key: dev-key"   -H "Content-Type: application/json"   -d '{"user_id":2001,"book_id":170,"rating":5}'
```

## **3. Design Note**

### **Collections & Schema**

1. **books**

- `book_id` (int, PK), `goodreads_book_id`, `title`, `authors`, `original_publication_year`, `average_rating`, `ratings_count`, `image_url`, `small_image_url`
- **Indexes:**  
  `{ title: 1, authors: 1 }` → search  
  `{ average_rating: -1 }` → top-rated  
  `{ book_id: 1 }` → primary lookup

2. **ratings**

- `user_id`, `book_id`, `rating`
- **Indexes:**  
  `{ book_id: 1 }` → ratings for a book  
  `{ user_id: 1, book_id: 1 }` → unique upsert protection

3. **tags**

- `tag_id`, `tag_name`
- **Indexes:** `{ tag_id: 1 }`, `{ tag_name: 1 }`

4. **book_tags**

- `goodreads_book_id`, `tag_id`, `count`
- **Indexes:** `{ tag_id: 1 }`, `{ goodreads_book_id: 1 }`

5. **to_read**

- `user_id`, `book_id`
- **Indexes:** `{ user_id: 1, book_id: 1 }`

### **Design Trade-Offs**

- **Separate collections** for flexibility & smaller document size.
- **Ratings separate** for efficient aggregation.
- **Indexes** optimized for read-heavy API (search, top-rated, tags).
- **Pagination** to handle large dataset (~6M ratings) efficiently.
- **Idempotent ingestion** ensures no duplicate entries.

### **Optional Extras**

- Embed popular tags in `books` for faster `/books` response.
- Pre-aggregate rating summaries to reduce repeated computation.
