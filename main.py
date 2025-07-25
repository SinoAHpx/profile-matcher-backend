from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.v1.profile import router as profile_router
# TODO: Complete Supabase client migration for these modules
# from src.api.v1.attributes import router as attributes_router
# from src.api.v1.ego import router as ego_router
from src.database import init_supabase, close_supabase

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化Supabase客户端
    await init_supabase()
    yield
    # 关闭时清理Supabase客户端
    await close_supabase()

app = FastAPI(
    title="Profile Matcher Backend",
    description="用户档案匹配系统后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 注册路由
# app.include_router(users_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
# TODO: Re-enable after completing Supabase client migration
# app.include_router(attributes_router, prefix="/api/v1")
# app.include_router(ego_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Profile Matcher Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "schemas": {
            "profile": "用户基本档案信息",
            "attributes": "用户属性/爱好管理",
            "ego": "人格特质/认知功能"
        }
    }

