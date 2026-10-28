# 验证指南

本文档提供 LabTrail 三个核心功能的可复现验证场景。

## 场景 A：研究知识检索（seekdb）

### 初始状态
- 演示项目已加载，包含 8 篇关于基于图的 ANN 搜索的研究笔记
- seekdb 中包含带有向量和全文索引的文档分块

### 操作步骤
1. 启动后端服务器
2. 发送搜索请求：
```bash
curl -X POST "http://localhost:8000/api/documents/search?project_id=demo_project" \
  -H "Content-Type: application/json" \
  -d '{"query": "Why does OOD query distribution degrade graph index performance?", "mode": "hybrid", "n_results": 5}'
```

### 预期输出
- 结果包含关于 OOD 查询和图索引的相关文本分块
- 每条结果包含：
  - `text`：匹配的文档分块
  - `metadata.file_name`：来源文档名称（如 "ood_analysis_notes.md"）
  - `metadata.source`：原始论文/笔记引用
  - `score`：RRF 融合的相关性评分
  - `fusion: true`：表示使用了混合搜索

### seekdb 证据
搜索使用了：
1. IVF 向量索引进行语义相似度匹配
2. 全文索引进行关键词匹配
3. RRF 融合组合结果

## 场景 B：研究记忆恢复（PowerContext 设计理念）

### 初始状态
- 演示项目已保存 6 条研究记忆

### 操作步骤

**步骤 1：查看现有记忆**
```bash
curl "http://localhost:8000/api/memory/demo_project"
```

**步骤 2：保存新记忆**
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

**步骤 3：模拟新会话 - 恢复上下文**
```bash
curl "http://localhost:8000/api/memory/demo_project/context"
```

### 预期输出
- 上下文端点返回所有已保存的记忆，包括新保存的那条
- 记忆按类型分组（结论、决策、计划、失败）
- 包含关于 OOD 优先级的新决策

**步骤 4：搜索记忆**
```bash
curl -X POST "http://localhost:8000/api/memory/search" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "demo_project", "query": "What should we prioritize?", "n_results": 3}'
```

### PowerContext 证据
- 记忆持久化存储在 seekdb 中，带有结构化元数据
- 通过 project_id 过滤实现项目隔离
- 对记忆内容进行语义搜索
- 上下文端点展示了跨会话恢复能力

## 场景 C：实验分析与周报生成

### 初始状态
- 演示项目包含来自 experiments.csv 的 30 条实验记录
- 数据涵盖 HNSW 和 Vamana 两种方法，跨 4 个数据集

### 操作步骤

**步骤 1：查看实验分析**
```bash
curl "http://localhost:8000/api/experiments/demo_project"
```

### 预期输出
```json
{
  "total_records": 30,
  "methods": ["HNSW", "Vamana"],
  "datasets": ["glove-200-angular", "glove-200-angular-ood", "sift-128-euclidean", "sift-128-euclidean-ood"],
  "metrics": ["index_build_time", "peak_memory", "qps", "recall@10"],
  "summary": {
    "HNSW": {
      "recall@10": {"mean": 0.884, "min": 0.7845, "max": 0.9678}
    },
    "Vamana": {
      "recall@10": {"mean": 0.9015, "min": 0.8312, "max": 0.9612}
    }
  }
}
```

**步骤 2：生成周报**
```bash
curl -X POST "http://localhost:8000/api/reports/weekly" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "demo_project"}'
```

### 预期输出
- 包含 9 个部分的结构化 Markdown 报告
- 所有实验数字与原始 CSV 数据一致
- 研究记忆包含在结论和决策部分中
- 来源部分确认数据可追溯性

### 数据可追溯性证据
- 报告数字可与 `demo-data/experiments.csv` 对照验证
- 每条实验记录有 `experiment_id` 链接至原始数据
- 记忆内容与保存的研究结论一致

## 自动化测试脚本

```bash
#!/bin/bash
# 运行所有验证场景

BASE_URL="http://localhost:8000"
PROJECT_ID="demo_project"

echo "=== 健康检查 ==="
curl -s "$BASE_URL/api/health" | python3 -m json.tool

echo -e "\n=== 场景 A：搜索 ==="
curl -s -X POST "$BASE_URL/api/documents/search?project_id=$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{"query": "OOD query distribution", "mode": "hybrid", "n_results": 3}' | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'结果数: {d[\"count\"]}, 模式: {d[\"mode\"]}')"

echo -e "\n=== 场景 B：记忆 ==="
curl -s "$BASE_URL/api/memory/$PROJECT_ID" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'记忆数: {len(d)}')"

echo -e "\n=== 场景 C：实验 ==="
curl -s "$BASE_URL/api/experiments/$PROJECT_ID" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'记录数: {d[\"total_records\"]}, 方法: {d[\"methods\"]}')"

echo -e "\n=== 报告生成 ==="
curl -s -X POST "$BASE_URL/api/reports/weekly" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\"}" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'报告长度: {len(d[\"report\"])} 字符')"

echo -e "\n=== 所有场景验证完成 ==="
```
