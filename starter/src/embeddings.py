"""Gemini embedding adapter (gemini-embedding-001, 768 chiều, L2-normalized)."""
import os
import time
from typing import Protocol

import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, question: str) -> list[float]: ...


class GeminiEmbedder:
    def __init__(self, model_name: str = "gemini-embedding-001", dimensions: int = 768) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Thiếu GEMINI_API_KEY trong .env")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.dimensions = dimensions

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        from google.genai import errors

        out: list[list[float]] = []
        batch_size = 20  # free tier: 100 text/phút -> 20 text mỗi ~13s
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for attempt in range(5):
                try:
                    resp = self.client.models.embed_content(
                        model=self.model_name,
                        contents=batch,
                        config=types.EmbedContentConfig(
                            task_type=task_type,
                            output_dimensionality=self.dimensions,
                        ),
                    )
                    break
                except errors.ClientError as e:
                    if e.code != 429 or attempt == 4:
                        raise
                    print(f"  429 quota, chờ 60s rồi thử lại (lần {attempt + 1})...")
                    time.sleep(60)
            for e in resp.embeddings:
                v = np.array(e.values)
                out.append((v / np.linalg.norm(v)).tolist())
            print(f"  embedded {min(i + batch_size, len(texts))}/{len(texts)}")
            if i + batch_size < len(texts):
                time.sleep(13)
        return out

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_query(self, question: str) -> list[float]:
        return self._embed([question], "RETRIEVAL_QUERY")[0]