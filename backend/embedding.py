import httpx
from config import QWEN_API_KEY

EMBED_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
EMBED_MODEL = "text-embedding-v3"
EMBED_DIM = 1024


async def get_embedding(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            EMBED_URL,
            headers={"Authorization": f"Bearer {QWEN_API_KEY}", "Content-Type": "application/json"},
            json={"model": EMBED_MODEL, "input": text, "dimensions": EMBED_DIM, "encoding_format": "float"}
        )
        res.raise_for_status()
        return res.json()["data"][0]["embedding"]
