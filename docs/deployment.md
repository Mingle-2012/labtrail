# 部署指南

## 本地开发

### 环境要求
- Python 3.12+（推荐：macOS 上通过 Homebrew 安装）
- Node.js 18+
- npm 或 yarn

### 安装步骤

1. **进入项目目录**
```bash
cd labtrail
```

2. **配置 Python 环境**
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

3. **安装前端依赖**
```bash
cd frontend
npm install
cd ..
```

4. **配置环境变量**
```bash
cp .env.example .env
```

5. **加载演示数据**
```bash
PYTHONPATH=backend python scripts/load_demo_data.py
```

6. **启动后端**
```bash
cd backend
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

7. **启动前端**（新终端窗口）
```bash
cd frontend
npm run dev
```

8. **访问应用**
打开 http://localhost:5173

## Docker 部署

### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - SEEKDB_MODE=embedded
      - SEEKDB_PATH=/app/data/seekdb

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:80"
    depends_on:
      - backend
```

### 构建并运行
```bash
docker-compose up -d
```

## Qoder Sites 部署

前端通过 Qoder Sites 作为静态站点部署。后端 API 通过开发服务器或单独托管的端点访问。

### 前端构建
```bash
cd frontend
npm run build
```

构建后的文件位于 `frontend/dist/` 目录，可部署到任何静态托管服务。

## 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `SEEKB_MODE` | seekdb 模式：`embedded` 或 `server` | `embedded` |
| `SEEKB_PATH` | 嵌入式 seekdb 数据路径 | `./data/seekdb` |
| `SEEKB_HOST` | seekdb 服务器地址 | `localhost` |
| `SEEKB_PORT` | seekdb 服务器端口 | `2881` |
| `EMBEDDING_MODEL` | 句子向量化模型 | `sentence-transformers/all-MiniLM-L6-v2` |
| `HOST` | 后端服务器地址 | `0.0.0.0` |
| `PORT` | 后端服务器端口 | `8000` |
| `FRONTEND_URL` | 前端 URL（用于 CORS） | `http://localhost:5173` |
| `OPENAI_API_KEY` | 可选 LLM API 密钥 | （空） |
| `OPENAI_BASE_URL` | 可选 LLM API 基础 URL | `https://api.openai.com/v1` |
| `LLM_MODEL` | 可选 LLM 模型名称 | `gpt-4o-mini` |

## 常见问题排查

### Python 版本问题
- pyseekdb 和 powercontext 需要 Python 3.11+
- 通过 Homebrew 安装 Python 3.12：`brew install python@3.12`

### seekdb 首次初始化较慢
- 向量化模型（all-MiniLM-L6-v2）在首次使用时下载
- 后续运行使用缓存模型（约 86MB）

### 前端代理问题
- Vite 开发服务器将 `/api` 请求代理到 `http://localhost:8000`
- 确保在启动前端之前后端正在运行

### 内存/磁盘使用
- seekdb 嵌入式模式将数据存储在 `backend/data/seekdb/` 目录
- 上传文件存储在 `backend/uploads/` 目录
- 清除这些目录可重置所有数据
