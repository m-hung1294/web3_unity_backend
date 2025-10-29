from fastapi import APIRouter, HTTPException, Query
from web3 import Web3
from ..services import web3_service as w3s

router = APIRouter(prefix="/chain", tags=["Blockchain"])

# 🟢 Kiểm tra trạng thái Web3
@router.get("/status", summary="Kiểm tra trạng thái Web3")
async def get_status():
    try:
        info = w3s.get_chain_info()
        if not info:
            raise HTTPException(status_code=503, detail="Web3 chưa được kết nối")
        return {"status": "✅ Connected", **info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🟣 Lấy block mới nhất
@router.get("/block/latest", summary="Lấy block mới nhất")
async def get_latest_block():
    try:
        if not w3s.is_connected():
            raise HTTPException(status_code=503, detail="Web3 chưa được kết nối")
        block = w3s.w3.eth.get_block("latest")
        return {
            "block_number": block.number,
            "timestamp": block.timestamp,
            "hash": block.hash.hex(),
            "tx_count": len(block.transactions),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy block: {e}")

# 🟡 Lấy số dư ví (từ Unity)
@router.get("/balance", summary="Lấy số dư ví người chơi")
async def get_balance(address: str = Query(..., description="Địa chỉ ví người chơi")):
    try:
        if not w3s.is_connected():
            raise HTTPException(status_code=503, detail="Web3 chưa được kết nối")
        if not Web3.is_address(address):
            raise HTTPException(status_code=400, detail="Địa chỉ ví không hợp lệ")
        balance = w3s.get_balance(address)
        return {"address": address, "balance": f"{balance} ETH"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy số dư ví: {e}")

# ⛽ Thông tin gas hiện tại
@router.get("/gas", summary="Lấy thông tin gas hiện tại")
async def get_gas():
    try:
        if not w3s.is_connected():
            raise HTTPException(status_code=503, detail="Web3 chưa được kết nối")
        gas_price = w3s.w3.eth.gas_price
        return {
            "gas_price_wei": gas_price,
            "gas_price_gwei": w3s.w3.from_wei(gas_price, "gwei"),
            "block_number": w3s.w3.eth.block_number,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy gas: {e}")

# 💰 Lấy số dư token ERC20
@router.get("/token_balance", summary="Lấy số dư token ERC20 của ví")
async def get_token_balance(
    token_address: str = Query(..., description="Địa chỉ contract ERC20"),
    wallet_address: str = Query(..., description="Địa chỉ ví người chơi")
):
    try:
        if not w3s.is_connected():
            raise HTTPException(status_code=503, detail="Web3 chưa được kết nối")

        abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function",
            },
        ]

        contract = w3s.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
        balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
        decimals = contract.functions.decimals().call()
        symbol = contract.functions.symbol().call()

        readable_balance = balance / (10 ** decimals)
        return {
            "token": symbol,
            "balance": readable_balance,
            "decimals": decimals,
            "wallet": wallet_address
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy số dư token: {str(e)}")


# 🚀 Gửi giao dịch thật (ví backend ký)
@router.post("/send_tx", summary="Gửi giao dịch thật từ backend")
async def send_transaction(payload: dict):
    """
    Gửi giao dịch thực tế (ví dụ chuyển token, gửi ETH)
    payload = {
        "to": "0xVíNhận",
        "value_eth": 0.001,
        "data": "0x..."  # tùy chọn
    }
    """
    try:
        private_key = os.getenv("PRIVATE_KEY")
        from_addr = os.getenv("WALLET_ADDRESS")

        if not private_key or not from_addr:
            raise HTTPException(status_code=400, detail="Thiếu PRIVATE_KEY hoặc WALLET_ADDRESS trong .env")

        if not w3s.is_connected():
            raise HTTPException(status_code=503, detail="Web3 chưa được kết nối")

        to_addr = payload.get("to")
        value_eth = float(payload.get("value_eth", 0))
        data = payload.get("data", "0x")

        nonce = w3s.w3.eth.get_transaction_count(Web3.to_checksum_address(from_addr))
        tx = {
            "nonce": nonce,
            "to": Web3.to_checksum_address(to_addr),
            "value": w3s.w3.to_wei(value_eth, "ether"),
            "gas": 21000,
            "gasPrice": w3s.w3.eth.gas_price,
            "data": data.encode() if isinstance(data, str) else data,
            "chainId": int(os.getenv("CHAIN_ID")),
        }

        signed_tx = w3s.w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3s.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return {"tx_hash": tx_hash.hex(), "from": from_addr, "to": to_addr, "value_eth": value_eth}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi gửi giao dịch: {str(e)}")
