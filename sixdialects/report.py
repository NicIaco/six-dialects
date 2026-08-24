"""Printing. Percentages first, then where the two methods disagreed."""

from __future__ import annotations


def _bar(fraction: float, width: int = 24) -> str:
    filled = round(fraction * width)
    return "█" * filled + "·" * (width - filled)


def _profile(title: str, profile: dict, dialects: dict) -> list[str]:
    if not profile:
        return [title, "  (nothing to report)", ""]
    lines = [title]
    for did, share in sorted(profile.items(), key=lambda kv: -kv[1]):
        name = dialects.get(did, {}).get("name", did)
        lines.append(f"  {name:<12} {_bar(share)} {share*100:5.1f}%")
    lines.append("")
    return lines


def render(result: dict, dialects: dict, model: str) -> str:
    out = ["", f"Six Dialects · {model}", "=" * 52, ""]
    if result.get("profile_judge"):
        out += _profile("Ethical premise the answer starts from (judge)",
                        result["profile_judge"], dialects)
    out += _profile("Dialect vocabulary present (marker count)",
                    result.get("profile_markers", {}), dialects)

    rate = result.get("agreement_rate")
    if rate is not None:
        out.append(f"The two readings coincided on {rate*100:.0f}% of scenarios.")
        out.append("Internal cross-check only. Both come from the same six")
        out.append("definitions, so this is not validation.")
        out.append("")

    unclassified = result.get("unclassified", 0)
    if unclassified:
        out.append(f"{unclassified} scenario(s) the judge would not place in one grammar.")
        out.append("")

    disputed = [r for r in result["scenarios"] if r.get("agreement") is False]
    if disputed:
        out.append("Where they disagreed (read these ones yourself):")
        for row in disputed:
            j = dialects.get(row["judge_primary"], {}).get("name", row["judge_primary"])
            m = dialects.get(row["marker_primary"], {}).get("name", row["marker_primary"])
            out.append(f"  {row['id']:<26} judge: {j:<11} vocabulary: {m}")
        out.append("")

    return "\n".join(out)
