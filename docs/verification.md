# 验证指南

本文档说明如何复现 LabTrail 的核心能力。所有结果均来自真实运行的后端，不使用预置假数据。

## 环境准备

```bash
# 终端 1：PowerContext Server（默认 127.0.0.1:8890）
./scripts/start_powercontext.sh

# 终端 2：加载演示数据并启动后端（默认 127.0.0.1:8000）
source venv/bin/activate
python scripts/load_demo_data.py
cd backend && uvicorn app.main:app --port 8000
```

健康检查应返回：

```json
{"status": "ok", "services": {"seekdb": "connected", "powercontext": "ready"}}
```

## 一键验证脚本

```bash
python scripts/verify.py
```

脚本执行 12 项检查，逐项打印 PASS/FAIL 和真实耗时，并把原始输出写入：

- `evidence/verification.log`：人类可读的检查表与样本
- `evidence/verification.json`：机器可读的完整结果

最近一次运行（2026-10-29）结果：**12/12 通过**。

| # | 检查项 | 结果 | 耗时 | 实际输出 |
| --- | --- | --- | --- | --- |
| 1 | API 健康（seekdb + PowerContext） | PASS | 184 ms | `seekdb=connected, powercontext=ready` |
| 2 | PowerContext 直连健康 + scope | PASS | 11 ms | `ready, scopes=2 -> Default, LabTrail · demo_project` |
| 3 | seekdb 混合检索 | PASS | 595 ms（进程首次检索含向量化预热） | 5 条结果，top：`ood_analysis_notes.md`、`query_aware_construction.md`、`build_time_analysis.md` |
| 4 | seekdb 向量检索 | PASS | 80 ms | 3 条结果（余弦相似度），top：`query_aware_construction.md` (0.6877) |
| 5 | seekdb 全文检索 | PASS | 4 ms | 3 条结果（全文相关度），top：`ood_analysis_notes.md` (0.9265) |
| 6 | 实验数据 | PASS | 3 ms | 30 条记录，方法 HNSW / Vamana，Vamana recall@10 均值 0.9015 |
| 7 | PowerContext 写入记忆 | PASS | 91 ms | 返回真实 `artifact_id` 与 `scope_id` |
| 8 | PowerContext 检索记忆 | PASS | 35 ms | 5 条结果，命中刚写入的验证记忆 |
| 9 | PowerContext 恢复上下文 | PASS | 27 ms | 上下文 1324 字符，包含新写入决策 |
| 10 | PowerContext 遗忘记忆 | PASS | 98 ms | 目标记忆生命周期置为 `forgotten`，列表剩余 6 条 |
| 11 | 周报生成 | PASS | 27 ms | 4439 字符，包含实验数据与研究记忆 |
| 12 | PowerContext 持久化文件 | PASS | 1 ms | `backend/data/powercontext` 下 7 个文件，1.4 MB |

## 场景 A：研究知识检索（seekdb）

演示项目包含 8 篇关于图 ANN 检索的研究笔记，全部写入 seekdb，并建立 IVF 向量索引与 FULLTEXT 索引。

```bash
curl -X POST "http://localhost:8000/api/documents/search?project_id=demo_project" \
  -H "Content-Type: application/json" \
  -d '{"query": "Why does OOD query distribution degrade graph index performance?", "mode": "hybrid", "n_results": 5}'
```

三种模式走的是三条不同的 seekdb 查询路径，而不是同一个结果换个标签：

| 模式 | seekdb 调用 | 分数含义 | 本次 top-1 |
| --- | --- | --- | --- |
| `hybrid` | `Collection.hybrid_search(query=全文, knn=向量, rank=RRF)` | RRF 融合分 | `ood_analysis_notes.md` 0.0325 |
| `vector` | `Collection.query`（IVF 余弦） | 余弦相似度，越大越相似 | `query_aware_construction.md` 0.6877 |
| `fulltext` | `hybrid_search` + `where_document={"$contains": ...}` | 全文相关度 | `ood_analysis_notes.md` 0.9265 |

每条结果都带 `metadata.file_name`、`metadata.page`、`metadata.source`，可追溯到原始笔记。

**可观察差异**：全文检索 top-1 是关键词密度最高的 OOD 笔记（0.9265），向量检索 top-1 是语义更接近“查询分布感知构建”的笔记（0.6877），混合检索则由 RRF 融合两路结果。三者结果与分数均不同，说明模式确实生效。

## 场景 B：研究记忆恢复（PowerContext Server）

记忆不存放在 seekdb，而是由独立的 PowerContext Server 持久化管理。LabTrail 的每个项目对应一个 PowerContext scope（`LabTrail · {project_id}`），实现项目隔离。

**步骤 1：查看现有记忆**（经 LabTrail 后端调用 PowerContext `/v1/memory/entries/list`）

```bash
curl "http://localhost:8000/api/memory/demo_project"
```

**步骤 2：写入一条决策**

```bash
curl -X POST "http://localhost:8000/api/memory" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "demo_project",
    "content": "记住：当前优先级是优化 OOD 感知的图构建。在 OOD 实验完成之前，不要研究量化压缩。",
    "memory_type": "decision",
    "tags": ["OOD", "priority", "decision"]
  }'
```

后端实际请求 `POST /v1/memory/remember`，返回 `artifact_id`、`scope_id` 与 `changed` 字段。

**步骤 3：模拟新会话，恢复上下文**

```bash
curl "http://localhost:8000/api/memory/demo_project/context"
```

返回的上下文中包含刚写入的决策。

**步骤 4：语义检索记忆**

```bash
curl -X POST "http://localhost:8000/api/memory/search" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "demo_project", "query": "What should we prioritize?", "n_results": 3}'
```

返回 `hits`、`score`、`matched_by`。默认本地配置未接 embedding provider，PowerContext 自动使用全文检索（jieba）；配置 provider 后会自动启用向量检索。

**步骤 5：遗忘记忆**

```bash
curl -X DELETE "http://localhost:8000/api/memory/demo_project/{memory_id}"
```

后端调用 `/v1/atomic-memory/lifecycle`，把该记忆状态置为 `forgotten`，列表中不再返回。

### PowerContext 证据

- `GET http://127.0.0.1:8890/health/ready` 返回 `ready`
- `GET http://127.0.0.1:8890/v1/scopes` 可见 `LabTrail · demo_project`
- 重启 PowerContext Server 后，记忆仍从 `POWERCONTEXT_HOME`（本地为 `backend/data/powercontext`）恢复
- `evidence/verification.log` 第 2、7–10、12 项即为上述调用的真实输出

## 场景 C：实验分析与周报生成

```bash
curl "http://localhost:8000/api/experiments/demo_project"
```

预期输出（实测）：

```json
{
  "total_records": 30,
  "methods": ["HNSW", "Vamana"],
  "datasets": ["glove-200-angular", "glove-200-angular-ood", "sift-128-euclidean", "sift-128-euclidean-ood"],
  "metrics": ["index_build_time", "peak_memory", "qps", "recall@10"],
  "summary": {
    "HNSW": {"recall@10": {"mean": 0.884}},
    "Vamana": {"recall@10": {"mean": 0.9015}}
  }
}
```

```bash
curl -X POST "http://localhost:8000/api/reports/weekly" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "demo_project"}'
```

实测生成 4439 字符的结构化 Markdown，包含实验统计与研究记忆，所有数字可与 `demo-data/experiments.csv` 对照验证。

## 在线静态演示

<https://labtrail-ufmfmmmc4qq.qoder.zone> 上的交互演示数据由 `scripts/export_web_demo.py` 从上述真实运行实例导出（`web/assets/data/demo.json`），并附有 `evidence/verification.json` 的 12 项检查结果。静态站点不提供 `/api/*`，完整功能请按上述步骤在本地启动。
