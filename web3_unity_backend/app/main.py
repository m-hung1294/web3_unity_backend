import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import nội bộ
from web3_unity_backend.app.models import init_db
from web3_unity_backend.app.routes import auth, leaderboard, nft, chain
from web3_unity_backend.app.services import web3_service

# Load biến môi trường từ .env
load_dotenv()

# Sửa lỗi import path khi chạy trực tiếp main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# -------------------------------
# 🚀 Khởi tạo FastAPI
# -------------------------------
app = FastAPI(
    title="Unity Web3 Backend",
    version="1.0.0",
    description="Backend API phục vụ Unity Web3 Game"
)

# -------------------------------
# 🌐 Cấu hình CORS (rất quan trọng cho Unity WebGL)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi domain (nên giới hạn sau này)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# ⚙️ Sự kiện khởi động
# -------------------------------
@app.on_event("startup")
def on_startup():
    init_db()
    web3_service.init_default_config()
    print("✅ Backend khởi động thành công và đã kết nối Web3.")

# -------------------------------
# 🧩 Route mặc định kiểm tra backend
# -------------------------------
@app.get("/")
def root():
    return {"message": "🚀 Unity Web3 Game Backend is running!"}

# -------------------------------
# 📦 Gắn các router chính
# -------------------------------
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(nft.router, prefix="/nft", tags=["NFT"])
app.include_router(chain.router, prefix="/chain", tags=["Chain"])

# -------------------------------
# 🧠 Alias tương thích Unity: /score/daily
# -------------------------------
@app.get("/score/daily", tags=["Compatibility"])
async def get_daily_score_alias():
    """
    Endpoint tạm để Unity gọi /score/daily mà không cần sửa code client.
    Gọi lại hàm tương ứng từ leaderboard router.
    """
    try:
        # Import trong hàm để tránh circular import
        from app.routes.leaderboard import get_daily_scores
        data = await get_daily_scores()
        return data
    except Exception as e:
        return {"error": f"Failed to fetch daily scores: {str(e)}"}
