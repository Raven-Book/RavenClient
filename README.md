# Raven Client

> LLM 客户端

## 安装与运行

### 后端

> 本项目使用 `uv` 作为包管理器 

```bash
uv python install 3.11
uv venv --python 3.11
uv pip install .
uv run fastapi dev
```

### 前端

```bash
cd frontend
pnpm install
pnpm dev
```