from pydantic import BaseModel, Field

class RatingIn(BaseModel):
    user_id: int
    book_id: int
    rating: int = Field(ge=1, le=5)
