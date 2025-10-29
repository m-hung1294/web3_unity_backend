from fastapi import APIRouter, HTTPException
from ..services import web3_service as w3s
from web3 import Web3

router = APIRouter(prefix="/wallet", tags=["Wallet"])

@router.post("/connect")
def connect_wallet(payload: dict):
    """Unity gửi ví người chơi lên backend"""
    wallet = payload.get("wallet")
    if not wallet or not Web3.is_address(wallet):
        raise HTTPException(status_code=400, detail="Địa chỉ ví không hợp lệ")
    return {"ok": True, "wallet": Web3.to_checksum_address(wallet)}

@router.get("/balance/{address}")
def get_balance(address: str):
    """Lấy số dư thật từ blockchain"""
    try:
        balance = w3s.get_balance(address)
        return {"address": address, "balance": f"{balance} ETH"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy số dư: {e}")
