#!/usr/bin/env python3
"""
Database initialization script
数据库初始化脚本
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import setup_database, init_supabase, close_supabase

async def main():
    """主函数"""
    print("开始初始化Supabase连接...")

    try:
        # 初始化Supabase客户端
        await init_supabase()

        # 执行架构设置（注意：使用Supabase时建议通过Dashboard执行）
        await setup_database()

        print("\nSupabase客户端初始化成功！")
        print("\n注意：使用Supabase时，建议通过以下方式管理数据库架构：")
        print("1. 使用Supabase Dashboard的SQL编辑器")
        print("2. 使用Supabase CLI进行迁移")
        print("3. 手动执行scripts/sql-scripts/目录下的SQL文件")
        print("\n可用的API端点：")
        print("- /api/v1/profile/* - 用户基本档案管理")
        print("- /api/v1/attributes/* - 用户属性/爱好管理")
        print("- /api/v1/ego/* - 人格特质/认知功能管理")
        print("\n访问 http://localhost:8000/docs 查看完整API文档")

    except Exception as e:
        print(f"❌ Supabase初始化失败: {e}")
        print("请检查环境变量：SUPABASE_URL, SUPABASE_ANON_KEY")
        sys.exit(1)
    finally:
        # 清理Supabase客户端
        await close_supabase()

if __name__ == "__main__":
    asyncio.run(main())
