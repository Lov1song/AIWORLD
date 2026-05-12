from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    saves = relationship("GameSave", back_populates="user", cascade="all, delete-orphan")


class GameSave(Base):
    __tablename__ = "game_saves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    save_name = Column(String(100), nullable=False, default="存档")
    world_bg = Column(String(2000), nullable=False)
    char_name = Column(String(50), nullable=False)
    char_bg = Column(String(500), default="")
    hp = Column(Integer, default=100)
    max_hp = Column(Integer, default=100)
    stats = Column(JSON, default={"str": 5, "int": 5, "cha": 5, "agi": 5})
    gold = Column(Integer, default=50)
    turn = Column(Integer, default=0)
    items = Column(JSON, default=[])
    history = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="saves")
    facts = relationship("WorldFact", back_populates="save", cascade="all, delete-orphan")


class WorldFact(Base):
    __tablename__ = "world_facts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    save_id = Column(UUID(as_uuid=True), ForeignKey("game_saves.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1024))
    turn = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    save = relationship("GameSave", back_populates="facts")
