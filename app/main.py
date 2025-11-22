from fastapi import FastAPI, Query, HTTPException, Depends, Request
from app.models import RatingIn
from app.db import db
import os, time

API_KEY = os.getenv("API_KEY", "dev-key")

app = FastAPI(title="GoodBooks API")

def require_key(req: Request):
    if req.headers.get("x-api-key") != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    latency = int((time.time() - start) * 1000)
    print({"route": request.url.path, "status": resp.status_code, "latency_ms": latency})
    return resp

@app.get("/books")
def list_books(q: str | None = None, page: int = 1, page_size: int = Query(20, le=100)):
    filt = {}
    if q:
        filt["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"authors": {"$regex": q, "$options": "i"}}
        ]
    total = db.books.count_documents(filt)
    items = list(db.books.find(filt).skip((page-1)*page_size).limit(page_size))
    for x in items: x["_id"] = str(x["_id"])
    return {"items": items, "page": page, "page_size": page_size, "total": total}

@app.post("/ratings", dependencies=[Depends(require_key)])
def upsert_rating(r: RatingIn):
    res = db.ratings.update_one({"user_id": r.user_id, "book_id": r.book_id},
                                {"$set": r.model_dump()}, upsert=True)
    return {"upserted": bool(res.upserted_id), "matched": res.matched_count}
