from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from models import User, GameSave
from schemas import SaveCreate, SaveUpdate, SaveInfo, SaveDetail
from security import get_current_user

router = APIRouter(prefix="/game", tags=["存档"])


@router.post("/saves", response_model=SaveDetail, status_code=201)
def create_save(body: SaveCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    save = GameSave(user_id=user.id, **body.model_dump())
    db.add(save)
    db.commit()
    db.refresh(save)
    return save


@router.get("/saves", response_model=List[SaveInfo])
def list_saves(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(GameSave).filter(GameSave.user_id == user.id)\
        .order_by(GameSave.updated_at.desc()).all()


@router.get("/saves/{save_id}", response_model=SaveDetail)
def get_save(save_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    save = db.query(GameSave).filter(GameSave.id == save_id, GameSave.user_id == user.id).first()
    if not save:
        raise HTTPException(status_code=404, detail="存档不存在")
    return save


@router.put("/saves/{save_id}", response_model=SaveDetail)
def update_save(save_id: UUID, body: SaveUpdate, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    save = db.query(GameSave).filter(GameSave.id == save_id, GameSave.user_id == user.id).first()
    if not save:
        raise HTTPException(status_code=404, detail="存档不存在")
    for key, val in body.model_dump(exclude_none=True).items():
        setattr(save, key, val)
    db.commit()
    db.refresh(save)
    return save


@router.delete("/saves/{save_id}", status_code=204)
def delete_save(save_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    save = db.query(GameSave).filter(GameSave.id == save_id, GameSave.user_id == user.id).first()
    if not save:
        raise HTTPException(status_code=404, detail="存档不存在")
    db.delete(save)
    db.commit()
