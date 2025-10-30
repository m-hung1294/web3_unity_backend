from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..models import Score, get_db

# ✅ Router có prefix /leaderboard
router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

# 🟢 GET /leaderboard/daily
@router.get("/daily")
def get_daily(db: Session = Depends(get_db)):
    try:
        start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        scores = (
            db.query(Score)
            .filter(Score.timestamp >= start_of_day)
            .order_by(Score.score.desc())
            .limit(10)
            .all()
        )
        return {
            "status": "ok",
            "updated_at": datetime.utcnow(),
            "leaderboard": [
                {"wallet": s.wallet, "score": s.score, "time": s.timestamp}
                for s in scores
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi /leaderboard/daily: {str(e)}")


# 🔵 GET /leaderboard/all-time
@router.get("/all-time")
def get_all_time(db: Session = Depends(get_db)):
    try:
        scores = db.query(Score).order_by(Score.score.desc()).limit(10).all()
        return {
            "status": "ok",
            "updated_at": datetime.utcnow(),
            "leaderboard": [
                {"wallet": s.wallet, "score": s.score, "time": s.timestamp}
                for s in scores
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi /leaderboard/all-time: {str(e)}")


# 🟣 POST /leaderboard/submit
@router.post("/submit")
def submit_score(wallet: str, score: float, session_id: str, db: Session = Depends(get_db)):
    try:
        new_score = Score(wallet=wallet.lower(), score=score, session_id=session_id)
        db.add(new_score)
        db.commit()
        return {"ok": True, "wallet": wallet, "score": score}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi lưu điểm: {e}")
