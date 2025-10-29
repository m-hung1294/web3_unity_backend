from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import các module router
from .routes import chain, wallet, leaderboard
from .models import init_db

# ---------------------------------------------
# 🧱 Khởi tạo ứng dụng FastAPI
# ---------------------------------------------
app = FastAPI(title="Unity Web3 Backend", version="1.1.0")

# ---------------------------------------------
# 🌐 Cấu hình CORS để Unity WebGL có thể gọi API
# ---------------------------------------------
origins = os.getenv("CORS_ORIGINS", "").split(",")
origins = [o.strip() for o in origins if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],  # Cho phép tất cả nếu chưa config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------
# 🗄️ Khởi tạo Database
# ---------------------------------------------
init_db()

# ---------------------------------------------
# 🔗 Gắn các router (API)
# ---------------------------------------------
# Blockchain
app.include_router(chain.router)
# Wallet
app.include_router(wallet.router)
# Leaderboard (bao gồm cả /daily và /all-time)
app.include_router(leaderboard.router)
app.include_router(leaderboard.router2)

# ---------------------------------------------
# 🧩 Endpoint kiểm tra nhanh backend
# ---------------------------------------------
@app.get("/health")
def health():
    return {"ok": True, "status": "running", "version": "1.1.0"}

# ---------------------------------------------
# 🚀 Chạy server cục bộ
# ---------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web3_unity_backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
