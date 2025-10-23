from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    query: str = Field(..., min_length=1)
