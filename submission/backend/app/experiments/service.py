"""Experiment data service: CSV import, normalization, analysis."""
import csv
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["experiment_id", "project_id", "method", "dataset", "timestamp", "metric_name", "metric_value"]

STANDARD_METRICS = {
    "recall@k", "recall@1", "recall@5", "recall@10", "recall@100",
    "qps", "queries_per_second",
    "index_build_time", "build_time",
    "peak_memory", "rss", "memory_mb", "memory",
    "update_throughput", "throughput",
    "latency", "latency_ms", "latency_p99", "search_latency",
}


def parse_experiment_csv(file_path: str, project_id: str) -> list[dict[str, Any]]:
    text = Path(file_path).read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise ValueError("CSV file is empty")

    headers = list(rows[0].keys())
    return _normalize_rows(rows, headers, project_id)


def _normalize_rows(
    rows: list[dict], headers: list[str], project_id: str
) -> list[dict[str, Any]]:
    normalized = []
    field_map = _build_field_map(headers)

    for i, row in enumerate(rows):
        try:
            record = _map_row(row, field_map, project_id, i)
            if record:
                normalized.append(record)
        except Exception as e:
            logger.warning("Skipping row %d: %s", i, e)
    return normalized


def _build_field_map(headers: list[str]) -> dict[str, str]:
    mapping = {}
    lower_headers = {h: h.lower().strip().replace(" ", "_") for h in headers}
    for orig, norm in lower_headers.items():
        if norm in REQUIRED_FIELDS:
            mapping[norm] = orig
        elif norm == "parameters" or norm == "params" or norm == "config":
            mapping["parameters"] = orig
    return mapping


def _map_row(
    row: dict, field_map: dict, project_id: str, row_idx: int
) -> dict[str, Any] | None:
    try:
        exp_id = row.get(field_map.get("experiment_id", ""), "")
        if not exp_id:
            exp_id = f"auto_{row_idx}"

        method = row.get(field_map.get("method", ""), "")
        dataset = row.get(field_map.get("dataset", ""), "")
        if not method or not dataset:
            return None

        timestamp = row.get(field_map.get("timestamp", ""), "")
        if not timestamp:
            timestamp = datetime.now().isoformat()

        metric_name = row.get(field_map.get("metric_name", ""), "")
        metric_value_str = row.get(field_map.get("metric_value", ""), "")

        try:
            metric_value = float(metric_value_str)
        except (ValueError, TypeError):
            return None

        parameters_str = row.get(field_map.get("parameters", ""), "{}")
        try:
            parameters = json.loads(parameters_str) if parameters_str else {}
        except json.JSONDecodeError:
            parameters = {"raw": parameters_str}

        return {
            "experiment_id": exp_id,
            "project_id": project_id,
            "method": method,
            "dataset": dataset,
            "timestamp": timestamp,
            "metric_name": metric_name.lower().strip(),
            "metric_value": metric_value,
            "parameters": parameters,
        }
    except Exception as e:
        logger.warning("Error mapping row %d: %s", row_idx, e)
        return None


def parse_wide_format_csv(file_path: str, project_id: str) -> list[dict[str, Any]]:
    df = pd.read_csv(file_path)
    records = []
    id_cols = [c for c in df.columns if c.lower() in ("experiment_id", "method", "dataset", "timestamp")]
    metric_cols = [c for c in df.columns if c.lower() not in [ic.lower() for ic in id_cols]]

    for _, row in df.iterrows():
        base = {}
        for ic in id_cols:
            base[ic.lower()] = str(row.get(ic, ""))
        base.setdefault("experiment_id", f"auto_{len(records)}")
        base.setdefault("project_id", project_id)
        base.setdefault("timestamp", datetime.now().isoformat())

        for mc in metric_cols:
            val = row.get(mc)
            if pd.isna(val):
                continue
            try:
                records.append({
                    "experiment_id": base["experiment_id"],
                    "project_id": project_id,
                    "method": base.get("method", ""),
                    "dataset": base.get("dataset", ""),
                    "timestamp": base.get("timestamp", ""),
                    "metric_name": mc.lower().strip(),
                    "metric_value": float(val),
                    "parameters": {},
                })
            except (ValueError, TypeError):
                continue
    return records


def analyze_experiments(
    records: list[dict[str, Any]],
    filter_method: str | None = None,
    filter_dataset: str | None = None,
    filter_metric: str | None = None,
) -> dict[str, Any]:
    if filter_method:
        records = [r for r in records if r["method"] == filter_method]
    if filter_dataset:
        records = [r for r in records if r["dataset"] == filter_dataset]
    if filter_metric:
        records = [r for r in records if r["metric_name"] == filter_metric]

    methods = sorted(set(r["method"] for r in records))
    datasets = sorted(set(r["dataset"] for r in records))
    metrics = sorted(set(r["metric_name"] for r in records))

    summary = {}
    for method in methods:
        method_records = [r for r in records if r["method"] == method]
        summary[method] = {}
        for metric in metrics:
            metric_records = [r for r in method_records if r["metric_name"] == metric]
            if metric_records:
                values = [r["metric_value"] for r in metric_records]
                summary[method][metric] = {
                    "count": len(values),
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "values": values,
                }

    return {
        "total_records": len(records),
        "methods": methods,
        "datasets": datasets,
        "metrics": metrics,
        "summary": summary,
        "records": records,
    }


def get_recall_qps_data(records: list[dict[str, Any]]) -> dict[str, list[dict]]:
    result = {}
    methods = sorted(set(r["method"] for r in records))
    for method in methods:
        method_records = [r for r in records if r["method"] == method]
        recall_records = [r for r in method_records if "recall" in r["metric_name"]]
        qps_records = [r for r in method_records if r["metric_name"] in ("qps", "queries_per_second")]

        points = []
        for rr in recall_records:
            matching_qps = [q for q in qps_records if q.get("dataset") == rr.get("dataset")]
            if matching_qps:
                points.append({
                    "recall": rr["metric_value"],
                    "qps": matching_qps[0]["metric_value"],
                    "dataset": rr.get("dataset", ""),
                })
        if points:
            result[method] = sorted(points, key=lambda p: p["recall"])
    return result
