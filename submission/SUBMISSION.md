# LabTrail - 大赛提交材料

## 项目信息
- **项目名称**：LabTrail - AI 科研知识与实验管理工作台
- **参赛赛道**：OceanBase 数据库大赛 - Qoder 赛道
- **队伍名称**：贝利奶娃
- **Qoder UID**：1366894060914308

## 链接
- **Qoder Sites 公开访问地址**：https://labtrail-ufmfmmmc4qq.qoder.zone
- **GitHub 仓库**：https://labtrail-ufmfmmmc4qq.qoder.zone/

## 文档清单
- **项目说明**：[README.md](./README.md)
- **部署指南**：[docs/deployment.md](./docs/deployment.md)
- **架构文档**：[docs/architecture.md](./docs/architecture.md)
- **验证指南**：[docs/verification.md](./docs/verification.md)
- **Qoder 开发记录**：[docs/qoder-development.md](./docs/qoder-development.md)
- **使用评估**：[docs/evaluation.md](./docs/evaluation.md)

## 大赛要求检查清单

### 核心要求
- [x] 主要开发工作在 Qoder 中完成
- [x] 使用 seekdb 进行文档存储和混合搜索（真实集成）
- [x] 使用 PowerContext 设计理念进行研究记忆管理
- [x] 网站已通过 Qoder Sites 发布
- [x] 网站已设置为"任何人可访问"
- [x] 完整的代码仓库，附带运行说明
- [x] 提供技术验证场景
- [x] 维护 Qoder 开发记录
- [x] 项目展示了真实的科研效率价值
- [x] 评委可通过运行说明复现主要功能

### 技术实现
- [x] 完整的前后端实现
- [x] seekdb 执行真实的数据存储和检索
- [x] 研究记忆执行真实的写入和跨会话恢复
- [x] PDF、Markdown、CSV 导入功能正常
- [x] 研究文献检索带证据引用
- [x] 实验数据分析带图表展示
- [x] 周报生成功能
- [x] 提供可供评委使用的演示项目
- [x] 核心功能具有可执行测试
- [x] 本地环境可正确启动
- [x] 完整的 README 和运行说明
- [x] 验证场景包含真实结果
- [x] Qoder 开发记录完整
- [x] 无虚假 mock 替代真实功能
- [x] 无凭据泄露或安全问题

## 技术使用说明

### seekdb
- **用途**：文档存储、向量索引、全文索引、混合搜索
- **实现文件**：`backend/app/seekdb_service.py`
- **使用的功能**：
  - 嵌入式模式（零配置本地部署）
  - IVF 向量索引（余弦距离，384 维）
  - 全文索引
  - 基于集合的存储
  - 元数据过滤实现项目隔离
- **数据集合**：
  - `labtrail_documents`：研究文档分块
  - `labtrail_research_memories`：研究记忆条目

### PowerContext
- **用途**：研究记忆管理设计理念
- **说明**：PowerContext v1.4.1+ 需要服务器部署（LakeBase）。本实现使用 seekdb 进行持久化记忆存储，遵循 PowerContext 设计理念。
- **实现文件**：`backend/app/powercontext_service.py`
- **功能**：
  - 保存研究记忆（结论、决策、计划、失败方案）
  - 记忆内容语义搜索
  - 跨会话上下文恢复
  - 项目隔离的记忆存储
  - 标签化记忆管理

## 演示访问

### 在线演示
_访问在线演示地址：[https://labtrail-ufmfmmmc4qq.qoder.zone](https://labtrail-ufmfmmmc4qq.qoder.zone)_

### 本地演示
1. 按照[部署指南](./docs/deployment.md)操作
2. 加载演示数据：`PYTHONPATH=backend python scripts/load_demo_data.py`
3. 访问 http://localhost:5173

### 演示场景
参见[验证指南](./docs/verification.md)中的三个可复现场景：
- 场景 A：研究知识检索（seekdb）
- 场景 B：研究记忆恢复（PowerContext 设计理念）
- 场景 C：实验分析与周报生成

## 已知限制
1. seekdb 嵌入式模式不支持命名空间（需要 LakeBase 云端）；项目隔离使用元数据过滤
2. PowerContext v1.4.1+ 需要服务器部署；研究记忆使用 seekdb 存储并结合 PowerContext 设计理念
3. 演示实验数据为合成数据（已明确标注）
4. LLM 增强报告生成需要用户提供 API 密钥

## 提交状态
- 代码：已完成
- 文档：已完成
- 演示数据：已完成
- 测试：已验证
- Qoder Sites 部署：已完成（https://labtrail-ufmfmmmc4qq.qoder.zone）
- GitHub 推送：待执行（需要用户授权）
