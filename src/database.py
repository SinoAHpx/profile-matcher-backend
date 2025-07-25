"""
Database connection and utilities using Supabase client
数据库连接和工具函数 - 使用Supabase客户端
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")

# 全局Supabase客户端实例
_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """获取Supabase客户端实例（使用匿名密钥）"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _supabase_client

def get_supabase_admin_client() -> Client:
    """获取Supabase管理员客户端实例（使用服务密钥，用于绕过RLS）"""
    global _supabase_admin_client
    if _supabase_admin_client is None:
        if not SUPABASE_SERVICE_KEY:
            raise ValueError("SUPABASE_SERVICE_KEY must be set for admin operations")
        _supabase_admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _supabase_admin_client

async def init_supabase():
    """初始化Supabase客户端"""
    # 预初始化客户端
    get_supabase_client()
    if SUPABASE_SERVICE_KEY:
        get_supabase_admin_client()
    print("✓ Supabase客户端已初始化")

async def close_supabase():
    """关闭Supabase客户端连接"""
    global _supabase_client, _supabase_admin_client
    # Supabase客户端不需要显式关闭，但我们可以清理引用
    _supabase_client = None
    _supabase_admin_client = None
    print("✓ Supabase客户端连接已清理")

async def execute_schema_file(file_path: str):
    """执行SQL架构文件（使用Supabase管理员客户端）"""
    try:
        admin_client = get_supabase_admin_client()
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 使用Supabase的rpc功能执行原始SQL
        # 注意：这需要在Supabase中创建一个执行SQL的函数
        result = admin_client.rpc('execute_sql', {'sql_query': sql_content}).execute()
        print(f"✓ 成功执行架构文件: {file_path}")
        return result
    except Exception as e:
        print(f"❌ 执行架构文件失败 {file_path}: {e}")
        raise

async def setup_database():
    """设置数据库架构"""
    print("注意: 使用Supabase时，建议通过Supabase Dashboard或迁移工具执行架构文件")
    print("当前函数保留用于兼容性，但可能需要手动执行SQL文件")

    schema_files = [
        "scripts/sql-scripts/01_profile_schema.sql",
        "scripts/sql-scripts/02_attributes_schema.sql",
        "scripts/sql-scripts/03_ego_schema.sql"
    ]

    for schema_file in schema_files:
        if os.path.exists(schema_file):
            print(f"架构文件存在: {schema_file}")
            # 注释掉自动执行，因为Supabase通常通过Dashboard管理架构
            await execute_schema_file(schema_file)
        else:
            print(f"警告: 架构文件不存在: {schema_file}")

# 兼容性函数 - 为了保持API兼容性
async def init_db_pool():
    """兼容性函数 - 重定向到init_supabase"""
    await init_supabase()

async def close_db_pool():
    """兼容性函数 - 重定向到close_supabase"""
    await close_supabase()
