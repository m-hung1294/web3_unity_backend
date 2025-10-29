import os
from dotenv import load_dotenv, find_dotenv
from web3 import Web3

# Load .env
env_path = find_dotenv(usecwd=True)
load_dotenv(env_path, override=True)

provider = os.getenv("WEB3_PROVIDER")
chain_id = int(os.getenv("CHAIN_ID", "0"))

w3 = Web3(Web3.HTTPProvider(provider))

print(f"🔗 Web3 Provider: {provider}")
print(f"✅ Connected: {w3.is_connected()} | Chain ID: {chain_id}")

def is_connected() -> bool:
    return w3.is_connected()

def get_balance(address: str):
    """Lấy số dư thật (ETH / SOMNIA)"""
    addr = Web3.to_checksum_address(address)
    balance = w3.eth.get_balance(addr)
    return w3.from_wei(balance, "ether")

def get_chain_info():
    """Thông tin mạng blockchain"""
    if not w3.is_connected():
        return None
    return {
        "chain_id": w3.eth.chain_id,
        "client": w3.client_version,
        "block_number": w3.eth.block_number,
        "provider": provider,
    }
