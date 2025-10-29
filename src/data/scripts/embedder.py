from typing import List, Optional
from sentence_transformers import SentenceTransformer


class TextEmbedder:
    """Класс для векторизации текста."""

    def __init__(self, model_name: Optional[str] = None, device: str = "cpu"):
        self.hf_model = SentenceTransformer(model_name, device=device)

    def execute(self, chunks: List[str]) -> List[List[float]]:
        # возвращает список списков
        return self.hf_model.encode(
            chunks,
            convert_to_numpy=False,
            show_progress_bar=False,
            normalize_embeddings=False
        )


if __name__ == "__main__":
    try:
        e = TextEmbedder(
            model_name="sergeyzh/LaBSE-ru-turbo",
            device="cpu"
        )
        v = e.execute(["Привет мир", "Ещё текст"])
        print("HF:", len(v), "×", len(v[0]))
    except Exception:
        pass
