import os
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    UniqueConstraint, create_engine, func
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./game.db")

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, index=True)
    wallet = Column(String, index=True)           # lowercase
    score = Column(Float)
    session_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    claimed = Column(Boolean, default=False)      # claimed as NFT yet?

    __table_args__ = (
        UniqueConstraint("session_id", name="uq_scores_session"),
    )

class Nonce(Base):
    __tablename__ = "nonces"
    id = Column(Integer, primary_key=True, index=True)
    wallet = Column(String, index=True)
    nonce = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
