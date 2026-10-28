"""Load demo data into seekdb and PowerContext for the Graph-based ANN Search project."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from app.config import DATA_DIR
from app.project_service import create_project, add_document_record, add_experiment_records
from app.seekdb_service import add_document_chunks
from app.powercontext_service import save_research_memory
from app.experiments.service import parse_experiment_csv

DEMO_PROJECT_ID = "demo_project"
DEMO_PROJECT_NAME = "Graph-based Approximate Nearest Neighbor Search"

PAPER_NOTES = [
    {
        "text": "HNSW (Hierarchical Navigable Small World) graphs achieve state-of-the-art performance for approximate nearest neighbor search. The algorithm builds a multi-layered proximity graph where upper layers provide logarithmic-scale navigation shortcuts and lower layers contain all data points for fine-grained search. Search complexity is O(log N) with high probability. Key parameters include M (maximum number of connections per element per layer), ef_construction (size of the dynamic candidate list during construction), and ef_search (size of the dynamic candidate list during search). The hierarchical structure enables efficient navigation even in high-dimensional spaces.",
        "metadata": {"file_name": "hnsw_paper_notes.md", "file_type": "markdown", "page": 1, "source": "Malkov & Yashunin, 2018 - Efficient and robust approximate nearest neighbor search using HNSW graphs"},
    },
    {
        "text": "Vamana (also known as DiskANN) is a graph-based ANN algorithm that builds a bounded-degree graph using alpha-relative neighborhood graph (alpha-RNG) pruning. Unlike HNSW's hierarchical approach, Vamana uses a single-layer graph with controlled connectivity. The pruning parameter alpha (typically 1.0-1.2) controls the tradeoff between graph quality and degree constraints. When alpha=1, the algorithm produces a standard RNG; alpha>1 allows longer edges that improve search recall at the cost of higher degree. Vamana supports both in-memory and disk-based indexing, making it suitable for billion-scale datasets.",
        "metadata": {"file_name": "vamana_paper_notes.md", "file_type": "markdown", "page": 1, "source": "Subramanya et al., 2019 - DiskANN: Fast accurate billion-point nearest neighbor search on a single node"},
    },
    {
        "text": "Out-of-Distribution (OOD) queries present a significant challenge for graph-based ANN indices. When the query distribution differs from the data distribution used during index construction, search recall degrades because the graph topology was optimized for in-distribution routing. The greedy search strategy may encounter more local minima when navigating to OOD query points. This effect is more pronounced in high-dimensional spaces where the curse of dimensionality amplifies distribution differences. Research shows that HNSW can lose 10-15% recall on OOD queries compared to in-distribution queries of similar difficulty.",
        "metadata": {"file_name": "ood_analysis_notes.md", "file_type": "markdown", "page": 1, "source": "Research analysis on OOD query patterns in graph indices"},
    },
    {
        "text": "Query distribution-aware graph construction modifies the standard index building process to account for the expected query distribution. By sampling representative queries during construction, the algorithm can create graph connections that improve routing for both in-distribution and OOD queries. Techniques include: (1) adding virtual query points during graph construction, (2) modifying the pruning criteria to maintain edges useful for query routing, (3) using bi-direction edges that consider both data and query neighborhoods. Experiments show 5-15% recall improvement on OOD benchmarks with moderate increase in construction time.",
        "metadata": {"file_name": "query_aware_construction.md", "file_type": "markdown", "page": 1, "source": "Research notes on distribution-aware indexing strategies"},
    },
    {
        "text": "The Recall-QPS tradeoff is the primary evaluation metric for ANN search algorithms. Higher recall typically requires more computational work per query (larger search lists, more graph traversals), reducing throughput (QPS). The Pareto frontier of recall vs QPS characterizes algorithm efficiency. For practical systems, the target is often recall@10 > 0.95 with QPS > 10000 for million-scale datasets. Memory consumption is another critical factor: graph-based methods require O(N*M) memory for the graph structure, where N is the dataset size and M is the average degree.",
        "metadata": {"file_name": "evaluation_metrics.md", "file_type": "markdown", "page": 1, "source": "ANN benchmark methodology documentation"},
    },
    {
        "text": "Index build time varies significantly between graph-based algorithms. HNSW construction is O(N*log(N)) due to the multi-layer structure, while Vamana's single-layer construction is O(N*R*L) where R is the max degree and L is the search list size used during construction. In practice, Vamana can be faster for moderate-dimensional data because it avoids the overhead of maintaining multiple graph layers. However, HNSW's construction is more predictable and less sensitive to parameter choices. Peak memory during construction can be 2-3x the final index size due to temporary data structures.",
        "metadata": {"file_name": "build_time_analysis.md", "file_type": "markdown", "page": 1, "source": "Comparative analysis of graph index construction costs"},
    },
    {
        "text": "SIFT-128-euclidean is a standard benchmark dataset for ANN search evaluation. It contains 1 million 128-dimensional vectors extracted from image descriptors, with Euclidean distance as the similarity metric. The dataset has relatively low intrinsic dimensionality and well-behaved distance distributions, making it suitable for evaluating basic algorithm performance. The OOD variant (sift-128-euclidean-ood) uses queries sampled from a shifted distribution to test robustness.",
        "metadata": {"file_name": "dataset_descriptions.md", "file_type": "markdown", "page": 1, "source": "ANN benchmarks dataset documentation"},
    },
    {
        "text": "GloVe-200-angular is a benchmark dataset based on GloVe word embeddings with 200 dimensions and angular (cosine) distance. It represents a more challenging scenario than SIFT due to higher dimensionality and non-uniform data distribution. Word embeddings exhibit clustering behavior with dense regions corresponding to semantic categories. This makes ANN search harder because many points have similar distances to queries, increasing the chance of false negatives in greedy search. The OOD variant simulates queries from a different semantic domain.",
        "metadata": {"file_name": "dataset_descriptions.md", "file_type": "markdown", "page": 2, "source": "ANN benchmarks dataset documentation"},
    },
]

RESEARCH_MEMORIES = [
    ("Current research focus: understanding how OOD query distributions affect graph-based ANN index performance. We hypothesize that query distribution-aware construction can significantly improve OOD recall.", "conclusion", ["OOD", "graph-index", "hypothesis"]),
    ("Decision: Prioritize Vamana over HNSW for OOD scenarios based on initial experiments showing 4-5% better recall on OOD benchmarks with comparable QPS.", "decision", ["Vamana", "HNSW", "OOD", "comparison"]),
    ("Failed approach: Adding random long-range edges to HNSW graph did not improve OOD recall significantly (< 1% improvement) while degrading in-distribution performance by 3%. The random edges introduced noise in the navigation structure.", "failure", ["HNSW", "random-edges", "failed"]),
    ("Next experiment plan: Test query distribution-aware graph construction on both HNSW and Vamana using the SIFT-128-OOD dataset. Compare recall improvement vs construction time overhead.", "plan", ["experiment", "query-aware", "SIFT"]),
    ("Key finding: The alpha parameter in Vamana's pruning strategy has a significant impact on OOD performance. Alpha=1.2 provides the best tradeoff between in-distribution and OOD recall for our test datasets.", "conclusion", ["Vamana", "alpha", "parameter-tuning"]),
    ("Research direction: Investigate whether combining HNSW's hierarchical structure with Vamana's alpha-pruning can create a hybrid index that handles OOD queries better than either method alone.", "plan", ["hybrid", "future-work"]),
]


def load_demo_data():
    print("Loading demo data for LabTrail...")

    project = create_project(
        name=DEMO_PROJECT_NAME,
        description="Research on graph-based indexing methods for Approximate Nearest Neighbor search, focusing on OOD query robustness and distribution-aware construction.",
        research_direction="Graph-based ANN search, OOD robustness, query distribution-aware indexing",
        goal="Understand and mitigate OOD performance degradation in graph-based ANN indices",
    )
    project_id = DEMO_PROJECT_ID
    from app.project_service import _load_json, _save_json, PROJECTS_FILE
    projects = _load_json(PROJECTS_FILE, {})
    if project["id"] != project_id:
        projects[project_id] = projects.pop(project["id"])
        projects[project_id]["id"] = project_id
        _save_json(PROJECTS_FILE, projects)
    print(f"  Created project: {DEMO_PROJECT_NAME}")

    print("  Loading research notes into seekdb...")
    for i, note in enumerate(PAPER_NOTES):
        doc_id = f"demo_doc_{i:03d}"
        chunks = [{
            "text": note["text"],
            "metadata": {**note["metadata"], "doc_id": doc_id, "project_id": project_id},
        }]
        add_document_chunks(project_id, doc_id, chunks)
        add_document_record(project_id, note["metadata"]["file_name"], ".md", f"demo://{doc_id}", 1)
    print(f"  Loaded {len(PAPER_NOTES)} research notes")

    print("  Loading experiment data...")
    csv_path = Path(__file__).parent.parent / "demo-data" / "experiments.csv"
    records = parse_experiment_csv(str(csv_path), project_id)
    add_experiment_records(project_id, records)
    print(f"  Loaded {len(records)} experiment records")

    print("  Saving research memories to PowerContext...")
    for content, memory_type, tags in RESEARCH_MEMORIES:
        save_research_memory(project_id, content, memory_type, tags)
    print(f"  Saved {len(RESEARCH_MEMORIES)} research memories")

    print("Demo data loading complete!")
    print(f"  Project ID: {project_id}")
    print(f"  Documents: {len(PAPER_NOTES)}")
    print(f"  Experiments: {len(records)}")
    print(f"  Memories: {len(RESEARCH_MEMORIES)}")


if __name__ == "__main__":
    load_demo_data()
