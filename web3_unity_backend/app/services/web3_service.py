import os
from web3 import Web3

# -------------------------------------
# 🌐 Global Web3 state
# -------------------------------------
w3 = None
RPC_URL = None
CHAIN_ID = None
NFT_CONTRACT = None


# -------------------------------------
# 🚀 Khởi tạo mặc định khi backend start
# -------------------------------------
def init_default_config():
    """
    Load config từ .env khi server khởi động.
    Nếu .env không có, sẽ tự gán giá trị mặc định local.
    """
    global RPC_URL, CHAIN_ID, NFT_CONTRACT, w3

    RPC_URL = (os.getenv("RPC_URL") or "http://127.0.0.1:8545").strip()
    CHAIN_ID = int(os.getenv("CHAIN_ID") or 1337)
    NFT_CONTRACT = (os.getenv("NFT_CONTRACT") or "0x0000000000000000000000000000000000000000").strip()

    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if w3.is_connected():
            print(f"✅ Web3 connected to {RPC_URL} (chain={CHAIN_ID})")
        else:
            print(f"⚠️ Web3 not connected at {RPC_URL} (chain={CHAIN_ID})")
    except Exception as e:
        w3 = None
        print(f"❌ Web3 initialization failed: {e}")


# -------------------------------------
# 🔧 Cập nhật config runtime (Unity gửi lên)
# -------------------------------------
def set_config(rpc_url: str, chain_id: int, nft_contract: str):
    """Cập nhật cấu hình khi Unity gửi qua API."""
    global RPC_URL, CHAIN_ID, NFT_CONTRACT, w3
    RPC_URL, CHAIN_ID, NFT_CONTRACT = rpc_url, chain_id, nft_contract

    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if w3.is_connected():
            print(f"✅ Config updated: {RPC_URL} | chain={CHAIN_ID} | contract={NFT_CONTRACT}")
        else:
            print(f"⚠️ Web3 connection failed for {RPC_URL}")
    except Exception as e:
        w3 = None
        print(f"❌ Error setting Web3 config: {e}")


# -------------------------------------
# 💰 Lấy số dư ví
# -------------------------------------
def get_balance(address: str):
    """Trả về số dư của địa chỉ ví (ETH)."""
    if not w3:
        raise RuntimeError("Web3 chưa được khởi tạo.")

    try:
        balance_wei = w3.eth.get_balance(address)
        return w3.from_wei(balance_wei, "ether")
    except Exception as e:
        print(f"⚠️ Lỗi get_balance: {e}")
        return None


# -------------------------------------
# 🔢 Lấy block mới nhất
# -------------------------------------
def get_latest_block():
    """Trả về block number hiện tại."""
    if not w3:
        raise RuntimeError("Web3 chưa được khởi tạo.")
    try:
        return w3.eth.block_number
    except Exception as e:
        print(f"⚠️ Lỗi get_latest_block: {e}")
        return None


# -------------------------------------
# 🧩 Kiểm tra kết nối Web3
# -------------------------------------
def is_connected():
    """Trả True nếu Web3 đang kết nối RPC hợp lệ."""
    return w3 is not None and w3.is_connected()


# -------------------------------------
# 🔨 Build transaction cơ bản (EIP-1559 fallback)
# -------------------------------------
def build_tx_common(acct_addr: str):
    """Build transaction cơ bản cho blockchain."""
    if not w3:
        raise RuntimeError("❌ Web3 chưa được cấu hình!")

    base = {
        "from": acct_addr,
        "nonce": w3.eth.get_transaction_count(acct_addr),
        "chainId": CHAIN_ID,
        "gas": 300000,
    }

    try:
        # Nếu RPC hỗ trợ EIP-1559
        _ = w3.eth.fee_history(1, "latest", [10])
        base["maxFeePerGas"] = w3.to_wei("2", "gwei")
        base["maxPriorityFeePerGas"] = w3.to_wei("1", "gwei")
    except Exception:
        base["gasPrice"] = w3.to_wei("2", "gwei")

    return base
