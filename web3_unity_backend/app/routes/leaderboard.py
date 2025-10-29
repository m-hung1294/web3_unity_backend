from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models import Score, get_db

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

# 🟢 Lấy top điểm mọi thời đại (all-time)
@router.get("/all-time")
def get_all_time_top(db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=500, detail=f"Lỗi lấy bảng xếp hạng: {str(e)}")

# 🟣 Lấy top điểm trong ngày (daily)
@router.get("/daily")
def get_daily_top(db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=500, detail=f"Lỗi lấy bảng xếp hạng ngày: {str(e)}")

# 🟡 API cũ (cho Unity dùng nếu gọi /leaderboard/top)
@router.get("/top")
def get_top_scores(db: Session = Depends(get_db)):
    scores = db.query(Score).order_by(Score.score.desc()).limit(10).all()
    return [{"wallet": s.wallet, "score": s.score} for s in scores]

# 🔵 Gửi điểm mới từ Unity
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
