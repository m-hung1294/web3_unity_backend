# Unity Web3 Game Backend (FastAPI + Web3.py)

End-to-end example showing:
- Wallet login (nonce + signature verification)
- Score submission with anti-replay
- Daily & All-time leaderboard
- Claim score as ERC1155 points (1 point = 1 token) with token id = YYYYMMDD
- Unity-friendly JSON APIs (CORS enabled)

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # fill RPC_URL, PRIVATE_KEY, ERC1155_ADDRESS
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API docs.
