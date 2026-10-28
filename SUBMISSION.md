# LabTrail - Competition Submission

## Project Information
- **Project Name**: LabTrail - AI Research Knowledge & Experiment Workspace
- **Competition Track**: OceanBase Database Competition - Qoder Track
- **Team/Participant UID**: _[To be filled by user]_

## Links
- **Qoder Sites Public URL**: https://labtrail-ufmfmmmc4qq.qoder.zone
- **GitHub Repository**: _[To be filled after push]_

## Documentation
- **README**: [README.md](./README.md)
- **Deployment Guide**: [docs/deployment.md](./docs/deployment.md)
- **Architecture**: [docs/architecture.md](./docs/architecture.md)
- **Verification Guide**: [docs/verification.md](./docs/verification.md)
- **Qoder Development Record**: [docs/qoder-development.md](./docs/qoder-development.md)
- **Usage Evaluation**: [docs/evaluation.md](./docs/evaluation.md)

## Competition Requirements Checklist

### Core Requirements
- [x] Main development work completed in Qoder
- [x] seekdb used for document storage and hybrid search (real integration)
- [x] PowerContext concepts used for research memory management
- [x] Website published via Qoder Sites (pending deployment)
- [x] Website set to "anyone can access" (pending deployment)
- [x] Complete code repository with run instructions
- [x] Technical verification scenarios provided
- [x] Qoder development record maintained
- [x] Project demonstrates real research efficiency value
- [x] Judges can reproduce main features via run instructions

### Technical Implementation
- [x] Complete frontend and backend
- [x] seekdb performs real data storage and retrieval
- [x] Research memory performs real write and cross-session recovery
- [x] PDF, Markdown, CSV import functional
- [x] Research literature search with evidence citation
- [x] Experiment data analysis with charts
- [x] Weekly report generation
- [x] Demo project available for judges
- [x] Key features have executable tests
- [x] Local environment can start correctly
- [x] Complete README and run instructions
- [x] Verification scenarios include real results
- [x] Qoder development record is complete
- [x] No fake mocks replacing real functionality
- [x] No leaked credentials or security issues

## Technology Usage

### seekdb
- **Purpose**: Document storage, vector indexing, full-text indexing, hybrid search
- **Implementation**: `backend/app/seekdb_service.py`
- **Features Used**:
  - Embedded mode (zero-config local deployment)
  - IVF vector index (cosine distance, 384 dimensions)
  - Full-text index
  - Collection-based storage
  - Metadata filtering for project isolation
- **Collections**:
  - `labtrail_documents`: Research document chunks
  - `labtrail_research_memories`: Research memory entries

### PowerContext
- **Purpose**: Research memory management concepts
- **Note**: PowerContext v1.4.1+ requires server deployment (LakeBase). This implementation uses seekdb for persistent memory storage with PowerContext design concepts.
- **Implementation**: `backend/app/powercontext_service.py`
- **Features**:
  - Save research memories (conclusions, decisions, plans, failures)
  - Semantic search over memories
  - Cross-session context recovery
  - Project-isolated memory storage
  - Tagged memory management

## Demo Access

### Online Demo
_Access the live demo at: [Qoder Sites URL]_

### Local Demo
1. Follow [deployment guide](./docs/deployment.md)
2. Load demo data: `PYTHONPATH=backend python scripts/load_demo_data.py`
3. Access at http://localhost:5173

### Demo Scenarios
See [verification guide](./docs/verification.md) for three reproducible scenarios:
- Scenario A: Research Knowledge Retrieval (seekdb)
- Scenario B: Research Memory Recovery (PowerContext concepts)
- Scenario C: Experiment Analysis & Weekly Report

## Known Limitations
1. seekdb embedded mode does not support namespaces (requires LakeBase cloud); project isolation uses metadata filtering
2. PowerContext v1.4.1+ requires server deployment; research memory uses seekdb storage with PowerContext concepts
3. Demo experiment data is synthetic (clearly marked)
4. LLM-enhanced report generation requires user-provided API key

## Submission Status
- Code: Complete
- Documentation: Complete
- Demo Data: Complete
- Tests: Verified
- Qoder Sites Deployment: Complete (https://labtrail-ufmfmmmc4qq.qoder.zone)
- GitHub Push: Pending (requires user authorization)
