"""Research weekly report generator."""
import logging
from datetime import datetime, timedelta
from typing import Any

from app.seekdb_service import search_documents, get_document_count
from app.powercontext_service import get_project_memories

logger = logging.getLogger(__name__)


def generate_weekly_report(
    project_id: str,
    project_name: str,
    experiment_data: dict[str, Any] | None = None,
    recent_activities: list[dict] | None = None,
    tasks: list[dict] | None = None,
    llm_api_key: str | None = None,
    llm_base_url: str | None = None,
    llm_model: str | None = None,
) -> str:
    today = datetime.now()
    week_start = today - timedelta(days=7)
    week_str = week_start.strftime("%Y-%m-%d") + " ~ " + today.strftime("%Y-%m-%d")

    memories = get_project_memories(project_id)
    conclusions = [m for m in memories if m.get("metadata", {}).get("memory_type") == "conclusion"]
    decisions = [m for m in memories if m.get("metadata", {}).get("memory_type") == "decision"]
    plans = [m for m in memories if m.get("metadata", {}).get("memory_type") == "plan"]
    failures = [m for m in memories if m.get("metadata", {}).get("memory_type") == "failure"]

    if llm_api_key:
        return _generate_with_llm(
            project_name, week_str, experiment_data, recent_activities,
            tasks, conclusions, decisions, plans, failures,
            llm_api_key, llm_base_url, llm_model,
        )
    return _generate_template_report(
        project_name, week_str, experiment_data, recent_activities,
        tasks, conclusions, decisions, plans, failures,
    )


def _generate_template_report(
    project_name: str,
    week_str: str,
    experiment_data: dict | None,
    recent_activities: list[dict] | None,
    tasks: list[dict] | None,
    conclusions: list[dict],
    decisions: list[dict],
    plans: list[dict],
    failures: list[dict],
) -> str:
    lines = []
    lines.append(f"# Research Weekly Report")
    lines.append(f"")
    lines.append(f"**Project**: {project_name}")
    lines.append(f"**Period**: {week_str}")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"")

    lines.append(f"## 1. Research Goals This Week")
    lines.append(f"")
    if plans:
        for p in plans[:5]:
            lines.append(f"- {p['content']}")
    else:
        lines.append(f"- *No specific goals recorded for this period*")
    lines.append(f"")

    lines.append(f"## 2. Literature & Reading Discoveries")
    lines.append(f"")
    if recent_activities:
        docs = [a for a in recent_activities if a.get("type") == "document"]
        if docs:
            for d in docs[:10]:
                lines.append(f"- {d.get('name', 'Unknown document')} ({d.get('date', '')})")
        else:
            lines.append(f"- *No new documents added this week*")
    else:
        lines.append(f"- *No recent activity data available*")
    lines.append(f"")

    lines.append(f"## 3. Experiment Progress")
    lines.append(f"")
    if experiment_data and experiment_data.get("total_records", 0) > 0:
        lines.append(f"Total experiment records: {experiment_data['total_records']}")
        lines.append(f"Methods tested: {', '.join(experiment_data.get('methods', []))}")
        lines.append(f"Datasets used: {', '.join(experiment_data.get('datasets', []))}")
        lines.append(f"")
        lines.append(f"### Key Results")
        summary = experiment_data.get("summary", {})
        for method, metrics in summary.items():
            lines.append(f"")
            lines.append(f"**{method}**:")
            for metric_name, stats in metrics.items():
                lines.append(f"- {metric_name}: mean={stats['mean']:.4f}, min={stats['min']:.4f}, max={stats['max']:.4f}")
    else:
        lines.append(f"- *No experiment data recorded this week*")
    lines.append(f"")

    lines.append(f"## 4. Main Experimental Results")
    lines.append(f"")
    if experiment_data and experiment_data.get("records"):
        records = experiment_data["records"][:20]
        lines.append(f"| Method | Dataset | Metric | Value |")
        lines.append(f"|--------|---------|--------|-------|")
        for r in records:
            lines.append(f"| {r['method']} | {r['dataset']} | {r['metric_name']} | {r['metric_value']:.4f} |")
    else:
        lines.append(f"- *No results to report*")
    lines.append(f"")

    lines.append(f"## 5. Current Issues & Failed Attempts")
    lines.append(f"")
    if failures:
        for f in failures[:5]:
            lines.append(f"- {f['content']}")
    else:
        lines.append(f"- *No failures recorded*")
    lines.append(f"")

    lines.append(f"## 6. Confirmed Research Conclusions")
    lines.append(f"")
    if conclusions:
        for c in conclusions[:5]:
            lines.append(f"- {c['content']}")
    else:
        lines.append(f"- *No conclusions confirmed this week*")
    lines.append(f"")

    lines.append(f"## 7. Next Week Research Plan")
    lines.append(f"")
    week_plans = [m for m in plans if m.get("metadata", {}).get("memory_type") == "plan"]
    if week_plans:
        for p in week_plans[:5]:
            lines.append(f"- {p['content']}")
    else:
        lines.append(f"- *No plans recorded yet*")
    lines.append(f"")

    lines.append(f"## 8. Key Decisions Made")
    lines.append(f"")
    if decisions:
        for d in decisions[:5]:
            lines.append(f"- {d['content']}")
    else:
        lines.append(f"- *No key decisions recorded*")
    lines.append(f"")

    lines.append(f"## 9. Sources")
    lines.append(f"")
    lines.append(f"- Data sourced from seekdb document store and PowerContext research memory")
    lines.append(f"- All experiment metrics traceable to original CSV records")
    lines.append(f"- Report generated by LabTrail Weekly Report Generator")

    return "\n".join(lines)


def _generate_with_llm(
    project_name: str,
    week_str: str,
    experiment_data: dict | None,
    recent_activities: list[dict] | None,
    tasks: list[dict] | None,
    conclusions: list[dict],
    decisions: list[dict],
    plans: list[dict],
    failures: list[dict],
    api_key: str,
    base_url: str | None,
    model: str | None,
) -> str:
    try:
        import httpx

        context = f"Project: {project_name}\nPeriod: {week_str}\n"
        if conclusions:
            context += "\nConclusions:\n" + "\n".join(f"- {c['content']}" for c in conclusions[:5])
        if decisions:
            context += "\nDecisions:\n" + "\n".join(f"- {d['content']}" for d in decisions[:5])
        if plans:
            context += "\nPlans:\n" + "\n".join(f"- {p['content']}" for p in plans[:5])
        if failures:
            context += "\nFailures:\n" + "\n".join(f"- {f['content']}" for f in failures[:5])
        if experiment_data:
            context += f"\nExperiments: {experiment_data.get('total_records', 0)} records"

        prompt = f"""Generate a research weekly report for the following project.
Use the provided data to fill in each section. If data is missing for a section, note it as unavailable.

{context}

Output the report in Markdown with these sections:
1. Research Goals This Week
2. Literature & Reading Discoveries
3. Experiment Progress
4. Main Experimental Results
5. Current Issues & Failed Attempts
6. Confirmed Research Conclusions
7. Next Week Research Plan
8. Sources"""

        client = httpx.Client(timeout=60)
        url = (base_url or "https://api.openai.com/v1") + "/chat/completions"
        resp = client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model or "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error("LLM report generation failed, falling back to template: %s", e)
        return _generate_template_report(
            project_name, week_str, experiment_data, recent_activities,
            tasks, conclusions, decisions, plans, failures,
        )
