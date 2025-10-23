from pydantic import BaseModel
from typing import List


class ChatbotResponse(BaseModel):
    answer: str
    retriever_docs: List[str]
