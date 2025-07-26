from supabase import create_client, Client
from src.config.settings import settings

def get_supabase_admin_client() -> Client:
    """获取具有service_role权限的Supabase客户端"""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)