# Qoder 开发记录

本文档记录使用 Qoder 开发 LabTrail 的过程、遇到的关键问题与解决方式，用于核对 Qoder 的使用情况。

- **Qoder 账号 UID**：1366894060914308
- **代码仓库**：<https://github.com/Mingle-2012/labtrail>
- **在线展示站**：<https://labtrail-ufmfmmmc4qq.qoder.zone>

## 开发时间线

### 第一阶段：需求分析与架构设计

**Qoder 操作**：
- 分析大赛任务书中的竞赛要求
- 研究 seekdb 官方文档与 pyseekdb SDK
- 研究 PowerContext 1.4.1 的 Server 模式与 Memory API
- 设计 React → FastAPI → seekdb / PowerContext 的分层架构
- 创建项目目录结构

**关键决策**：
- seekdb 使用嵌入式模式，零配置本地运行
- 使用 pyseekdb 内置的 all-MiniLM-L6-v2（ONNX，384 维）本地向量化，无需外部 API
- 向量索引使用 IVF（嵌入式模式不支持命名空间与 HNSW 组合）
- 项目隔离使用 metadata 过滤，而非 namespace
- 研究记忆使用独立运行的 PowerContext Server，不用 seekdb 模拟
- 项目与实验元数据使用 JSON 文件存储

### 第二阶段：后端开发

**Qoder 操作**：
- 创建带生命周期管理的 FastAPI 应用
- 实现 seekdb 服务：向量检索、全文检索、混合检索
- 接入 PowerContext Server：scope 管理、记忆写入、检索、上下文恢复、遗忘
- 实现文档摄入：PDF、Markdown、CSV、TXT
- 实现实验数据解析与分析
- 实现模板模式和可选 LLM 模式的周报生成器
- 创建所有 API 路由：项目、文档、搜索、实验、记忆、报告

**关键文件**：
- `backend/app/main.py` — FastAPI 应用入口
- `backend/app/seekdb_service.py` — seekdb 存储与三种检索
- `backend/app/powercontext_service.py` — PowerContext HTTP 集成
- `backend/app/embedding_service.py` — 本地向量化
- `backend/app/ingestion/parser.py` — 文档解析
- `backend/app/experiments/service.py` — 实验分析
- `backend/app/reports/generator.py` — 报告生成
- `backend/app/api/*.py` — API 路由

**遇到的问题与解决**：

1. **Python 3.9 过旧**，不支持 pyseekdb / powercontext → 通过 Homebrew 安装 Python 3.12 并创建 venv。
2. **`use_namespace=True` 需要 LakeBase 云端** → 嵌入式模式改用 metadata 过滤实现项目隔离。
3. **`Client` 是函数而非类**，直接用作类型注解会报错 → 使用 `from __future__ import annotations`。
4. **HNSW 索引与命名空间集合不兼容** → 改用 IVF 索引（384 维，余弦距离）。
5. **PowerContext 1.4.1 改为 Server 架构**，不再是可嵌入的库 → 使用 `powercontext server run --role all` 启动本地服务，后端通过 HTTP 调用 `/v1/scopes`、`/v1/memory/remember`、`/v1/memory/search`、`/v1/memory/entries/list`、`/v1/atomic-memory/lifecycle`。
6. **PowerContext 默认本地配置没有 embedding provider** → 记忆检索使用 `mode: "auto"`，由 PowerContext 选择可用的全文检索（jieba）；后端代码不写死检索方式。

### 第三阶段：前端开发

**Qoder 操作**：
- 创建 React + TypeScript + Vite 项目
- 安装 Tailwind CSS、Recharts、Lucide React、React Router
- 构建带侧边栏导航的 Layout 组件
- 构建 7 个页面：仪表盘、文档库、检索、实验分析、研究记忆、周报、项目管理
- 检索页支持混合 / 向量 / 全文三种模式，并展示不同口径的分数
- 研究记忆页支持保存、搜索、恢复上下文

**关键文件**：
- `frontend/src/App.tsx` — 主应用路由
- `frontend/src/components/Layout.tsx` — 导航布局
- `frontend/src/pages/*.tsx` — 7 个页面组件
- `frontend/src/index.css` — 全局样式

**解决的问题**：
- npm install 在错误目录运行 → 使用显式 dir_path 参数
- TypeScript 未使用导入错误 → 移除未使用的导入
- 搜索 API 混用 Form/Body 参数 → 重构为仅使用 Body
- 向量分数把余弦距离当相似度显示 → 后端改为返回 `1 - distance`，前端标注“余弦相似度”

### 第四阶段：演示数据与测试

**Qoder 操作**：
- 创建关于图 ANN 检索的研究笔记（8 篇文档）
- 创建包含 30 条记录的合成实验 CSV（HNSW / Vamana × 4 个数据集）
- 创建演示数据加载脚本，写入 seekdb 与 PowerContext
- 通过 curl 与 `scripts/verify.py` 测试全部 API
- 验证三种检索模式返回不同结果与分数
- 验证记忆写入、检索、上下文恢复、遗忘
- 验证实验统计与周报生成的数字可追溯

**测试结果**：
- seekdb：连接成功，8 个分块已建立向量与全文索引 ✓
- 混合 / 向量 / 全文：三条查询路径均生效，top-1 分别为 `ood_analysis_notes.md`、`query_aware_construction.md`、`ood_analysis_notes.md` ✓
- PowerContext：写入、检索、上下文恢复、遗忘全部通过 ✓
- 实验：30 条记录，Vamana recall@10 均值 0.9015 ✓
- 报告：4439 字符，包含实验与研究记忆 ✓
- 自动化验证：12/12 通过，输出见 `evidence/verification.log` ✓

### 第五阶段：文档与部署

**Qoder 操作**：
- 编写 README、架构文档、部署指南、验证指南、评估文档
- 创建 SUBMISSION.md
- 编写 Dockerfile、docker-compose.yml、nginx.conf、`.env.example`
- 构建静态展示站（Qoder Sites）与演示数据导出脚本

**解决的问题**：
- docker-compose 引用了不存在的 Dockerfile → 补齐 `backend/Dockerfile`、`frontend/Dockerfile`，`docker compose config` 与 `docker compose build` 均通过
- 静态站点无法运行后端 → 增加 `scripts/export_web_demo.py`，从本地真实实例导出检索、记忆、实验、报告快照，网站明确标注“静态快照，不伪造在线 API”

### 第六阶段：提交前自审与修复

**Qoder 操作**：
- 对照竞赛要求逐项审查提交材料
- 修正 SUBMISSION.md 中的仓库地址
- 补齐 Docker 部署文件与 `.env.example`
- 排查并修复“全文检索实际走了向量检索”的隐藏缺陷
- 将展示站从文本示例改为可交互的真实数据快照
- 补齐证据截图与验证日志

**关键缺陷：全文 / 混合检索曾名不副实**

pyseekdb 的 `query()` 会忽略 `search_mode="fulltext"` 参数，导致“全文检索”实际执行的是向量检索；旧实现的“混合检索”则是把向量结果做了两次手动 RRF 融合，并未真正使用全文索引。修复方式：

```python
# 全文：只走 FULLTEXT 索引
collection.hybrid_search(
    query={"where_document": {"$contains": query},
           "where": {"project_id": project_id},
           "n_results": n_results},
    n_results=n_results,
    include=["documents", "metadatas", "distances"],
)

# 混合：向量 KNN + FULLTEXT，由 seekdb 原生 RRF 融合
collection.hybrid_search(
    query={"where_document": {"$contains": query}, "where": where, "n_results": n_results},
    knn={"query_texts": [query], "where": where, "n_results": n_results},
    rank={"rrf": {"rank_window_size": 60, "rank_constant": 60}},
    n_results=n_results,
    include=["documents", "metadatas", "distances"],
)
```

修复后三种模式的结果文件、顺序与分数均不同，`scripts/verify.py` 增加了针对性断言防止回归：

- 向量分数必须在 `[0, 1]` 区间（余弦相似度）
- 全文检索 top-1 必须是 `ood_analysis_notes.md`

## 技术验证

### seekdb 集成

- **版本**：pyseekdb 1.4.0.post1
- **模式**：嵌入式（无需服务器）
- **向量索引**：IVF，余弦距离，384 维
- **全文索引**：FULLTEXT 已启用
- **集合**：`labtrail_documents`
- **检索模式**：向量、全文、混合（seekdb 原生 RRF）
- **状态**：✓ 正常运行

### PowerContext 集成

- **版本**：powercontext 1.4.1，Server 模式（`--role all`）
- **启动方式**：`./scripts/start_powercontext.sh`，默认 `http://127.0.0.1:8890`
- **实现文件**：`backend/app/powercontext_service.py`
- **集成方式**：真实 HTTP API 调用，不使用 seekdb 模拟
- **项目隔离**：每个项目对应一个 `LabTrail · {project_id}` scope
- **功能**：记忆写入、检索、上下文恢复、遗忘（生命周期 `forgotten`）
- **持久化**：`POWERCONTEXT_HOME` 指定目录（本地为 `backend/data/powercontext`），重启后可恢复
- **状态**：✓ 正常运行

### 向量化模型

- **模型**：all-MiniLM-L6-v2（pyseekdb 内置 ONNX Runtime，384 维）
- **维度**：384
- **运行时**：本地 CPU，无需 API 密钥
- **状态**：✓ 正常运行

## 代码统计

- 后端 Python 文件：约 15 个
- 前端 TypeScript/TSX 文件：约 10 个
- 展示站：单页 HTML + 两份真实数据快照
- 演示数据文件：3 个
- 文档文件：6 个

## Qoder 开发截图

以下为 Qoder 开发过程中的对话截图，展示关键开发环节：

![Qoder 开发对话截图](./qoder-screenshot.png)

**Qoder 账号 UID**：1366894060914308

## 总结

LabTrail 使用 Qoder 完成从架构设计、后端、前端、测试到部署的完整开发流程。项目与 seekdb（文档存储 + 向量/全文/混合检索）和 PowerContext Server（长期研究记忆）均为真实集成，关键路径有自动化验证脚本与可复查的运行日志。
