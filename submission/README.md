# LabTrail

**AI 科研知识与实验管理工作台**

> 从碎片化科研到连接式知识管理。

[![OceanBase Qoder Track](https://img.shields.io/badge/OceanBase-Qoder%20Track-blue)](https://github.com/oceanbase)
[![seekdb](https://img.shields.io/badge/seekdb-AI--Native%20Database-green)](https://github.com/oceanbase/seekdb)
[![PowerContext](https://img.shields.io/badge/PowerContext-Research%20Memory-purple)](https://github.com/oceanbase/powercontext)

## 项目概述

LabTrail 是一个综合性科研工作台，帮助科研人员管理研究知识、实验数据和长期研究上下文。系统集成 **seekdb**（OceanBase AI 原生混合搜索数据库）用于文档存储与检索，并运用 **PowerContext** 设计理念实现持久化研究记忆管理。

### 核心工作流

**导入科研资料 → 知识检索 → 实验分析 → 保存研究记忆 → 恢复上下文 → 生成周报**

## 核心功能

### 1. 研究项目管理
- 创建和管理多个研究项目
- 跟踪研究目标、方向和进度
- 项目隔离的知识库和记忆空间

### 2. 文档知识库（seekdb）
- 导入 PDF 论文、Markdown 笔记、TXT 文档和 CSV 数据
- 自动文档分块和向量化
- **seekdb 驱动的混合搜索**：向量语义搜索 + 全文搜索 + RRF 融合排序
- 来源追溯：显示文档名称、页码和原文引用

### 3. 智能证据检索（seekdb）
- 三种搜索模式：向量搜索、全文搜索和混合搜索
- 倒数排名融合（RRF）组合多策略搜索结果
- 按项目、文档类型和元数据过滤
- 每条结果包含相关性评分、来源文档和原文

### 4. 实验数据分析
- 导入标准化 CSV 实验结果
- 支持指标：Recall@K、QPS、索引构建时间、峰值内存、延迟
- 交互式图表：Recall-QPS 曲线、构建时间对比、内存对比
- 按方法、数据集和指标类型过滤
- 所有图表基于真实导入数据计算，可追溯至原始 CSV 记录

### 5. 长期研究记忆（PowerContext）
- 保存研究结论、决策、计划和失败方案
- 基于 seekdb 的项目隔离记忆存储
- 跨会话上下文恢复
- 记忆内容语义搜索
- 结构化记忆类型与标签管理

### 6. 科研周报生成器
- 基于真实项目数据自动生成周报
- 包含：研究目标、文献发现、实验进展、结论和计划
- 所有实验数据可追溯至原始 CSV 记录
- 模板生成模式（无需 LLM API 密钥）
- 可选 LLM 增强生成（需用户提供 API 密钥）
- 支持 Markdown 导出

### 7. 专业仪表盘
- 实时项目统计
- 最近活动动态
- 快速访问所有功能
- 实验方法和数据集概览

## 技术栈

### 前端
- **React 19** + **TypeScript** + **Vite**
- **Tailwind CSS** 样式设计
- **Recharts** 数据可视化
- **Lucide React** 图标库
- **React Router** 路由管理

### 后端
- **Python 3.12** + **FastAPI**
- **pyseekdb**（seekdb Python SDK）文档存储与混合搜索
- **sentence-transformers** 本地向量化（all-MiniLM-L6-v2，无需 API 密钥）
- **PyMuPDF** PDF 解析
- **pandas** 实验数据处理

### 数据库与记忆
- **seekdb**（OceanBase AI 原生数据库）：文档存储、向量索引（IVF）、全文索引、混合搜索
- **PowerContext 设计理念**：基于 seekdb 持久化存储的研究记忆管理

### 部署
- **Qoder Sites** 公共网站部署
- 支持 Docker Compose 本地部署

## 快速开始

### 环境要求
- Python 3.12+
- Node.js 18+
- npm 或 yarn

### 安装步骤

1. 克隆仓库：
```bash
git clone <repository-url>
cd labtrail
```

2. 配置 Python 后端：
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

3. 配置前端：
```bash
cd frontend
npm install
```

4. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件设置您的配置
```

### 本地运行

1. 启动后端：
```bash
source venv/bin/activate
cd backend
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. 启动前端（新终端窗口）：
```bash
cd frontend
npm run dev
```

3. 加载演示数据：
```bash
source venv/bin/activate
PYTHONPATH=backend python scripts/load_demo_data.py
```

4. 在浏览器中打开 http://localhost:5173

### Docker 部署

```bash
docker-compose up -d
```

## 演示项目

内置演示项目涵盖 **基于图的近似最近邻搜索**：

- **研究主题**：HNSW、Vamana、OOD 查询鲁棒性
- **文档**：8 篇包含论文摘要的研究笔记
- **实验**：30 条记录，涵盖 2 种方法和 4 个数据集
- **记忆**：6 条研究结论、决策和计划

### 演示场景

**场景 A：研究知识检索**
1. 进入"检索"页面
2. 输入："为什么 OOD 查询分布会影响图索引性能？"
3. 查看混合搜索结果，包含来源文档和相关性评分

**场景 B：研究记忆恢复**
1. 进入"研究记忆"页面
2. 点击"恢复上下文"查看已保存的研究记忆
3. 添加新记忆："当前优先级：优化 OOD 感知的图构建"
4. 验证记忆已保存并可搜索

**场景 C：实验分析与报告**
1. 进入"实验分析"页面
2. 查看 Recall-QPS 曲线和方法对比
3. 进入"周报"页面
4. 点击"生成周报"，基于真实实验数据生成周报

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   前端 (React)                        │
│  仪表盘 │ 文档库 │ 检索 │ 实验分析 │ 研究记忆 │ 周报  │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP API
┌───────────────────────┴─────────────────────────────┐
│                  后端 (FastAPI)                       │
│  项目 │ 文档 │ 搜索 │ 实验 │ 记忆 │ 报告             │
└──────┬────────┬────────┬────────┬────────┬──────────┘
       │        │        │        │        │
  ┌────┴───┐ ┌─┴──────┐ │  ┌────┴───┐ ┌──┴──────────┐
  │ seekdb │ │ seekdb │ │  │ seekdb │ │  seekdb     │
  │ 文档   │ │ 向量   │ │  │ 实验   │ │  研究记忆   │
  │ 集合   │ │ 搜索   │ │  │ 集合   │ │  集合       │
  └────────┘ └────────┘ │  └────────┘ └─────────────┘
                    ┌───┴────┐
                    │sentence│
                    │-trans- │
                    │formers │
                    └────────┘
```

### seekdb 集成
- **文档集合**：存储文档分块及元数据（file_name、page、doc_id、project_id）
- **实验集合**：存储实验元数据供参考
- **研究记忆集合**：存储研究记忆，包含类型和标签
- **向量索引**：IVF 索引，余弦距离（维度 384，来自 all-MiniLM-L6-v2）
- **全文索引**：启用关键词搜索
- **混合搜索**：RRF 融合向量和全文搜索结果

### 研究记忆（PowerContext 设计理念）
- 记忆存储在 seekdb 中，带有结构化元数据
- 类型：结论、决策、计划、失败、通用
- 通过元数据过滤实现项目隔离
- 语义搜索用于上下文恢复
- 跨会话持久化

## 项目结构

```
labtrail/
├── frontend/              # React + TypeScript + Vite 前端
│   ├── src/
│   │   ├── components/    # 布局和共享组件
│   │   └── pages/         # 仪表盘、文档库、检索等页面
│   └── package.json
├── backend/               # Python FastAPI 后端
│   ├── app/
│   │   ├── api/           # API 路由处理
│   │   ├── ingestion/     # 文档解析（PDF、MD、CSV）
│   │   ├── experiments/   # 实验数据处理
│   │   ├── reports/       # 周报生成
│   │   ├── config.py      # 配置管理
│   │   ├── main.py        # FastAPI 应用入口
│   │   ├── seekdb_service.py      # seekdb 集成
│   │   ├── powercontext_service.py # 记忆管理
│   │   ├── embedding_service.py   # 本地向量化
│   │   └── project_service.py     # 项目 CRUD
│   └── requirements.txt
├── demo-data/             # 示例研究数据
│   ├── research_notes.md
│   └── experiments.csv
├── scripts/
│   └── load_demo_data.py  # 演示数据加载器
├── docs/                  # 文档
├── docker-compose.yml     # Docker 部署配置
├── .env.example           # 环境变量模板
└── README.md
```

## API 接口

### 项目管理
- `GET /api/projects` - 获取所有项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 获取项目详情
- `GET /api/projects/{id}/dashboard` - 获取仪表盘统计

### 文档管理
- `POST /api/documents/upload` - 上传并索引文档
- `GET /api/documents/{project_id}` - 获取文档列表
- `POST /api/documents/search` - 搜索文档（混合/向量/全文）
- `DELETE /api/documents/{project_id}/{doc_id}` - 删除文档

### 实验管理
- `POST /api/experiments/upload` - 上传实验 CSV
- `GET /api/experiments/{project_id}` - 获取实验分析
- `GET /api/experiments/{project_id}/recall-qps` - 获取 Recall-QPS 数据

### 研究记忆
- `POST /api/memory` - 保存研究记忆
- `GET /api/memory/{project_id}` - 获取记忆列表
- `POST /api/memory/search` - 搜索记忆
- `GET /api/memory/{project_id}/context` - 获取研究上下文

### 报告生成
- `POST /api/reports/weekly` - 生成周报

## 测试

### 运行后端测试
```bash
source venv/bin/activate
cd backend
PYTHONPATH=. pytest tests/
```

### 手动验证
1. 启动后端和前端
2. 加载演示数据
3. 测试演示部分中的每个场景
4. 验证搜索结果包含来源文档
5. 验证实验图表显示真实数据
6. 验证记忆在页面刷新后持久化

## 已知限制

- seekdb 嵌入式模式不支持命名空间（需要 LakeBase 云端）；项目隔离使用元数据过滤
- PowerContext v1.4.1+ 需要服务器部署；研究记忆使用 seekdb 存储并结合 PowerContext 设计理念
- PDF 解析仅提取文本（不支持图片/表格理解）
- LLM 增强报告生成需要用户提供 API 密钥
- 演示实验数据为合成数据，已明确标注

## 安全性

- API 密钥不会存储在前端或提交到 git
- 文件上传有大小限制（50MB）和格式验证
- 项目数据通过 project_id 隔离
- 演示数据中不包含敏感凭据

## 许可证

本项目为 OceanBase 数据库大赛 Qoder 赛道参赛作品。

## 致谢

- [seekdb](https://github.com/oceanbase/seekdb) - OceanBase AI 原生混合搜索数据库
- [PowerContext](https://github.com/oceanbase/powercontext) - OceanBase 上下文管理框架
- [Qoder](https://qoder.com) - AI 驱动的开发平台
- [sentence-transformers](https://www.sbert.net/) - 本地向量化模型

## 链接

- **在线演示**：[https://labtrail-ufmfmmmc4qq.qoder.zone](https://labtrail-ufmfmmmc4qq.qoder.zone)
- **源代码**：[GitHub 仓库地址]
- **大赛**：OceanBase 数据库大赛 - Qoder 赛道
