# Graph-based Approximate Nearest Neighbor Search

## Research Direction

This project investigates graph-based indexing methods for Approximate Nearest Neighbor (ANN) search, with a focus on understanding how Out-of-Distribution (OOD) query patterns affect search performance and how to build more robust graph indices.

## Background

Approximate Nearest Neighbor search is a fundamental problem in information retrieval, machine learning, and database systems. Given a query point, the goal is to find the closest point(s) in a large dataset approximately, trading off a small amount of accuracy for significant speedup.

Graph-based methods have emerged as one of the most effective approaches for ANN search, achieving state-of-the-art recall-performance tradeoffs. Key algorithms include:

### HNSW (Hierarchical Navigable Small World)

HNSW builds a multi-layered graph where upper layers provide coarse navigation and lower layers enable fine-grained search. The algorithm achieves O(log N) search complexity with high recall.

Key properties:
- Hierarchical structure with navigable small world graphs at each level
- Construction time: O(N log N) where N is the dataset size
- Search time: O(log N) per query with high probability
- Memory overhead: O(N log N) for the multi-layer graph structure
- Parameters: M (max connections per node), ef_construction (construction quality), ef_search (search quality)

### Vamana (DiskANN)

Vamana is a graph-based ANN algorithm designed for both in-memory and disk-based scenarios. It uses a modified greedy routing strategy with bounded-degree graphs.

Key properties:
- Single-layer graph with bounded degree (R parameter)
- Uses α-RNG (alpha-relative neighborhood graph) pruning for better routing
- Supports disk-based indexing with SSD-friendly I/O patterns
- Construction involves iterative graph improvement
- Parameters: R (max degree), L (search list size), α (pruning parameter, typically 1.0-1.2)

### OOD Query Distribution Problem

A critical challenge in graph-based ANN search is the performance degradation when query distributions differ from the data distribution used during index construction. This is known as the Out-of-Distribution (OOD) problem.

When queries come from a different distribution than the indexed data:
1. Graph connectivity may be suboptimal for routing OOD queries
2. Greedy search may get trapped in local minima more frequently
3. Recall degrades significantly, especially for high-dimensional data
4. The gap between base and query distributions directly impacts performance

Research has shown that standard graph construction algorithms optimize for in-distribution performance and may create graph structures that are fragile to distribution shifts.

## Research Questions

1. How does the divergence between base and query distributions affect graph index quality?
2. Can we design graph construction algorithms that are aware of query distributions?
3. What is the tradeoff between construction cost and OOD robustness?
4. How do different graph topologies (HNSW vs Vamana) handle distribution shift?

## Key Findings So Far

- Vamana shows better OOD robustness than HNSW for moderate distribution shifts
- Query distribution-aware graph construction can improve recall by 5-15% on OOD queries
- The α parameter in Vamana's pruning strategy significantly affects OOD performance
- Higher-dimensional datasets are more sensitive to distribution shift

## Notes

- All experiment data in the demo is synthetic and marked as such
- Paper references are to publicly available preprints and published works
- The focus is on demonstrating the LabTrail research workflow
