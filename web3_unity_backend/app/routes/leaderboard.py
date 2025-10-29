from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..models import Score, get_db

router = APIRouter(tags=["Leaderboard"])

# --------------------------
# 🟢 Route gốc: /daily & /all-time (Unity đang gọi)
# --------------------------

@router.get("/daily")
def get_daily_direct(db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=500, detail=f"Lỗi /daily: {str(e)}")


@router.get("/all-time")
def get_all_time_direct(db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=500, detail=f"Lỗi /all-time: {str(e)}")


# --------------------------
# 🟣 Giữ nguyên các API có prefix /leaderboard
# --------------------------

router2 = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router2.get("/daily")
def get_daily_prefixed(db: Session = Depends(get_db)):
    return get_daily_direct(db)

@router2.get("/all-time")
def get_all_time_prefixed(db: Session = Depends(get_db)):
    return get_all_time_direct(db)
