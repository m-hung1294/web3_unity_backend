from eth_account.messages import encode_defunct
from web3 import Web3

w3 = Web3()

def login_message(wallet: str, nonce: str) -> str:
    return f"Login with wallet: {wallet}\nNonce: {nonce}"

def claim_message(wallet: str, session_id: str, timestamp: int) -> str:
    return f"claim|{wallet}|{session_id}|{timestamp}"

def verify_signature(expected_wallet: str, message: str, signature: str) -> bool:
    try:
        encoded = encode_defunct(text=message)
        recovered = w3.eth.account.recover_message(encoded, signature=signature)
        return recovered.lower() == expected_wallet.lower()
    except Exception:
        return False
