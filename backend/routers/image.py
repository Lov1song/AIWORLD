from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import asyncio
import uuid
import httpx
from security import get_optional_user
from models import User
from config import QWEN_API_KEY

router = APIRouter(prefix="/ai", tags=["AI"])

WANX_CREATE = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
WANX_QUERY  = "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"

# 内存任务池，key=task_id，value={"status":..., "url":...}
_tasks: dict[str, dict] = {}


class ImageRequest(BaseModel):
    prompt: str
    style: Optional[str] = None


async def _run_task(task_id: str, prompt: str):
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "X-DashScope-Async": "enable",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            res = await client.post(WANX_CREATE, headers=headers, json={
                "model": "wanx2.1-t2i-turbo",
                "input": {"prompt": prompt},
                "parameters": {"size": "1024*576", "n": 1}
            })
            if res.status_code != 200:
                _tasks[task_id] = {"status": "failed", "url": None}
                return

            wanx_task_id = res.json()["output"]["task_id"]

            for _ in range(35):
                await asyncio.sleep(2)
                poll = await client.get(
                    WANX_QUERY.format(task_id=wanx_task_id),
                    headers={"Authorization": f"Bearer {QWEN_API_KEY}"}
                )
                output = poll.json().get("output", {})
                status = output.get("task_status")
                if status == "SUCCEEDED":
                    url = output["results"][0]["url"]
                    _tasks[task_id] = {"status": "done", "url": url}
                    return
                elif status in ("FAILED", "CANCELED"):
                    _tasks[task_id] = {"status": "failed", "url": None}
                    return

        _tasks[task_id] = {"status": "failed", "url": None}
    except Exception:
        _tasks[task_id] = {"status": "failed", "url": None}


@router.post("/image/start")
async def start_image(body: ImageRequest, user: Optional[User] = Depends(get_optional_user)):
    prompt = body.prompt[:300]
    if body.style:
        prompt = f"{body.style}风格，{prompt}"

    task_id = str(uuid.uuid4())
    _tasks[task_id] = {"status": "pending", "url": None}
    asyncio.create_task(_run_task(task_id, prompt))

    # 超过 200 个任务时清理最旧的一半
    if len(_tasks) > 200:
        old_keys = list(_tasks.keys())[:100]
        for k in old_keys:
            _tasks.pop(k, None)

    return {"task_id": task_id}


@router.get("/image/{task_id}")
async def get_image_result(task_id: str):
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    return task
