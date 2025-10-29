from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routes import chain, wallet, leaderboard
from .models import init_db

app = FastAPI(title="Unity Web3 Backend")

# 🧱 Cấu hình CORS (cho phép Unity WebGL truy cập)
origins = os.getenv("CORS_ORIGINS", "").split(",")
origins = [o.strip() for o in origins if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🗄️ Tạo database nếu chưa có
init_db()

# 🔗 Gắn các router
app.include_router(chain.router)
app.include_router(wallet.router)
app.include_router(leaderboard.router)

@app.get("/health")
def health():
    return {"ok": True, "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web3_unity_backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
