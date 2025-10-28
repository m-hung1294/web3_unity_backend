from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()

# -------------------------------
# 🟢 1. Kiểm tra trạng thái chain
# -------------------------------
@router.get("/status")
async def get_chain_status():
    """
    Kiểm tra trạng thái backend chain service.
    """
    return {
        "status": "✅ Chain API active",
        "network": "local",
        "provider": "http://127.0.0.1:8545"
    }

# -------------------------------
# 🔵 2. Lấy thông tin mạng (network info)
# -------------------------------
@router.get("/network")
async def get_network_info():
    """
    Trả thông tin mạng blockchain.
    """
    return {
        "chain_id": 1337,
        "network_name": "Localhost",
        "rpc_url": "http://127.0.0.1:8545",
        "symbol": "ETH",
        "decimals": 18
    }

# -------------------------------
# 🟣 3. Lấy thông tin block hiện tại (giả lập)
# -------------------------------
@router.get("/block/latest")
async def get_latest_block():
    """
    Trả block number giả lập (demo).
    """
    # Ở đây có thể gọi web3.eth.block_number nếu đã config web3_service
    latest_block = 1234567
    return {"latest_block": latest_block}

# -------------------------------
# 🟡 4. Lấy số dư ví (mock hoặc thật)
# -------------------------------
@router.get("/balance")
async def get_wallet_balance(address: Optional[str] = Query(None, description="Địa chỉ ví cần kiểm tra")):
    """
    Lấy số dư ví (tạm thời mock, có thể tích hợp Web3 sau).
    """
    if not address:
        return {"error": "Missing address parameter"}
    # Tạm thời giả lập số dư
    return {"address": address, "balance": "0.1234 ETH"}
