# LabTrail

**AI Research Knowledge & Experiment Workspace**

**AI 科研知识与实验管理工作台**

> From scattered research to connected knowledge.

[![OceanBase Qoder Track](https://img.shields.io/badge/OceanBase-Qoder%20Track-blue)](https://github.com/oceanbase)
[![seekdb](https://img.shields.io/badge/seekdb-AI--Native%20Database-green)](https://github.com/oceanbase/seekdb)
[![PowerContext](https://img.shields.io/badge/PowerContext-Research%20Memory-purple)](https://github.com/oceanbase/powercontext)

## Project Overview

LabTrail is a comprehensive research workspace that helps scientists and engineers manage their research knowledge, experiment data, and long-term research context. It integrates **seekdb** (OceanBase's AI-native hybrid search database) for document storage and retrieval, and **PowerContext** concepts for persistent research memory management.

### Core Workflow

**Import Research Materials → Knowledge Retrieval → Experiment Analysis → Save Research Memory → Restore Context → Generate Weekly Reports**

## Key Features

### 1. Research Project Management
- Create and manage multiple research projects
- Track research goals, directions, and progress
- Project-isolated knowledge bases and memories

### 2. Document Knowledge Base (seekdb)
- Import PDF papers, Markdown notes, TXT documents, and CSV data
- Automatic document chunking and vectorization
- **seekdb-powered hybrid search**: vector semantic search + full-text search + RRF fusion ranking
- Source tracing with document names, page numbers, and original text references

### 3. Intelligent Evidence Retrieval (seekdb)
- Three search modes: vector search, full-text search, and hybrid search
- Reciprocal Rank Fusion (RRF) for combining results from multiple search strategies
- Filter by project, document type, and metadata
- Each result includes relevance score, source document, and original text

### 4. Experiment Data Analysis
- Import CSV experiment results with standardized schema
- Support for metrics: Recall@K, QPS, Index Build Time, Peak Memory, Latency
- Interactive charts: Recall-QPS curves, build time comparison, memory comparison
- Filter by method, dataset, and metric type
- All charts computed from real imported data, traceable to original CSV records

### 5. Long-term Research Memory (PowerContext)
- Save research conclusions, decisions, plans, and failed approaches
- Project-isolated memory storage via seekdb
- Cross-session context recovery
- Semantic search over saved memories
- Structured memory types with tagging

### 6. Research Weekly Report Generator
- Auto-generated reports from real project data
- Includes: research goals, literature findings, experiment progress, conclusions, and plans
- All experiment numbers traceable to original CSV records
- Template-based generation (no LLM API key required)
- Optional LLM-enhanced generation with user-provided API key
- Markdown export support

### 7. Professional Dashboard
- Real-time project statistics
- Recent activity feed
- Quick access to all features
- Experiment method and dataset overview

## Technology Stack

### Frontend
- **React 19** + **TypeScript** + **Vite**
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **Lucide React** for icons
- **React Router** for navigation

### Backend
- **Python 3.12** + **FastAPI**
- **pyseekdb** (seekdb Python SDK) for document storage and hybrid search
- **sentence-transformers** for local embedding (all-MiniLM-L6-v2, no API key needed)
- **PyMuPDF** for PDF parsing
- **pandas** for experiment data processing

### Database & Memory
- **seekdb** (OceanBase AI-native database): Document storage, vector indexing (IVF), full-text indexing, hybrid search
- **PowerContext concepts**: Research memory management with persistent storage via seekdb

### Deployment
- **Qoder Sites** for public website deployment
- Docker Compose support for local deployment

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd labtrail
```

2. Set up Python backend:
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

3. Set up frontend:
```bash
cd frontend
npm install
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

### Running Locally

1. Start the backend:
```bash
source venv/bin/activate
cd backend
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Start the frontend (in a new terminal):
```bash
cd frontend
npm run dev
```

3. Load demo data:
```bash
source venv/bin/activate
PYTHONPATH=backend python scripts/load_demo_data.py
```

4. Open http://localhost:5173 in your browser

### Docker Deployment

```bash
docker-compose up -d
```

## Demo Project

The included demo project covers **Graph-based Approximate Nearest Neighbor Search**:

- **Research Topic**: HNSW, Vamana, OOD query robustness
- **Documents**: 8 research notes with paper summaries
- **Experiments**: 30 records across 2 methods and 4 datasets
- **Memories**: 6 research conclusions, decisions, and plans

### Demo Scenarios

**Scenario A: Research Knowledge Retrieval**
1. Navigate to "检索" (Search) page
2. Enter: "Why does OOD query distribution affect graph index performance?"
3. View hybrid search results with source documents and relevance scores

**Scenario B: Research Memory Recovery**
1. Navigate to "研究记忆" (Memory) page
2. Click "恢复上下文" (Restore Context) to view saved research memories
3. Add a new memory: "Current priority: optimize OOD-aware graph construction"
4. Verify the memory is saved and searchable

**Scenario C: Experiment Analysis & Report**
1. Navigate to "实验分析" (Experiments) page
2. View Recall-QPS curves and method comparisons
3. Navigate to "周报" (Reports) page
4. Click "生成周报" to generate a weekly report with real experiment data

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (React)                    │
│  Dashboard │ Library │ Search │ Experiments │ Memory  │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP API
┌───────────────────────┴─────────────────────────────┐
│                  Backend (FastAPI)                    │
│  Projects │ Documents │ Search │ Experiments │ Memory │
└──────┬────────┬────────┬────────┬────────┬──────────┘
       │        │        │        │        │
  ┌────┴───┐ ┌─┴──────┐ │  ┌────┴───┐ ┌──┴──────────┐
  │ seekdb │ │ seekdb │ │  │ seekdb │ │  seekdb     │
  │ docs   │ │ vector │ │  │ exps   │ │  memories   │
  │collection│ │ search │ │  │collection│ │ collection │
  └────────┘ └────────┘ │  └────────┘ └─────────────┘
                    ┌───┴────┐
                    │sentence│
                    │-trans- │
                    │formers │
                    └────────┘
```

### seekdb Integration
- **Documents Collection**: Stores document chunks with metadata (file_name, page, doc_id, project_id)
- **Experiments Collection**: Stores experiment metadata for reference
- **Research Memories Collection**: Stores research memories with type and tags
- **Vector Index**: IVF with cosine distance (dimension 384 from all-MiniLM-L6-v2)
- **Full-Text Index**: Enabled for keyword search
- **Hybrid Search**: RRF fusion of vector and full-text results

### Research Memory (PowerContext Concepts)
- Memories stored in seekdb with structured metadata
- Types: conclusion, decision, plan, failure, general
- Project isolation via metadata filtering
- Semantic search for context recovery
- Persistent across sessions

## Project Structure

```
labtrail/
├── frontend/              # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/    # Layout, shared components
│   │   └── pages/         # Dashboard, Library, Search, etc.
│   └── package.json
├── backend/               # Python FastAPI
│   ├── app/
│   │   ├── api/           # Route handlers
│   │   ├── ingestion/     # Document parsing (PDF, MD, CSV)
│   │   ├── experiments/   # Experiment data processing
│   │   ├── reports/       # Weekly report generation
│   │   ├── config.py      # Configuration
│   │   ├── main.py        # FastAPI application
│   │   ├── seekdb_service.py      # seekdb integration
│   │   ├── powercontext_service.py # Memory management
│   │   ├── embedding_service.py   # Local embeddings
│   │   └── project_service.py     # Project CRUD
│   └── requirements.txt
├── demo-data/             # Sample research data
│   ├── research_notes.md
│   └── experiments.csv
├── scripts/
│   └── load_demo_data.py  # Demo data loader
├── docs/                  # Documentation
├── docker-compose.yml     # Docker deployment
├── .env.example           # Environment template
└── README.md
```

## API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `GET /api/projects/{id}/dashboard` - Get dashboard stats

### Documents
- `POST /api/documents/upload` - Upload and index document
- `GET /api/documents/{project_id}` - List documents
- `POST /api/documents/search` - Search documents (hybrid/vector/fulltext)
- `DELETE /api/documents/{project_id}/{doc_id}` - Delete document

### Experiments
- `POST /api/experiments/upload` - Upload experiment CSV
- `GET /api/experiments/{project_id}` - Get experiment analysis
- `GET /api/experiments/{project_id}/recall-qps` - Get Recall-QPS data

### Memory
- `POST /api/memory` - Save research memory
- `GET /api/memory/{project_id}` - List memories
- `POST /api/memory/search` - Search memories
- `GET /api/memory/{project_id}/context` - Get research context

### Reports
- `POST /api/reports/weekly` - Generate weekly report

## Testing

### Run Backend Tests
```bash
source venv/bin/activate
cd backend
PYTHONPATH=. pytest tests/
```

### Manual Verification
1. Start backend and frontend
2. Load demo data
3. Test each scenario from the Demo section
4. Verify search results include source documents
5. Verify experiment charts show real data
6. Verify memory persists across page reloads

## Known Limitations

- seekdb embedded mode does not support namespaces (requires LakeBase cloud); project isolation uses metadata filtering
- PowerContext v1.4.1+ requires server deployment; research memory uses seekdb storage with PowerContext concepts
- PDF parsing extracts text only (no image/table understanding)
- LLM-enhanced report generation requires user-provided API key
- Demo experiment data is synthetic and clearly marked

## Security

- API keys are never stored in frontend or committed to git
- File uploads are size-limited (50MB) and format-validated
- Project data is isolated by project_id
- No sensitive credentials in demo data

## License

This project is developed for the OceanBase Database Competition Qoder Track.

## Acknowledgments

- [seekdb](https://github.com/oceanbase/seekdb) - OceanBase's AI-native hybrid search database
- [PowerContext](https://github.com/oceanbase/powercontext) - OceanBase's context management framework
- [Qoder](https://qoder.com) - AI-powered development platform
- [sentence-transformers](https://www.sbert.net/) - Local embedding models

## Links

- **Live Demo**: [Qoder Sites URL] (to be updated after deployment)
- **Source Code**: [GitHub Repository URL]
- **Competition**: OceanBase Database Competition - Qoder Track
