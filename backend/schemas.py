from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInfo(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SaveCreate(BaseModel):
    save_name: str = "存档"
    world_bg: str
    char_name: str
    char_bg: str = ""
    hp: int = 100
    max_hp: int = 100
    stats: Dict[str, int] = {"str": 5, "int": 5, "cha": 5, "agi": 5}
    gold: int = 50
    turn: int = 0
    items: List[str] = []
    history: List[Dict[str, Any]] = []


class SaveUpdate(BaseModel):
    save_name: Optional[str] = None
    world_bg: Optional[str] = None
    char_name: Optional[str] = None
    char_bg: Optional[str] = None
    hp: Optional[int] = None
    max_hp: Optional[int] = None
    stats: Optional[Dict[str, int]] = None
    gold: Optional[int] = None
    turn: Optional[int] = None
    items: Optional[List[str]] = None
    history: Optional[List[Dict[str, Any]]] = None


class SaveInfo(BaseModel):
    id: UUID
    save_name: str
    char_name: str
    turn: int
    hp: int
    max_hp: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SaveDetail(SaveInfo):
    world_bg: str
    char_bg: str
    stats: Dict[str, int]
    gold: int
    items: List[str]
    history: List[Dict[str, Any]]


class ChatMessage(BaseModel):
    role: str
    content: str


class AIRequest(BaseModel):
    system_prompt: str
    messages: List[ChatMessage]
    save_id: Optional[UUID] = None
