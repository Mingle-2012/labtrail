# 架构文档

## 总览

LabTrail 是前后端分离的单用户科研工作台：

```
React SPA ── HTTP /api ── FastAPI ── pyseekdb（文档 + 检索）
                                   ├─ PowerContext Server（长期记忆，HTTP）
                                   ├─ pandas（实验 CSV）
                                   └─ JSON 文件（项目 / 文档元数据 / 实验记录）
```

- **前端**：React 19 + TypeScript + Vite，客户端路由，7 个功能页面。
- **后端**：FastAPI，负责文档摄取、检索、实验分析、记忆代理、周报生成。
- **seekdb**：嵌入式模式，存储文档分块与索引，执行混合检索。
- **PowerContext**：独立 Server 进程，存储研究记忆；后端只通过 HTTP API 访问。
- **JSON 文件**：项目元数据、文档清单、实验记录，便于备份与溯源。

## 为什么这样分工

| 数据 | 存储 | 原因 |
| --- | --- | --- |
| 文档分块 | seekdb | 需要向量 / 全文索引与混合检索 |
| 项目、文档清单、实验记录 | JSON 文件 | 结构化、小规模、可直接检查和备份；实验数字可追溯到 CSV |
| 研究记忆 | PowerContext | 需要 scope 隔离、记忆类型、生命周期与跨会话恢复；使用其原生能力而不是自建表 |

本项目的目标是让两个 OceanBase 技术各自做擅长的事，而不是用一个数据库模拟另一个。

## seekdb 集成

### 嵌入与索引

- 模式：`embedded`，数据目录 `SEEKDB_PATH`（默认 `backend/data/seekdb`）
- 向量模型：pyseekdb 内置 `all-MiniLM-L6-v2`（ONNX Runtime），384 维，本地 CPU 推理
- 向量索引：IVF，余弦距离
- 全文索引：`FulltextIndexConfig`
- 集合：`labtrail_documents`
- 项目隔离：所有分块写入 `metadata.project_id`，查询时过滤

### 文档数据模型

```json
{
  "id": "demo_doc_000_ab12cd34",
  "text": "HNSW (Hierarchical Navigable Small World) graphs ...",
  "metadata": {
    "project_id": "demo_project",
    "doc_id": "demo_doc_000",
    "file_name": "hnsw_paper_notes.md",
    "file_type": "markdown",
    "page": 1,
    "chunk_index": 0,
    "source": "Malkov & Yashunin, 2018 ..."
  }
}
```

### 混合检索管线

1. 用户提交查询，后端用 all-MiniLM-L6-v2 编码为 384 维向量。
2. **向量检索**：seekdb IVF 索引返回余弦相似度 Top-K。
3. **全文检索**：seekdb 全文索引返回关键词匹配 Top-K。
4. **RRF 融合**：`score = Σ 1 / (k + rank)`，`k = 60`，按融合分排序。
5. 结果按 `project_id` 过滤，返回 `text`、`metadata`、`score`、`fusion`。

**为什么用 RRF**：向量与全文的分数尺度不同，直接加权需要归一化与调参；RRF 只依赖排名，稳定且无需训练。代价是融合分本身不可解释为概率，前端因此显示“RRF 融合分”而不是“相关度百分比”。

### 检索 API

`POST /api/documents/search?project_id={id}`

```json
{"query": "...", "mode": "hybrid|vector|fulltext", "n_results": 10}
```

## PowerContext 集成

### 进程与数据目录

- PowerContext 1.4.1，Server 模式，默认监听 `127.0.0.1:8890`
- 由 `scripts/start_powercontext.sh` 启动：

```bash
powercontext server run --host 127.0.0.1 --port 8890 --no-env-file --role all
```

- `--role all` 是 SQLite / 嵌入式 seekdb 后端的必需配置，否则启动时报
  `runtime.artifact_processing_role must be 'all'`。
- 数据目录由 `POWERCONTEXT_HOME` 指定（默认 `backend/data/powercontext`），重启后记忆仍在。
- 注意：`POWERCONTEXT_DATA_DIR` 不是有效变量；早期排查时曾误用，实际路径来自 `POWERCONTEXT_HOME`。

### 项目到 scope 的映射

PowerContext 创建 scope 时不接受自定义 ID，因此后端按标题查找或创建：

```python
_scope_title(project_id) = f"LabTrail · {project_id}"
```

`_ensure_scope` 先 `GET /v1/scopes` 匹配标题，不存在才 `POST /v1/scopes`，并带幂等键
`labtrail-scope-{project_id}`。这样同一项目在多次调用中复用同一个 scope。

### 记忆数据流

```
POST /api/memory
  → PowerContext POST /v1/memory/remember
      {scope_id, kind, text, reason: "tags: ..."}
  → 返回 artifact_id

GET /api/memory/{project_id}
  → POST /v1/memory/entries/list
  → 过滤 state == "active"

POST /api/memory/search
  → POST /v1/memory/search {mode: "auto", limit}
  → 映射 artifact id / text / kind / score / matched_by

GET /api/memory/{project_id}/context
  → 汇总有效记忆，格式化为 [kind] content

DELETE /api/memory/{project_id}/{memory_id}
  → POST /v1/atomic-memory/lifecycle
      {scope_id, target: {artifact, state_version}, state: "forgotten"}
```

### 检索模式说明

PowerContext 的 `/v1/memory/search` 支持 `mode: auto|text|vector`。默认本地配置没有 embedding provider，
`vector` 会返回 `internal_error`；`auto` 会回退到全文检索（jieba 分词）。本项目固定使用 `auto`，并在
`matched_by` 中返回实际使用的检索方式。若部署时配置了 provider，`auto` 会自动升级为混合 / 向量检索。

### 为什么不用 seekdb 存记忆

早期版本曾用 seekdb 集合模拟记忆，但那样只能证明“会建表”，无法体现 PowerContext 的 scope、记忆类型、
生命周期和上下文恢复能力。现版本改为真实 Server 集成；seekdb 只负责文档检索，职责边界清晰。

## 实验数据

- 上传 CSV → `parse_experiment_csv` 校验列与方法 / 数据集
- 记录写入 `backend/data/experiments.json`，包含 `experiment_id`、方法、数据集、指标、参数
- `/api/experiments/{project_id}` 用 pandas 聚合均值 / 最值，生成 Recall-QPS 数据
- 周报直接读取同一份记录，保证数字与 CSV 一致

## 周报生成

1. 读取项目、文档清单、实验记录、PowerContext 记忆
2. 按方法和数据集汇总指标
3. 按记忆类型组织“结论 / 决策 / 计划 / 失败”
4. 模板渲染 Markdown；可选调用 OpenAI 兼容接口增强
5. 前端导出 `.md` 文件

模板模式是确定性的，便于评审复核；LLM 只做语言润色，不参与数字计算。

## 前端

- `App.tsx` 维护项目列表与当前项目上下文
- `Layout.tsx` 侧边栏导航，7 个页面
- `Search.tsx` 三种检索模式，展示来源与 RRF 融合分
- `Experiments.tsx` Recharts 图表 + 数据表
- `Memory.tsx` 记忆列表、搜索、保存、恢复上下文、遗忘
- `Reports.tsx` 生成 / 导出周报
- 样式：Tailwind CSS 4；自定义组件样式放在 `@layer components`，避免覆盖工具类

### 一个实际踩过的坑

`index.css` 早期把 `* { margin:0; padding:0 }` 放在所有 Tailwind 层之外。未分层的 CSS 优先级高于
`@layer utilities`，导致页面上所有 `p-*` / `m-*` 工具类失效（表现为侧边栏文字重叠、搜索框错位）。
修复方式是删除该全局重置（Tailwind preflight 已包含），并把 `.btn` / `.card` / `.input` 等移入
`@layer components`。这类问题只有实际打开浏览器才能发现，也是本次提交前重新截图审查的原因。

## 部署形态

### 本地开发
- PowerContext Server（8890）+ 后端（8000）+ Vite（5173）
- Vite 将 `/api` 代理到后端

### Docker Compose
- `powercontext`：内部 8890，数据卷 `powercontext-data`
- `backend`：8000，数据卷 `labtrail-data`，启动时按需加载演示数据
- `frontend`：nginx 静态文件 + `/api` 反向代理到 `backend:8000`
- PowerContext 不暴露到宿主机

### Qoder Sites
- 仅托管 `web/` 静态展示站
- 展示真实截图、真实数据快照与本地运行入口
- 不提供在线 API；页面明确说明运行时需本地启动

## 关键决策记录

| 决策 | 选择 | 理由 |
| --- | --- | --- |
| 向量模型 | all-MiniLM-L6-v2（pyseekdb 内置 ONNX） | 本地运行、无需 API Key、384 维足够演示 |
| 项目隔离 | metadata 过滤 | 嵌入式 seekdb 不支持 namespace（需 LakeBase） |
| 记忆存储 | PowerContext Server | 真实使用 scope / 生命周期，而非自建模拟 |
| 记忆检索 | `mode: auto` | 默认无 embedding provider，自动回退全文检索 |
| 实验存储 | JSON | 数据量小、便于溯源和评审直接查看 |
| 报告生成 | 模板优先 | 无密钥可运行、结果确定、数字可复核 |
| 网站 | 静态展示 + 快照演示 | 静态托管无法运行嵌入式数据库；明确标注避免误导 |
