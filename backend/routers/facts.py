from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
from pydantic import BaseModel
from database import get_db
from models import User, GameSave, WorldFact
from security import get_current_user
from embedding import get_embedding, EMBED_DIM

router = APIRouter(prefix="/game", tags=["事实记忆"])


class FactCreate(BaseModel):
    content: str
    turn: int = 0


@router.post("/saves/{save_id}/facts", status_code=201)
async def store_fact(save_id: UUID, body: FactCreate,
                     db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    save = db.query(GameSave).filter(GameSave.id == save_id, GameSave.user_id == user.id).first()
    if not save:
        raise HTTPException(status_code=404, detail="存档不存在")

    embedding = await get_embedding(body.content)
    fact = WorldFact(save_id=save_id, content=body.content, embedding=embedding, turn=body.turn)
    db.add(fact)
    db.commit()
    return {"id": str(fact.id)}


async def query_relevant_facts(save_id: UUID, query: str, db: Session, top_k: int = 5) -> list[str]:
    try:
        query_vec = await get_embedding(query)
        vec_str = "[" + ",".join(str(v) for v in query_vec) + "]"
        rows = db.execute(
            text("""
                SELECT content FROM world_facts
                WHERE save_id = :save_id
                ORDER BY embedding <=> CAST(:vec AS vector)
                LIMIT :k
            """),
            {"save_id": str(save_id), "vec": vec_str, "k": top_k}
        ).fetchall()
        return [r[0] for r in rows]
    except Exception:
        return []
