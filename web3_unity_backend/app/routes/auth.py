import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models import get_db, Nonce
from ..services.verification import login_message, verify_signature

router = APIRouter()

class NonceResp(BaseModel):
    wallet: str
    nonce: str
    message: str

@router.get("/nonce/{wallet}", response_model=NonceResp, summary="Get a login nonce for a wallet")
def get_nonce(wallet: str, db: Session = Depends(get_db)):
    wallet_l = wallet.lower()
    nonce = secrets.token_hex(16)
    row = Nonce(wallet=wallet_l, nonce=nonce)
    db.add(row)
    db.commit()
    message = login_message(wallet_l, nonce)
    return NonceResp(wallet=wallet_l, nonce=nonce, message=message)

class VerifyReq(BaseModel):
    wallet: str
    nonce: str
    signature: str

@router.post("/verify", summary="Verify login signature")
def verify_login(data: VerifyReq, db: Session = Depends(get_db)):
    message = login_message(data.wallet.lower(), data.nonce)
    ok = verify_signature(data.wallet, message, data.signature)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid signature")
    # Optionally delete nonce or mark as used
    db.query(Nonce).filter(Nonce.nonce == data.nonce).delete()
    db.commit()
    # In production you would issue a JWT. We'll return a boolean here.
    return {"verified": True, "wallet": data.wallet.lower()}
