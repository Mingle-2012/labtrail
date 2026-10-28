# Architecture Documentation

## System Architecture

LabTrail follows a three-tier architecture:

### Frontend (React + TypeScript + Vite)
- Single Page Application with client-side routing
- Tailwind CSS for responsive design
- Recharts for data visualization
- Communicates with backend via REST API

### Backend (Python + FastAPI)
- RESTful API server
- Document ingestion pipeline (PDF, Markdown, CSV, TXT)
- seekdb integration for storage and retrieval
- Research memory management
- Experiment data analysis
- Report generation

### Data Layer (seekdb)
- Embedded mode for local development
- IVF vector index (dimension 384, cosine distance)
- Full-text index for keyword search
- Multiple collections for different data types

## Data Model

### Documents Collection
```
{
  "id": "doc_id_chunk_hash",
  "text": "chunk content",
  "metadata": {
    "project_id": "string",
    "doc_id": "string",
    "file_name": "string",
    "file_type": "pdf|markdown|csv|text",
    "page": number (for PDF),
    "chunk_index": number,
    "source": "string"
  }
}
```

### Research Memories Collection
```
{
  "id": "mem_xxxx",
  "text": "memory content",
  "metadata": {
    "project_id": "string",
    "memory_type": "conclusion|decision|plan|failure|general",
    "tags": "comma,separated,tags",
    "memory_id": "string"
  }
}
```

### Experiments (JSON file storage)
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

## Search Pipeline

1. User submits query
2. Query text is embedded using sentence-transformers (all-MiniLM-L6-v2)
3. **Vector search**: seekdb IVF index returns top-K by cosine similarity
4. **Full-text search**: seekdb full-text index returns top-K by text match
5. **RRF Fusion**: Results combined using Reciprocal Rank Fusion (k=60)
6. Project filtering applied via metadata
7. Results returned with scores, metadata, and source information

## Memory Pipeline

1. User saves research memory (conclusion, decision, plan, etc.)
2. Memory text is embedded and stored in seekdb
3. Metadata includes project_id, memory_type, and tags
4. For context recovery, all project memories are retrieved
5. For search, semantic similarity is used to find relevant memories
6. Memories persist across sessions via seekdb storage

## Report Generation Pipeline

1. Load project data: documents, experiments, memories
2. Aggregate experiment metrics by method and dataset
3. Retrieve research memories by type (conclusions, decisions, plans, failures)
4. Generate structured report using template
5. Optional: LLM enhancement if API key provided
6. Export as Markdown

## Key Engineering Decisions

### seekdb over other vector databases
- Native hybrid search (vector + fulltext) in one system
- Embedded mode for zero-config local development
- OceanBase ecosystem integration for competition
- IVF index supports namespace-like filtering via metadata

### Local embedding model
- No API key required for core functionality
- all-MiniLM-L6-v2: 384 dimensions, fast inference
- Runs on CPU with ONNX runtime
- Good balance of quality and speed

### JSON file storage for projects/experiments
- Simple, no additional database needed
- seekdb handles the heavy lifting for search
- Easy to backup and migrate
- Suitable for single-user research workspace

### Template-based report generation
- Works without LLM API key
- All numbers traceable to real data
- LLM enhancement is optional
- Deterministic output for reproducibility
