# LabTrail - 大赛提交材料

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | LabTrail - AI 科研知识与实验管理工作台 |
| 参赛赛道 | OceanBase 数据库大赛 - Qoder 赛道 |
| 队伍名称 | 贝利奶娃 |
| Qoder UID | 1366894060914308 |

## 链接

- **Qoder Sites 公开访问地址**：<https://labtrail-ufmfmmmc4qq.qoder.zone>
- **GitHub 代码仓库**：<https://github.com/Mingle-2012/labtrail>
- **在线运行说明**：<https://github.com/Mingle-2012/labtrail/blob/main/docs/deployment.md>
- **验证样例**：<https://github.com/Mingle-2012/labtrail/blob/main/docs/verification.md>
- **Qoder 开发记录**：<https://github.com/Mingle-2012/labtrail/blob/main/docs/qoder-development.md>

> 网站为公网可访问的静态展示站，包含项目介绍、真实运行截图、可交互的数据快照演示和本地体验入口。完整的 seekdb + PowerContext 运行时需要按运行说明在本地或服务器启动（嵌入式 seekdb 与本地 PowerContext Server 无法运行在静态托管环境中）。网站不伪造在线 API。

## 文档清单

- **项目说明**：[README.md](./README.md)
- **运行说明**：[docs/deployment.md](./docs/deployment.md)
- **架构文档**：[docs/architecture.md](./docs/architecture.md)
- **验证样例**：[docs/verification.md](./docs/verification.md)
- **Qoder 开发记录**：[docs/qoder-development.md](./docs/qoder-development.md)
- **使用评估**：[docs/evaluation.md](./docs/evaluation.md)
- **验证证据**：[evidence/README.md](./evidence/README.md)

## 技术使用说明

### seekdb（真实集成，负责知识库与检索）

- **版本**：pyseekdb 1.4.0.post1，嵌入式模式（无需额外数据库服务）
- **实现文件**：`backend/app/seekdb_service.py`
- **用途**：
  - 科研文档分块存储（PDF / Markdown / TXT / CSV）
  - IVF 向量索引（384 维，余弦距离；pyseekdb 内置 all-MiniLM-L6-v2 ONNX 模型本地向量化）
  - 全文索引（关键词检索）
  - 向量 + 全文混合检索，RRF 倒数排名融合
  - 通过 `project_id` 元数据过滤实现项目隔离
- **集合**：`labtrail_documents`
- **验证方式**：`POST /api/documents/search` 返回带来源文件名、页码、RRF 融合分的真实检索结果

### PowerContext（真实集成，负责长期研究记忆）

- **版本**：powercontext 1.4.1，Server 模式
- **启动方式**：`./scripts/start_powercontext.sh`（默认 `http://127.0.0.1:8890`）
- **实现文件**：`backend/app/powercontext_service.py`
- **集成方式**：后端通过 HTTP 调用 PowerContext Server 的真实 API，不使用 seekdb 模拟：
  - `GET /health/ready`：服务健康检查
  - `GET /v1/scopes`、`POST /v1/scopes`：每个项目对应一个 `LabTrail · {project_id}` scope
  - `POST /v1/memory/remember`：写入研究结论 / 决策 / 计划 / 失败方案，`kind` 与记忆类型一一对应
  - `POST /v1/memory/search`：检索研究记忆（`mode: auto`；默认配置下由 jieba 全文检索提供结果）
  - `POST /v1/memory/entries/list`：恢复某个项目的全部有效记忆
  - `POST /v1/atomic-memory/lifecycle`：将记忆标记为 `forgotten` 实现删除
- **验证方式**：`POST /api/memory` 写入后，通过 `GET /api/memory/{project_id}/context` 在“新会话”中恢复；重启 PowerContext Server 后记忆仍然存在（数据目录由 `POWERCONTEXT_HOME` 指定）

### 技术分工

| 能力 | 技术 | 说明 |
| --- | --- | --- |
| 文档分块、向量化、全文索引、混合检索 | seekdb | 证据检索与来源追溯 |
| 实验 CSV 解析、指标汇总、图表、周报数字 | pandas + JSON 数据文件 | 所有数字可追溯到原始 CSV |
| 长期研究记忆、跨会话恢复、记忆检索、遗忘 | PowerContext Server | 每项目独立 scope，真实 HTTP API |
| Web 界面与 API | React 19 + FastAPI | 本地运行 / Docker Compose |

> PowerContext 默认本地配置未接入 embedding provider，因此其向量检索模式不可用；本项目使用 `mode: auto` 让 PowerContext 选择可用的全文检索。若配置了 embedding provider，PowerContext 会自动启用向量检索，后端代码无需修改。这一点在 [docs/architecture.md](./docs/architecture.md) 中有详细说明。

## 运行与验证

### 一键启动（本地）

```bash
# 1. 安装依赖
python3.12 -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 2. 启动 PowerContext Server（终端 1）
./scripts/start_powercontext.sh

# 3. 加载演示数据（终端 2）
PYTHONPATH=backend python scripts/load_demo_data.py

# 4. 启动后端（终端 2）
cd backend && PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000

# 5. 启动前端（终端 3）
cd frontend && npm run dev
```

打开 <http://localhost:5173>。详细步骤、Docker 部署和环境变量见 [docs/deployment.md](./docs/deployment.md)。

### 自动化验证

```bash
# 需先启动 PowerContext Server 与后端
source venv/bin/activate
PYTHONPATH=backend python scripts/verify.py
```

脚本会逐项验证健康检查、seekdb 混合检索、实验数据、PowerContext 写入 / 检索 / 上下文恢复 / 遗忘、周报生成，并将真实输出写入 `evidence/`。本次提交已附运行输出：[evidence/verification.log](./evidence/verification.log)。

### 演示数据

- 8 篇图 ANN 检索研究笔记（HNSW、Vamana、OOD、数据集、评测方法）
- 30 条实验记录，覆盖 HNSW / Vamana 两种方法、4 个数据集、4 类指标
- 6 条研究记忆（结论、决策、计划、失败方案），存储在 PowerContext
- 说明：实验 CSV 为合成的演示数据，界面与文档均已标注；研究笔记为公开论文摘要的整理

## 大赛要求检查清单

### 作品与网站

- [x] 作品基于 Qoder 开发完成，保留开发记录与 Qoder 对话截图（UID：1366894060914308）
- [x] 作品网站已通过 Qoder Sites 发布，公网无需登录即可访问
- [x] 网站包含项目简介、方向、核心功能、真实界面截图、可交互演示、仓库链接、体验入口
- [x] 网站链接均可跳转（GitHub、运行说明、验证指南、Qoder 开发记录）
- [x] 网站演示明确标注为“真实数据快照”，不冒充在线 API

### 技术真实性

- [x] seekdb 执行真实的文档存储、向量索引、全文索引与混合检索
- [x] PowerContext Server 真实运行，研究记忆通过 HTTP API 写入、检索、恢复、遗忘
- [x] 重启 PowerContext Server 后记忆仍可恢复（本地文件持久化）
- [x] 无 mock 替换核心数据库功能
- [x] 所有实验数字可追溯至 `demo-data/experiments.csv`
- [x] 提供可执行的自动化验证脚本与真实运行日志
- [x] 配置示例仅含占位符，无真实 API Key / 密码 / 凭据

### 提交材料

- [x] 完整代码仓库（公开）
- [x] 运行说明（环境、依赖版本、seekdb / PowerContext 部署与集成、安装与启动步骤）
- [x] 验证样例（初始数据、输入、步骤、预期结果、实际输出）
- [x] Qoder 开发记录（对话截图 + UID）
- [x] 使用评估（真实测量数据 + 未完成项如实标注）
- [x] 开源代码与数据来源标注

## 已知限制（如实说明）

1. Qoder Sites 为静态托管，线上站点不提供 `/api/*`。真实 API 需本地启动后端；网站通过真实数据快照演示检索、记忆与实验分析，并明确标注。
2. PowerContext 的默认本地配置未接入 embedding provider，记忆检索使用其全文检索（jieba）；向量检索模式需配置 provider 后启用。
3. seekdb 嵌入式模式不支持命名空间（需 LakeBase 云端）；项目隔离通过元数据过滤实现。
4. PDF 解析仅提取文本，不包含图片 / 表格理解。
5. LLM 增强周报为可选项，需要用户自备 API Key；默认模板模式无需密钥。
6. 实验 CSV 为合成的演示数据；未进行真实用户测试，评估文档中已标注。
7. 演示笔记为英文论文摘要整理，建议使用英文查询获得最佳向量检索效果。

## 提交状态

- 代码：已完成并本地验证
- 文档：已完成
- 演示数据：已加载并验证
- 自动化验证：已执行，日志与截图见 `evidence/`
- Qoder Sites：已发布并更新（2026-10-29，含最新验证数据与仓库链接）
- GitHub：已推送公开仓库
