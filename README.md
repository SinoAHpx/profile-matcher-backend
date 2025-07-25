# Profile Matcher Backend
# Profile Matcher 后端

A comprehensive backend system for user profile matching using Supabase, FastAPI, and PostgreSQL. This system supports Jung's 8 cognitive functions personality typing, user interests and hobbies management, and an extensible personality traits system.

一个使用 Supabase、FastAPI 和 PostgreSQL 构建的综合用户档案匹配后端系统。支持荣格8种认知功能人格类型分析、用户兴趣爱好管理和可扩展的人格特质系统。

## 🚀 Recent Improvements (2025-01-25)
## 🚀 最新改进 (2025-01-25)

### ✅ Optimized Supabase Integration / 优化的Supabase集成
- **Removed redundant fields** from profile tables that duplicate `auth.users` fields / **移除冗余字段**，避免与`auth.users`表重复
- **Replaced asyncpg** with native Supabase Python client for better integration / **替换asyncpg**为原生Supabase Python客户端，提供更好的集成
- **Enhanced authentication** with proper JWT token handling and RLS integration / **增强认证**，支持JWT令牌处理和RLS集成
- **Optimized schema** to leverage Supabase's built-in user management features / **优化架构**，充分利用Supabase内置用户管理功能

### ✅ Comprehensive Test Suite / 综合测试套件
- **Profile Tests** (`tests/test_profile.py`): User profile CRUD, dictionaries, search functionality / 用户档案CRUD、字典、搜索功能
- **Attributes Tests** (`tests/test_attributes.py`): Category trees, hierarchical navigation, user associations / 分类树、层级导航、用户关联
- **Ego Tests** (`tests/test_ego.py`): Jung's 8 cognitive functions, personality traits, assessments / 荣格8种认知功能、人格特质、评估
- **Mock Supabase responses** and async testing support with pytest-asyncio / 模拟Supabase响应和pytest-asyncio异步测试支持

### ✅ Enhanced Security & Data Integrity / 增强安全性和数据完整性
- **Verified CASCADE DELETE** relationships between `auth.users` and all profile tables / **验证CASCADE DELETE**关系，确保用户删除时相关数据级联删除
- **Comprehensive RLS policies** for data privacy and security / **全面的RLS策略**，保护数据隐私和安全
- **Granular privacy controls** with `is_public` flags and profile visibility settings / **细粒度隐私控制**，支持`is_public`标志和档案可见性设置
- **Proper auth integration** using `auth.uid()` in all security policies / **正确的认证集成**，在所有安全策略中使用`auth.uid()`

## 🏗️ Architecture Overview / 架构概览

### Database Schema (Modular Design) / 数据库架构（模块化设计）
- **Profile Schema** (`profile.*`): User basic information and demographics / 用户基本信息和人口统计
- **Attributes Schema** (`attributes.*`): User interests, hobbies, and activities / 用户兴趣、爱好和活动
- **Ego Schema** (`ego.*`): Personality traits and cognitive functions / 人格特质和认知功能

### API Structure / API结构
- **Profile API** (`/api/v1/profile/*`): User profile management / 用户档案管理
- **Attributes API** (`/api/v1/attributes/*`): User attributes and interests / 用户属性和兴趣
- **Ego API** (`/api/v1/ego/*`): Personality and cognitive function management / 人格和认知功能管理

### Key Features / 主要功能
- **Jung's 8 Cognitive Functions** / 荣格8种认知功能
- **Hierarchical Attribute Categories** / 层级属性分类
- **Multi-framework Personality Support** / 多框架人格支持
- **Comprehensive Privacy Controls** / 全面隐私控制
- **Real-time Supabase Integration** / 实时Supabase集成

## 🧪 Testing / 测试

### Run All Tests / 运行所有测试
```bash
pytest
```

### Run Specific Test Suites / 运行特定测试套件
```bash
# Profile tests
pytest tests/test_profile.py

# Attributes tests
pytest tests/test_attributes.py

# Ego/Personality tests
pytest tests/test_ego.py
```

### Test Coverage / 测试覆盖率
```bash
pytest --cov=src --cov-report=html
```

## 📚 Documentation / 文档

- **[Database Schema Documentation](docs/NEW_ARCHITECTURE.md)** / 数据库架构文档
- **[CASCADE DELETE & RLS Verification](docs/CASCADE_DELETE_RLS_VERIFICATION.md)** / CASCADE DELETE和RLS验证
- **[API Documentation](http://localhost:8000/docs)** (when running) / API文档（运行时访问）

## 安装指南 / Installation Guide

本指南将引导您完成项目的开发和生产环境设置。

### 1. 环境准备

#### a. Python 版本管理器 (推荐)

为确保您使用正确的 Python 版本 (3.13, 根据 `.python-version` 文件指定)，我们建议使用像 `pyenv` 这样的 Python 版本管理器。

- **对于 macOS/Linux (使用 Homebrew):**
  ```bash
  brew install pyenv
  pyenv install 3.13
  ```

安装后，为此项目设置本地 Python 版本：
```bash
pyenv local 3.13
```

#### b. 安装 uv

本项目使用 `uv` 进行包和环境管理。它是 `pip` 和 `venv` 的一个快速、现代的替代品。

- **对于 macOS/Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **对于 Windows:**
  ```powershell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 2. 项目设置

#### a. 创建虚拟环境

使用 `uv` 创建虚拟环境。这将在项目根目录下创建一个 `.venv` 目录。

```bash
uv venv
```

#### b. 激活虚拟环境

- **对于 macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **对于 Windows:**
  ```powershell
  .venv\Scripts\activate
  ```

#### c. 安装依赖

使用 `uv` 安装所有项目依赖项。要安装所有生产和开发依赖，请运行：
```bash
uv pip install -e . pytest
```
这将安装 `pyproject.toml` 中定义的所有主依赖项和 `pytest` 测试框架。

### 3. 运行应用

要运行 FastAPI 开发服务器，请使用 `fastapi dev` 命令。它会监视文件变化并自动重新加载服务。

```bash
fastapi dev main.py
```

应用将在 `http://127.0.0.1:8000` 上可用。

### 4. 运行测试

本项目使用 `pytest` 进行测试。要运行测试套件，请执行：

```bash
pytest
```