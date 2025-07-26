# Profile Matcher 后端

这是一个使用 FastAPI 构建的 Profile Matcher 应用的后端服务。

## 安装指南

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
