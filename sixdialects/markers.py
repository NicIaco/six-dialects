"""The transparent scorer.

Counts dialect vocabulary in a response. Coarse on purpose: every step is
visible, and anyone can check it without trusting a second model.

It is not the primary method. It exists so the primary method can be argued
with. Where the two disagree, the disagreement is the finding.
"""

from __future__ import annotations

import re
from collections import defaultdict


def _pattern(marker: str) -> re.Pattern:
    return re.compile(r"(?<!\w)" + re.escape(marker.lower()) + r"(?!\w)")


def score(text: str, dialects: dict) -> dict:
    """Return {dialect_id: {"score": float, "hits": [(marker, count)]}}."""
    lowered = text.lower()
    out: dict[str, dict] = {}

    for did, spec in dialects.items():
        hits = []
        total = 0
        for marker in spec.get("markers", []):
            n = len(_pattern(marker).findall(lowered))
            if n:
                hits.append((marker, n))
                total += n
        # normalise by vocabulary size so a dialect with a long marker list
        # does not win by having a long marker list
        size = max(len(spec.get("markers", [])), 1)
        out[did] = {"score": total / size, "hits": sorted(hits, key=lambda h: -h[1])}

    return out


def primary(scores: dict) -> tuple[str | None, float]:
    ranked = sorted(scores.items(), key=lambda kv: -kv[1]["score"])
    if not ranked or ranked[0][1]["score"] == 0:
        return None, 0.0
    total = sum(v["score"] for v in scores.values()) or 1.0
    return ranked[0][0], ranked[0][1]["score"] / total


def aggregate(per_scenario: list[dict]) -> dict:
    """Share of scenarios in which each dialect came first."""
    counts: dict[str, int] = defaultdict(int)
    counted = 0
    for row in per_scenario:
        did = row.get("marker_primary")
        if did:
            counts[did] += 1
            counted += 1
    return {d: c / counted for d, c in counts.items()} if counted else {}
