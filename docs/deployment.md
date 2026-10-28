# 运行说明

本文档描述从零启动 LabTrail 的完整步骤，包括 seekdb、PowerContext Server、后端与前端。

## 1. 环境要求

| 组件 | 版本 | 说明 |
| --- | --- | --- |
| Python | 3.11+（推荐 3.12） | pyseekdb 与 PowerContext 均要求 |
| Node.js | 20.19+ 或 22.12+ | Vite 8 要求 |
| npm | 10+ | 随 Node.js 安装 |
| 内存 | 4 GB+ | embedding 模型与前后端 |
| 网络 | 首次运行需联网 | pyseekdb 自动下载 all-MiniLM-L6-v2 ONNX 模型（约 90 MB，缓存于 `~/.cache/pyseekdb`） |
| Docker | 可选 | 用于 Compose 部署 |

已验证环境：macOS 15（arm64）、Python 3.12.16、Node 24.18.0、pyseekdb 1.4.0.post1、powercontext 1.4.1。

## 2. 获取代码

```bash
git clone https://github.com/Mingle-2012/labtrail.git
cd labtrail
```

## 3. 安装依赖

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

cd frontend
npm install
cd ..
```

> `requirements.txt` 中的 `powercontext[server,cli]>=1.4.1,<2` 会安装 PowerContext Server、其 CLI 入口及依赖。
> 如果此前安装过不带 `[server]` 的版本，请重新执行上面的 pip 命令。

## 4. 配置环境变量

```bash
cp .env.example .env
```

默认配置即可本地运行：

```dotenv
SEEKDB_MODE=embedded
POWERCONTEXT_URL=http://127.0.0.1:8890
POWERCONTEXT_HOME=./backend/data/powercontext
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:5173
```

`.env.example` 只包含占位符，不包含任何真实密钥。可选项：

- `SEEKDB_MODE=server` + `SEEKDB_HOST` / `SEEKDB_PORT`：连接远程 seekdb
- `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `LLM_MODEL`：启用周报 LLM 增强
- `POWERCONTEXT_URL`：PowerContext Server 地址（默认本机 8890）

## 5. 启动 PowerContext Server（终端 1）

```bash
./scripts/start_powercontext.sh
```

脚本等价于：

```bash
export POWERCONTEXT_HOME="${POWERCONTEXT_HOME:-$PWD/backend/data/powercontext}"
mkdir -p "$POWERCONTEXT_HOME"
powercontext server run --host 127.0.0.1 --port 8890 --no-env-file --role all
```

- `--role all` 是 SQLite / 嵌入式 seekdb 后端的必需参数；写成 `--role api` 会报
  `runtime.artifact_processing_role must be 'all' for SQLite and embedded seekdb`。
- `POWERCONTEXT_HOME` 决定数据目录；不要使用 `POWERCONTEXT_DATA_DIR`，后者不生效。
- 健康检查：

```bash
curl http://127.0.0.1:8890/health/ready
# {"status":"ready", ...}
```

首次启动会初始化 SQLite 与全文索引，通常几秒内完成。

## 6. 加载演示数据（终端 2）

```bash
source venv/bin/activate
PYTHONPATH=backend python scripts/load_demo_data.py
```

脚本会：

1. 检查 PowerContext `/health/ready`，未启动时给出提示并退出；
2. 创建（或复用）演示项目 `demo_project`；
3. 将 8 篇研究笔记写入 seekdb（含向量化、全文索引）；
4. 导入 30 条实验记录；
5. 将 6 条研究记忆写入 PowerContext。

脚本是幂等的：重复执行不会重复插入文档 / 实验 / 记忆。

预期输出：

```
Loading demo data for LabTrail...
  Created project: Graph-based Approximate Nearest Neighbor Search
  Loading research notes into seekdb...
  Loaded 8 research notes
  Loading experiment data...
  Loaded 30 experiment records
  Saving research memories to PowerContext...
  Saved 6 research memories
Demo data loading complete!
```

## 7. 启动后端（终端 2）

```bash
cd backend
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/api/health
# {"status":"ok","services":{"seekdb":"connected","powercontext":"ready"}}
```

如果 PowerContext 未启动，健康检查会返回 `"status":"degraded"`，文档检索仍可用，但记忆功能会报错。

## 8. 启动前端（终端 3）

```bash
cd frontend
npm run dev
```

打开 <http://localhost:5173>。

Vite 已配置 `/api` 代理到 `http://localhost:8000`（见 `frontend/vite.config.ts`）。

## 9. Docker Compose 部署

### 9.1 文件

```
docker-compose.yml
backend/Dockerfile
frontend/Dockerfile
frontend/nginx.conf
.dockerignore
```

### 9.2 启动

```bash
docker compose up --build
```

服务：

| 服务 | 端口 | 说明 |
| --- | --- | --- |
| `frontend` | 宿主 5173 → 容器 80 | nginx 托管构建产物，并将 `/api` 代理到后端 |
| `backend` | 宿主 8000 | FastAPI，启动时自动加载演示数据 |
| `powercontext` | 仅内网 8890 | PowerContext Server，不暴露到宿主机 |

首次启动会：

1. 构建后端镜像（安装 Python 依赖与 PowerContext Server，并把 pyseekdb 的 `all-MiniLM-L6-v2` ONNX 向量模型预先烘焙进镜像）；
2. 构建前端镜像（Node 构建 + nginx）；
3. 启动 PowerContext，等待健康检查；
4. 后端等待 PowerContext ready 后加载演示数据并启动；
5. 前端等待后端健康后启动。

后端容器直接使用镜像内烘焙的 ONNX 向量模型，**运行时不访问 Hugging Face**。只有构建镜像时需要联网下载依赖与模型；模型固定为 pyseekdb 内置的 `all-MiniLM-L6-v2`（384 维）。

访问 <http://localhost:5173>。健康检查：

```bash
curl http://localhost:8000/api/health
```

### 9.3 数据卷

- `labtrail-data`：`/app/backend/data`（seekdb 数据、JSON 记录、PowerContext 数据）
- `powercontext-data`：`/data/powercontext`（PowerContext 数据目录）

重置全部数据：

```bash
docker compose down -v
docker compose up --build
```

### 9.4 不自动加载演示数据

在 `docker-compose.yml` 中将 `AUTO_LOAD_DEMO` 设为 `false`，然后：

```bash
docker compose exec backend python scripts/load_demo_data.py
```

## 10. Qoder Sites 展示站

`web/` 是静态展示站，部署在 Qoder Sites：

<https://labtrail-ufmfmmmc4qq.qoder.zone>

它是**静态站点**，不包含 `/api` 后端。页面中的“在线演示”使用本地 seekdb 真实检索生成的快照数据，并已明确标注；完整系统请按本文档在本地或 Docker 中启动。

更新网站：

```bash
# 修改 web/index.html 与 web/assets/ 后，通过 Qoder Sites 重新发布
```

## 11. 环境变量参考

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `SEEKDB_MODE` | `embedded` | `embedded` 或 `server` |
| `SEEKDB_PATH` | `<repo>/backend/data/seekdb` | 嵌入式数据目录 |
| `SEEKDB_HOST` | `localhost` | server 模式地址 |
| `SEEKDB_PORT` | `2881` | server 模式端口 |
| `POWERCONTEXT_URL` | `http://127.0.0.1:8890` | PowerContext Server 地址 |
| `POWERCONTEXT_HOME` | `<repo>/backend/data/powercontext` | PowerContext 数据目录（启动脚本使用） |
| `HOST` | `0.0.0.0` | 后端监听地址 |
| `PORT` | `8000` | 后端端口 |
| `FRONTEND_URL` | `http://localhost:5173` | CORS 允许的前端地址 |
| `OPENAI_API_KEY` | 空 | 可选，周报 LLM 增强 |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | 可选 |
| `LLM_MODEL` | `gpt-4o-mini` | 可选 |

## 12. 常见问题

### PowerContext 启动失败：role 必须为 all

```
runtime.artifact_processing_role must be 'all' for SQLite and embedded seekdb
```

使用 `--role all`，或直接运行 `./scripts/start_powercontext.sh`。

### 记忆数据写到了用户目录

早期版本未设置 `POWERCONTEXT_HOME`，PowerContext 会写到
`~/Library/Application Support/powercontext`（macOS）或 `~/.local/share/powercontext`（Linux）。
本项目启动脚本已固定到 `backend/data/powercontext`。

### 首次检索很慢

首次调用会下载并加载 all-MiniLM-L6-v2（约 90 MB）。后续使用缓存。

### 端口被占用

```bash
lsof -i :8000
lsof -i :8890
lsof -i :5173
```

### 重置本地数据

```bash
rm -rf backend/data/seekdb backend/data/powercontext
rm -f backend/data/documents.json backend/data/experiments.json backend/data/projects.json
PYTHONPATH=backend python scripts/load_demo_data.py
```

### 前端能打开但 API 404

- 确认后端在 8000 端口运行；
- 通过 `npm run dev` 访问 5173，而不是直接打开 `index.html`；
- Docker 部署时确认 nginx 的 `/api` 代理指向 `backend:8000`。
