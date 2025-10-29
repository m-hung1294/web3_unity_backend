from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..models import Score, get_db

router = APIRouter()

@router.get("/top")
def get_top_scores(db: Session = Depends(get_db)):
    scores = db.query(Score).order_by(Score.score.desc()).limit(10).all()
    return [{"wallet": s.wallet, "score": s.score} for s in scores]

@router.post("/submit")
def submit_score(wallet: str, score: float, session_id: str, db: Session = Depends(get_db)):
    try:
        new_score = Score(wallet=wallet.lower(), score=score, session_id=session_id)
        db.add(new_score)
        db.commit()
        return {"ok": True, "score": score}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving score: {e}")
