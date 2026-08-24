"""Orchestration: ask, score, aggregate."""

from __future__ import annotations

import importlib.resources as resources
from collections import defaultdict

import yaml

from . import markers
from .judge import classify


def load(name: str):
    with resources.files("sixdialects.data").joinpath(name).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_dialects() -> dict:
    return load("dialects.yaml")


def load_scenarios(path: str | None = None) -> list:
    if path:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    return load("scenarios.yaml")


def probe(target, scenarios, dialects, judge=None, on_event=None) -> dict:
    rows = []

    for scenario in scenarios:
        if on_event:
            on_event(scenario["id"])

        answer = target.chat(scenario["prompt"].strip())
        m_scores = markers.score(answer, dialects)
        m_primary, m_share = markers.primary(m_scores)

        row = {
            "id": scenario["id"],
            "domain": scenario.get("domain", ""),
            "prompt": scenario["prompt"].strip(),
            "answer": answer,
            "marker_scores": {d: round(v["score"], 4) for d, v in m_scores.items()},
            "marker_evidence": {d: v["hits"] for d, v in m_scores.items() if v["hits"]},
            "marker_primary": m_primary,
            "marker_share": round(m_share, 3),
        }

        if judge is not None:
            verdict = classify(judge, scenario["prompt"], answer, dialects)
            row["judge_primary"] = verdict.get("primary")
            row["judge_secondary"] = verdict.get("secondary")
            row["judge_confidence"] = verdict.get("confidence")
            row["judge_evidence"] = verdict.get("evidence", [])
            row["judge_reason"] = verdict.get("reason", "")
            row["agreement"] = (
                row["judge_primary"] == row["marker_primary"]
                if row["judge_primary"] not in (None, "none")
                else None
            )

        rows.append(row)

    return {
        "profile_markers": markers.aggregate(rows),
        "profile_judge": _judge_profile(rows),
        "agreement_rate": _agreement(rows),
        "scenarios": rows,
    }


def _judge_profile(rows) -> dict:
    counts = defaultdict(int)
    counted = 0
    for row in rows:
        did = row.get("judge_primary")
        if did and did != "none":
            counts[did] += 1
            counted += 1
    return {d: c / counted for d, c in counts.items()} if counted else {}


def _agreement(rows) -> float | None:
    values = [r["agreement"] for r in rows if r.get("agreement") is not None]
    return sum(values) / len(values) if values else None
