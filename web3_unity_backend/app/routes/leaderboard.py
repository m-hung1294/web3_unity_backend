import time
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..models import get_db, Score
from ..services.verification import score_message, verify_signature

router = APIRouter()

class ScoreRequest(BaseModel):
    wallet: str
    score: int
    session_id: str
    timestamp: int
    signature: str

@router.post("/submit", summary="Submit score (signed by the player's wallet)")
def submit_score(req: ScoreRequest, db: Session = Depends(get_db)):
    # Check timestamp drift (anti replay)
    now = int(time.time())
    if abs(now - req.timestamp) > 300:
        raise HTTPException(status_code=400, detail="Invalid timestamp (too old/new)")

    # Verify signature
    msg = score_message(req.wallet, req.score, req.session_id, req.timestamp)
    if not verify_signature(req.wallet, msg, req.signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    wallet_l = req.wallet.lower()
    exists = db.query(Score).filter(Score.session_id == req.session_id).first()
    if exists:
        # idempotent: keep the better score for the session
        if req.score > exists.score:
            exists.score = req.score
            exists.timestamp = datetime.utcnow()
            exists.wallet = wallet_l
            db.commit()
            db.refresh(exists)
        row = exists
    else:
        row = Score(wallet=wallet_l, score=req.score, session_id=req.session_id, timestamp=datetime.utcnow())
        db.add(row); db.commit(); db.refresh(row)

    # Compute player's best
    best_all = db.query(func.max(Score.score)).filter(Score.wallet == wallet_l).scalar() or 0
    today = date.today()
    best_today = (
        db.query(func.max(Score.score))
        .filter(Score.wallet == wallet_l)
        .filter(func.date(Score.timestamp) == today.isoformat())
        .scalar()
        or 0
    )
    return {
        "status": "ok",
        "wallet": wallet_l,
        "score": row.score,
        "best_today": int(best_today),
        "best_all_time": int(best_all),
        "claimed": row.claimed,
    }

class TopRow(BaseModel):
    wallet: str
    best: int

@router.get("/top", summary="Return top leaderboard", response_model=list[TopRow])
def get_top(
    period: str = Query("alltime", pattern="^(daily|alltime)$"),
    limit: int = 10,
    db: Session = Depends(get_db),
):
    q = db.query(Score.wallet, func.max(Score.score).label("best"))
    if period == "daily":
        today = date.today()
        q = q.filter(func.date(Score.timestamp) == today.isoformat())
    q = q.group_by(Score.wallet).order_by(desc("best")).limit(limit)
    rows = [{"wallet": w, "best": int(b)} for (w, b) in q.all()]
    return rows

@router.get("/best/{wallet}", summary="Best score of a wallet (daily & all-time)")
def best_score(wallet: str, db: Session = Depends(get_db)):
    wallet_l = wallet.lower()
    today = date.today()
    best_all = db.query(func.max(Score.score)).filter(Score.wallet == wallet_l).scalar() or 0
    best_today = (
        db.query(func.max(Score.score))
        .filter(Score.wallet == wallet_l)
        .filter(func.date(Score.timestamp) == today.isoformat())
        .scalar()
        or 0
    )
    return {"wallet": wallet_l, "best_today": int(best_today), "best_all_time": int(best_all)}
