from pydantic import BaseModel
from typing import List


class ChatbotResponse(BaseModel):
    answer: str  # Итоговый ответ
    retriever_docs: List[str]  # Использованные документы
