from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    app_name: str = "Profile Matcher Backend"
    debug: bool = False
    
    # Supabase配置
    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str
    supabase_storage_bucket: str
    
    # JWT密钥
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    
    # 文件上传设置
    max_file_size_mb: int = 10
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 忽略额外的字段

def get_allowed_origins() -> List[str]:
    origins = os.getenv("ALLOWED_ORIGINS", "*")
    if origins == "*":
        return ["*"]
    return [origin.strip() for origin in origins.split(",")]

settings = Settings()
allowed_origins = get_allowed_origins()