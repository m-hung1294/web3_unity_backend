import time
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import get_db, Score
from ..services import web3_service as w3s
from ..services.verification import claim_message, verify_signature

router = APIRouter()

class ClaimReq(BaseModel):
    wallet: str = Field(..., description="Receiver wallet")
    session_id: str = Field(..., description="The game session to claim")
    timestamp: int
    signature: str

def _day_token_id(dt) -> int:
    d = dt.date() if hasattr(dt, "date") else dt
    return d.year * 10_000 + d.month * 100 + d.day  # e.g., 20251031

@router.post("/claim", summary="Claim your score as ERC1155 points (1 point = 1 token, token_id = YYYYMMDD)")
def claim_points(req: ClaimReq, db: Session = Depends(get_db)):
    # Anti-replay
    now = int(time.time())
    if abs(now - req.timestamp) > 300:
        raise HTTPException(status_code=400, detail="Invalid timestamp (too old/new)")

    # Verify signature (claim|wallet|session_id|timestamp)
    msg = claim_message(req.wallet, req.session_id, req.timestamp)
    if not verify_signature(req.wallet, msg, req.signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    row = db.query(Score).filter(Score.session_id == req.session_id, Score.wallet == req.wallet.lower()).first()
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    if row.claimed:
        raise HTTPException(status_code=400, detail="Already claimed")

    token_id = _day_token_id(row.timestamp)
    amount = int(row.score)

    # Mint via Web3
    try:
        tx_hash = w3s.mint_points(req.wallet, token_id, amount)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mint failed: {e}")

    row.claimed = True
    db.commit()
    return {"status": "minted", "wallet": req.wallet.lower(), "token_id": token_id, "amount": amount, "tx": tx_hash}

@router.get("/ping", summary="web3 connectivity check")
def ping():
    return w3s.check_connection()
