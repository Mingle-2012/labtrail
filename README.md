# LabTrail

**AI 科研知识与实验管理工作台**

> 从碎片化科研到连接式知识管理。

LabTrail 把科研过程中的三类信息——**文献笔记、实验结果、研究记忆**——放进同一个工作台：用 **seekdb** 做文档知识库与混合检索，用 **PowerContext Server** 做可跨会话恢复的长期研究记忆，用真实实验数据生成可追溯的周报。项目使用 Qoder 开发。

- **在线展示站**：<https://labtrail-ufmfmmmc4qq.qoder.zone>
- **代码仓库**：<https://github.com/Mingle-2012/labtrail>
- **运行说明**：[docs/deployment.md](docs/deployment.md)
- **验证样例**：[docs/verification.md](docs/verification.md)
- **Qoder 开发记录**：[docs/qoder-development.md](docs/qoder-development.md)

> 在线站点为静态展示：包含项目介绍、真实运行截图与基于真实检索结果的交互演示。seekdb 嵌入式数据库与本地 PowerContext Server 无法运行在静态托管环境，完整 API 请按运行说明在本地启动。

## 问题与思路

科研工作常见三个断点：

1. **资料碎片化**：论文、笔记散落在不同目录，找一个结论要翻很多文件。
2. **实验对比靠手工**：CSV 指标需要手动汇总、画图，难以快速回答“哪个方法更好”。
3. **上下文丢失**：上周做出的决策、失败的尝试、下一步计划，在新会话里很难恢复。

LabTrail 的对应方案：

- **seekdb 混合检索**：向量语义 + 全文关键词 + RRF 融合，结果保留文件名、页码与原文出处。
- **实验分析**：标准化 CSV 导入，按方法 / 数据集聚合 Recall、QPS、构建时间、内存，并生成周报。
- **PowerContext 长期记忆**：把结论、决策、计划、失败方案写入项目独立的 scope，随时恢复上下文。

## 核心功能

### 1. 研究项目管理
- 多项目隔离，独立的知识库与记忆空间
- 项目目标、研究方向与活动记录

### 2. 文档知识库（seekdb）
- 导入 PDF、Markdown、TXT、CSV
- 自动分块、向量化、建立全文索引
- 支持按项目检索，结果带来源文件名 / 页码 / 原始引用

### 3. 智能证据检索（seekdb）
- 三种模式：向量检索、全文检索、混合检索
- 混合模式使用倒数排名融合（RRF）组合两路结果
- 显示 RRF 融合分、来源文档与原文

### 4. 实验数据分析
- 标准化 CSV 导入（方法、数据集、指标、参数）
- 指标：`recall@10`、`qps`、`index_build_time`、`peak_memory`
- 交互式图表与数据表，按方法 / 数据集过滤
- 所有数字可追溯到原始 CSV

### 5. 长期研究记忆（PowerContext）
- 真实调用 PowerContext Server HTTP API，不使用 seekdb 模拟
- 每个项目一个 `LabTrail · {project_id}` scope
- 支持结论、决策、计划、失败方案等类型与标签
- 记忆检索、上下文恢复、遗忘（`forgotten` 生命周期）
- 数据持久化在 `POWERCONTEXT_HOME` 指定目录，重启服务后仍可恢复

### 6. 科研周报生成器
- 从文档、实验、研究记忆自动汇总
- 模板模式无需 LLM API Key；可选 LLM 增强
- 导出 Markdown，实验数字可回查 CSV

### 7. 仪表盘
- 文档数、实验记录数、研究记忆数、数据块数
- 最近活动、快速操作、方法与数据集概览

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | React 19、TypeScript、Vite 8、Tailwind CSS 4、Recharts、Lucide |
| 后端 | Python 3.12、FastAPI、uvicorn、pandas |
| 文档检索 | pyseekdb 1.4.0.post1（嵌入式，IVF 向量索引 + 全文索引 + RRF） |
| 向量化 | pyseekdb 内置 `all-MiniLM-L6-v2`（ONNX，384 维，本地运行） |
| 研究记忆 | PowerContext 1.4.1 Server（HTTP API、scope、生命周期） |
| 部署 | 本地脚本 / Docker Compose / Qoder Sites（静态展示站） |

## 快速开始

### 环境要求
- Python 3.11+（推荐 3.12）
- Node.js 20.19+ 或 22.12+
- npm
- 首次运行需联网下载 embedding 模型（约 90 MB）

### 安装

```bash
git clone https://github.com/Mingle-2012/labtrail.git
cd labtrail

python3.12 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

cd frontend && npm install && cd ..
cp .env.example .env
```

### 启动（三个终端）

```bash
# 终端 1：PowerContext Server
./scripts/start_powercontext.sh

# 终端 2：加载演示数据（保持 PowerContext 运行）
source venv/bin/activate
PYTHONPATH=backend python scripts/load_demo_data.py

# 终端 2：启动后端
cd backend
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000

# 终端 3：启动前端
cd frontend
npm run dev
```

打开 <http://localhost:5173>。健康检查：

```bash
curl http://localhost:8000/api/health
# {"status":"ok","services":{"seekdb":"connected","powercontext":"ready"}}
```

### Docker Compose

```bash
docker compose up --build
```

- 前端：<http://localhost:5173>
- 后端：<http://localhost:8000>
- PowerContext：仅容器内网 `http://powercontext:8890`，不对外暴露
- 首次启动会自动加载演示数据（`AUTO_LOAD_DEMO=true`）
- 向量模型已烘焙进后端镜像，容器以离线模式运行，启动时不再下载模型

详细步骤与环境变量见 [docs/deployment.md](docs/deployment.md)。

## 演示项目

内置项目：**Graph-based Approximate Nearest Neighbor Search**

| 数据 | 数量 | 说明 |
| --- | --- | --- |
| 研究笔记 | 8 篇 | HNSW、Vamana、OOD、查询感知构建、评测指标、数据集 |
| 文档分块 | 8 个 | 全部写入 seekdb，含向量与全文索引 |
| 实验记录 | 30 条 | HNSW / Vamana × 4 个数据集 × 4 类指标 |
| 研究记忆 | 6 条 | 结论、决策、计划、失败方案，存储在 PowerContext |

> 实验 CSV 为合成的演示数据，已在界面标注；研究笔记为公开论文摘要的整理。

### 三个验证场景

**A. 研究知识检索（seekdb）**

检索 `Why does OOD query distribution degrade graph index performance?`，混合检索返回相关笔记，结果包含来源文件名、页码与 RRF 融合分。

**B. 研究记忆恢复（PowerContext）**

在“研究记忆”页保存一条决策，点击“恢复上下文”，即可看到包含新决策的完整上下文；重启 PowerContext Server 后再次恢复，记忆仍然存在。

**C. 实验分析与周报**

“实验分析”页查看 HNSW / Vamana 在 SIFT / GloVe 上的指标对比；“周报”页生成包含实验汇总与研究记忆的 Markdown 报告。

完整命令、预期输出与实际结果见 [docs/verification.md](docs/verification.md)。

## 架构

```
┌────────────────────────────────────────────────────────────┐
│                    前端 React SPA (Vite)                    │
│  仪表盘 │ 知识库 │ 检索 │ 实验分析 │ 研究记忆 │ 周报 │ 项目  │
└───────────────────────────┬────────────────────────────────┘
                            │ REST /api
┌───────────────────────────┴────────────────────────────────┐
│                     后端 FastAPI                            │
│  文档摄取 │ 混合检索 │ 实验分析 │ 记忆 API │ 周报生成        │
└───────────┬───────────────────────────────┬────────────────┘
            │ pyseekdb SDK                  │ HTTP
┌───────────┴───────────────┐   ┌───────────┴────────────────┐
│ seekdb（嵌入式）           │   │ PowerContext Server         │
│ 文档分块 + IVF + 全文索引  │   │ Scope / Memory / Lifecycle  │
│ 项目隔离：metadata 过滤    │   │ 持久化于 POWERCONTEXT_HOME  │
└───────────────────────────┘   └────────────────────────────┘
```

详细设计见 [docs/architecture.md](docs/architecture.md)。

## 项目结构

```
labtrail/
├── backend/
│   ├── app/
│   │   ├── api/                 # projects / documents / experiments / memory / reports
│   │   ├── ingestion/           # PDF、Markdown、TXT、CSV 解析
│   │   ├── experiments/         # 实验 CSV 解析与聚合
│   │   ├── reports/             # 周报生成
│   │   ├── seekdb_service.py    # seekdb 存储与混合检索
│   │   ├── powercontext_service.py # PowerContext HTTP 集成
│   │   ├── embedding_service.py # 本地向量化
│   │   └── main.py              # FastAPI 入口与健康检查
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/pages/               # 7 个页面
│   ├── Dockerfile
│   └── nginx.conf
├── demo-data/                   # 研究笔记与实验 CSV
├── scripts/
│   ├── load_demo_data.py        # 演示数据加载（幂等）
│   ├── verify.py                # 端到端验证
│   └── start_powercontext.sh    # 启动本地 PowerContext Server
├── evidence/                    # 真实验证日志与截图
├── web/                         # Qoder Sites 静态展示站
├── docs/                        # 架构、部署、验证、Qoder 记录、评估
├── docker-compose.yml
└── .env.example
```

## API 一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/health` | 后端、seekdb、PowerContext 健康状态 |
| GET | `/api/projects` | 项目列表 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects/{id}/dashboard` | 仪表盘统计 |
| POST | `/api/documents/upload` | 上传并索引文档 |
| GET | `/api/documents/{project_id}` | 文档列表 |
| POST | `/api/documents/search?project_id=...` | 混合 / 向量 / 全文检索 |
| DELETE | `/api/documents/{project_id}/{doc_id}` | 删除文档 |
| POST | `/api/experiments/upload` | 上传实验 CSV |
| GET | `/api/experiments/{project_id}` | 实验分析结果 |
| GET | `/api/experiments/{project_id}/recall-qps` | Recall-QPS 数据 |
| POST | `/api/memory` | 写入研究记忆（PowerContext） |
| GET | `/api/memory/{project_id}` | 记忆列表 |
| POST | `/api/memory/search` | 记忆检索 |
| GET | `/api/memory/{project_id}/context` | 恢复研究上下文 |
| DELETE | `/api/memory/{project_id}/{memory_id}` | 遗忘记忆 |
| POST | `/api/reports/weekly` | 生成科研周报 |

## 验证

需先启动 PowerContext Server 与后端：

```bash
source venv/bin/activate
PYTHONPATH=backend python scripts/verify.py
```

脚本验证 8 项内容并写入 `evidence/verification.log`：

1. `/api/health`：seekdb 连接 + PowerContext ready
2. seekdb 混合检索：结果数量、来源文件
3. seekdb 向量检索与全文检索
4. 实验数据：30 条记录、2 种方法、4 个数据集
5. PowerContext 写入记忆
6. PowerContext 检索记忆
7. PowerContext 上下文恢复
8. 周报生成（含记忆内容）

提交包中的实际运行日志：[evidence/verification.log](evidence/verification.log)。界面截图：[evidence/screenshots/](evidence/screenshots/)。

## 已知限制

- Qoder Sites 为静态托管，线上站点不提供 `/api/*`；真实运行时需本地启动或 Docker 部署。
- PowerContext 默认本地配置未接入 embedding provider，记忆检索使用全文检索（jieba）；配置 provider 后会自动启用向量检索。
- seekdb 嵌入式模式不支持命名空间，项目隔离使用元数据过滤。
- PDF 只提取文本，不解析图片与表格。
- LLM 增强周报需要用户自备 API Key，默认模板模式无需密钥。
- 演示实验数据为合成数据；未进行真实用户测试。

## 安全

- `.env` 不提交，`.env.example` 只含占位符
- 演示数据不含任何真实凭据
- 文件上传限制大小并校验扩展名
- PowerContext 仅在本地 / Docker 内网监听，不暴露公网

## 开源与致谢

- [OceanBase seekdb](https://github.com/oceanbase/seekdb)：AI 原生混合搜索数据库
- [OceanBase PowerContext](https://github.com/oceanbase/powercontext)：上下文与记忆管理框架
- [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)：Apache-2.0 向量模型，由 pyseekdb 内置 ONNX 运行时加载
- [Qoder](https://qoder.com)：开发平台
- 演示笔记内容整理自以下公开论文摘要，详见 `demo-data/research_notes.md`：
  - Malkov & Yashunin, *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs*, IEEE TPAMI 2018（[arXiv:1603.09320](https://arxiv.org/abs/1603.09320)）
  - Subramanya et al., *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node*, NeurIPS 2019
- 数据集名称（SIFT、GLOVE）引用自公开 ANN 基准；实验 CSV 为合成数据，未直接复用第三方数据文件

## 许可证

本项目为 OceanBase 数据库大赛 Qoder 赛道参赛作品，仅用于比赛评审与学习交流。
