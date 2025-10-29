import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import get_db, Nonce
from ..services.verification import login_message, verify_signature

router = APIRouter()

@router.get("/nonce/{wallet}")
def get_nonce(wallet: str, db: Session = Depends(get_db)):
    nonce = secrets.token_hex(16)
    row = Nonce(wallet=wallet.lower(), nonce=nonce)
    db.add(row)
    db.commit()
    message = login_message(wallet, nonce)
    return {"wallet": wallet, "nonce": nonce, "message": message}

@router.post("/verify")
def verify_login(wallet: str, nonce: str, signature: str, db: Session = Depends(get_db)):
    msg = login_message(wallet, nonce)
    if not verify_signature(wallet, msg, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    db.query(Nonce).filter(Nonce.nonce == nonce).delete()
    db.commit()
    return {"verified": True}
