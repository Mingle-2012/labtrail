# 架构文档

## 系统架构

LabTrail 采用三层架构：

### 前端（React + TypeScript + Vite）
- 单页应用，客户端路由
- Tailwind CSS 响应式设计
- Recharts 数据可视化
- 通过 REST API 与后端通信

### 后端（Python + FastAPI）
- RESTful API 服务器
- 文档摄入管线（PDF、Markdown、CSV、TXT）
- seekdb 集成用于存储和检索
- 研究记忆管理
- 实验数据分析
- 报告生成

### 数据层（seekdb）
- 嵌入式模式用于本地开发
- IVF 向量索引（维度 384，余弦距离）
- 全文索引用于关键词搜索
- 多个集合存储不同类型数据

## 数据模型

### 文档集合
```
{
  "id": "doc_id_chunk_hash",
  "text": "分块内容",
  "metadata": {
    "project_id": "string",
    "doc_id": "string",
    "file_name": "string",
    "file_type": "pdf|markdown|csv|text",
    "page": number (PDF 页码),
    "chunk_index": number,
    "source": "string"
  }
}
```

### 研究记忆集合
```
{
  "id": "mem_xxxx",
  "text": "记忆内容",
  "metadata": {
    "project_id": "string",
    "memory_type": "conclusion|decision|plan|failure|general",
    "tags": "comma,separated,tags",
    "memory_id": "string"
  }
}
```

### 实验数据（JSON 文件存储）
```
{
  "experiment_id": "string",
  "project_id": "string",
  "method": "string",
  "dataset": "string",
  "timestamp": "ISO datetime",
  "metric_name": "string",
  "metric_value": number,
  "parameters": {}
}
```

## 搜索管线

1. 用户提交查询
2. 使用 sentence-transformers（all-MiniLM-L6-v2）对查询文本进行向量化
3. **向量搜索**：seekdb IVF 索引返回余弦相似度 Top-K
4. **全文搜索**：seekdb 全文索引返回文本匹配 Top-K
5. **RRF 融合**：使用倒数排名融合（k=60）组合结果
6. 通过元数据应用项目过滤
7. 返回结果，包含评分、元数据和来源信息

## 记忆管线

1. 用户保存研究记忆（结论、决策、计划等）
2. 记忆文本向量化后存储到 seekdb
3. 元数据包含 project_id、memory_type 和 tags
4. 上下文恢复时，检索该项目的所有记忆
5. 搜索时，使用语义相似度查找相关记忆
6. 通过 seekdb 存储实现跨会话持久化

## 报告生成管线

1. 加载项目数据：文档、实验、记忆
2. 按方法和数据集汇总实验指标
3. 按类型检索研究记忆（结论、决策、计划、失败）
4. 使用模板生成结构化报告
5. 可选：如果提供了 API 密钥，使用 LLM 增强
6. 导出为 Markdown

## 关键工程决策

### 选择 seekdb 而非其他向量数据库
- 原生混合搜索（向量 + 全文）集成在一个系统中
- 嵌入式模式实现零配置本地开发
- OceanBase 生态集成，符合大赛要求
- IVF 索引支持通过元数据实现类似命名空间的过滤

### 本地向量化模型
- 核心功能无需 API 密钥
- all-MiniLM-L6-v2：384 维，推理速度快
- 使用 ONNX 运行时在 CPU 上运行
- 质量和速度的良好平衡

### JSON 文件存储项目/实验数据
- 简单，无需额外数据库
- seekdb 处理搜索的核心工作
- 易于备份和迁移
- 适合单用户科研工作空间

### 基于模板的报告生成
- 无需 LLM API 密钥即可工作
- 所有数字可追溯至真实数据
- LLM 增强为可选项
- 确定性输出，可复现
