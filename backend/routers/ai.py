from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import httpx
from schemas import AIRequest
from security import get_optional_user
from models import User
from database import get_db
from routers.facts import query_relevant_facts
from config import QWEN_API_KEY

QWEN_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
async def chat(body: AIRequest, db: Session = Depends(get_db), user: Optional[User] = Depends(get_optional_user)):
    system_prompt = body.system_prompt

    if body.save_id and body.messages:
        last_msg = body.messages[-1].content
        facts = await query_relevant_facts(body.save_id, last_msg, db)
        if facts:
            recall = "\n".join(f"- {f}" for f in facts)
            system_prompt += f"\n\n【世界记忆·相关事实】\n{recall}"

    messages = [{"role": "system", "content": system_prompt}]
    messages += [m.model_dump() for m in body.messages]

    async def stream():
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST", QWEN_URL,
                headers={"Authorization": f"Bearer {QWEN_API_KEY}", "Content-Type": "application/json"},
                json={"model": "qwen-plus", "messages": messages, "stream": True}
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        yield line + "\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
