from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import các module route
from .routes import chain, wallet, leaderboard
from .models import init_db


# =====================================
# 🚀 TẠO ỨNG DỤNG FASTAPI
# =====================================
app = FastAPI(
    title="Unity Web3 Backend",
    version="1.2.0",
    description="Backend phục vụ game Unity WebGL có tích hợp Web3 (Blockchain, Wallet, Leaderboard)"
)


# =====================================
# 🌐 CẤU HÌNH CORS (cho Unity WebGL)
# =====================================
origins = os.getenv("CORS_ORIGINS", "").split(",")
origins = [o.strip() for o in origins if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],  # Cho phép mọi domain nếu chưa config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# 🗄️ KHỞI TẠO DATABASE (SQLite hoặc khác)
# =====================================
init_db()


# =====================================
# 🔗 ĐĂNG KÝ ROUTES
# =====================================
app.include_router(chain.router)
app.include_router(wallet.router)
app.include_router(leaderboard.router)


# =====================================
# 💓 KIỂM TRA TRẠNG THÁI BACKEND
# =====================================
@app.get("/health", tags=["System"])
def health():
    return {
        "ok": True,
        "status": "running",
        "version": "1.2.0",
        "message": "Unity Web3 Backend đang hoạt động ổn định 🚀"
    }


# =====================================
# 🧩 TRANG CHỦ (tuỳ chọn)
# =====================================
@app.get("/", tags=["System"])
def home():
    return {
        "message": "Chào mừng đến với Unity Web3 Backend API!",
        "docs": "/docs",
        "status": "✅ Ready",
        "routes": ["/chain", "/wallet", "/daily", "/all-time", "/leaderboard"]
    }


# =====================================
# ▶️ CHẠY SERVER LOCAL (nếu chạy thủ công)
# =====================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web3_unity_backend.app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
