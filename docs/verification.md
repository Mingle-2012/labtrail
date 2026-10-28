# Verification Guide

This document provides reproducible verification scenarios for the three core features of LabTrail.

## Scenario A: Research Knowledge Retrieval (seekdb)

### Initial State
- Demo project loaded with 8 research notes about Graph-based ANN Search
- seekdb contains document chunks with vector and full-text indices

### Steps
1. Start the backend server
2. Send a search request:
```bash
curl -X POST "http://localhost:8000/api/documents/search?project_id=demo_project" \
  -H "Content-Type: application/json" \
  -d '{"query": "Why does OOD query distribution degrade graph index performance?", "mode": "hybrid", "n_results": 5}'
```

### Expected Output
- Results contain relevant text chunks about OOD queries and graph indices
- Each result includes:
  - `text`: The matching document chunk
  - `metadata.file_name`: Source document name (e.g., "ood_analysis_notes.md")
  - `metadata.source`: Original paper/note reference
  - `score`: Relevance score from RRF fusion
  - `fusion: true`: Indicates hybrid search was used

### seekdb Evidence
The search uses:
1. IVF vector index for semantic similarity
2. Full-text index for keyword matching
3. RRF fusion to combine results

## Scenario B: Research Memory Recovery (PowerContext Concepts)

### Initial State
- Demo project has 6 saved research memories

### Steps

**Step 1: View existing memories**
```bash
curl "http://localhost:8000/api/memory/demo_project"
```

**Step 2: Save a new memory**
```bash
curl -X POST "http://localhost:8000/api/memory" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "demo_project",
    "content": "Remember: Current priority is optimizing OOD-aware graph construction. Do not research quantization compression until OOD experiments are complete.",
    "memory_type": "decision",
    "tags": ["OOD", "priority", "decision"]
  }'
```

**Step 3: Simulate new session - recover context**
```bash
curl "http://localhost:8000/api/memory/demo_project/context"
```

### Expected Output
- The context endpoint returns all saved memories including the newly saved one
- Memories are grouped by type (conclusion, decision, plan, failure)
- The new decision about OOD priority is included

**Step 4: Search memories**
```bash
curl -X POST "http://localhost:8000/api/memory/search" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "demo_project", "query": "What should we prioritize?", "n_results": 3}'
```

### PowerContext Evidence
- Memories persist in seekdb with structured metadata
- Project isolation via project_id filtering
- Semantic search over memory content
- Cross-session recovery demonstrated by context endpoint

## Scenario C: Experiment Analysis & Weekly Report

### Initial State
- Demo project has 30 experiment records from experiments.csv
- Data includes HNSW and Vamana methods across 4 datasets

### Steps

**Step 1: View experiment analysis**
```bash
curl "http://localhost:8000/api/experiments/demo_project"
```

### Expected Output
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

**Step 2: Generate weekly report**
```bash
curl -X POST "http://localhost:8000/api/reports/weekly" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "demo_project"}'
```

### Expected Output
- Structured Markdown report with 9 sections
- All experiment numbers match the raw CSV data
- Research memories are included in conclusions and decisions sections
- Sources section confirms data traceability

### Data Traceability Evidence
- Report numbers can be verified against `demo-data/experiments.csv`
- Each experiment record has an `experiment_id` linking to original data
- Memory content matches saved research conclusions

## Automated Test Script

```bash
#!/bin/bash
# Run all verification scenarios

BASE_URL="http://localhost:8000"
PROJECT_ID="demo_project"

echo "=== Health Check ==="
curl -s "$BASE_URL/api/health" | python3 -m json.tool

echo -e "\n=== Scenario A: Search ==="
curl -s -X POST "$BASE_URL/api/documents/search?project_id=$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{"query": "OOD query distribution", "mode": "hybrid", "n_results": 3}' | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Results: {d[\"count\"]}, Mode: {d[\"mode\"]}')"

echo -e "\n=== Scenario B: Memory ==="
curl -s "$BASE_URL/api/memory/$PROJECT_ID" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Memories: {len(d)}')"

echo -e "\n=== Scenario C: Experiments ==="
curl -s "$BASE_URL/api/experiments/$PROJECT_ID" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Records: {d[\"total_records\"]}, Methods: {d[\"methods\"]}')"

echo -e "\n=== Report Generation ==="
curl -s -X POST "$BASE_URL/api/reports/weekly" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\"}" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Report length: {len(d[\"report\"])} chars')"

echo -e "\n=== All scenarios verified ==="
```
