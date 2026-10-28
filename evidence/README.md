# 验证证据

本目录保存 `scripts/verify.py` 对真实运行实例的验证输出，以及应用界面截图。

## 文件说明

| 文件 | 内容 |
| --- | --- |
| `verification.log` | 12 项端到端检查的 PASS/FAIL、耗时、实际输出与样本（人类可读） |
| `verification.json` | 同一批检查的机器可读结果，供网站验证区渲染 |
| `screenshots/dashboard.png` | 仪表盘：文档、实验记录、记忆数量统计 |
| `screenshots/library.png` | 文档库：8 篇研究笔记及来源 |
| `screenshots/search.png` | 检索页：混合检索结果与来源文件 |
| `screenshots/experiments.png` | 实验分析：HNSW / Vamana 指标对比 |
| `screenshots/memory.png` | 研究记忆：6 条记忆与类型 |
| `screenshots/memory-context.png` | 记忆上下文恢复：跨会话拼接的完整上下文 |
| `screenshots/reports.png` | 周报生成：包含实验数字与记忆的 Markdown |

## 复现方式

```bash
./scripts/start_powercontext.sh                 # 终端 1
python scripts/load_demo_data.py                # 终端 2
cd backend && uvicorn app.main:app --port 8000  # 终端 2
python scripts/verify.py                        # 终端 3
```

脚本会覆盖本目录下的 `verification.log` 与 `verification.json`。最近一次运行（2026-10-29）：12/12 通过。

## 截图说明

截图由本机运行的 LabTrail 前端（React + Vite，连接真实后端）通过 Playwright 自动拍摄，未做内容修改；页面中的统计数字与 `demo-data/` 及 seekdb / PowerContext 中的实际数据一致。
