import re

from typing import List, Optional
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)


class TextChunker:
    """
    Класс для разбиения текста на чанки
    с использованием langchain.text_splitter.
    Используйте метод execute(text) для получения списка чанков.
    """

    def __init__(
        self,
        chunk_size: int = 200,
        overlap: int = 20,
        unit: str = "chars",
        encoding_name: str = "gpt2"
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.unit = unit
        self.encoding_name = encoding_name

    def execute(self, text: Optional[str]) -> List[str]:
        if text is None:
            return []

        text = re.sub(r'\n{3,}', '\n', text)

        if self.unit == "chars":
            splitter = CharacterTextSplitter(
                chunk_size=self.chunk_size, chunk_overlap=self.overlap
            )
            return splitter.split_text(text)

        if self.unit == "tokens":
            splitter = TokenTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.overlap,
                encoding_name=self.encoding_name,
            )
            return splitter.split_text(text)

        if self.unit == "sentences":
            separators = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]
            splitter = RecursiveCharacterTextSplitter(
                separators=separators,
                chunk_size=self.chunk_size,
                chunk_overlap=self.overlap,
            )
            return splitter.split_text(text)
