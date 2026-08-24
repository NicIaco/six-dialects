"""The review.

You are building something. This reads it in six grammars and tells you what
each one will assume, what will read as wrong, and the one design decision
that changes between them.

It is not a compliance check and it will not tell you which grammar to pick.
Where two of them contradict each other, that contradiction is a fork in your
design, and you are the one who has to take it.
"""

from __future__ import annotations

import json
import re

SYSTEM = (
    "You read software projects in six ethical grammars. You do not rank the "
    "grammars and you do not tell the builder which one is right. You report "
    "what each one assumes, what will read as wrong inside it, and the "
    "concrete design decision that differs. Be specific to this project. "
    "Generic ethics advice is worse than none. Answer with JSON and nothing else."
)

TEMPLATE = """Six ethical grammars.

{dialects}

Someone is building this:

\"\"\"
{project}
\"\"\"

{context}For each grammar, answer three things about THIS project:

- assumes: what this grammar takes for granted about the situation, in one sentence
- misreads: what in this project would read as wrong or offensive inside this grammar
- decision: one concrete, implementable design decision this grammar implies
  (a default, a flow, a piece of copy, a retention rule, who is asked first)

Constraints. Breaking any of these makes the output worse than nothing:

- Do not invent laws, standards or regulatory caps. If you refer to a rule,
  name it. If you cannot name it, say what the grammar would ask for instead.
- Do not invent specific numbers, thresholds or limits that the project did
  not mention. The grammars differ in what they start from, not in what
  number they pick.
- The design decision must be something this team could implement this week,
  and it must follow from the grammar's premise, not from general product
  sense.
- Do not escalate severity to make a grammar sound distinct. London is not
  the grammar of catastrophe for its own sake; it asks what happens when the
  same default runs a million times.

Then find the places where two grammars contradict each other about this
specific project. Those are forks the builder has to take deliberately.

Finally, name the moment in THIS project where the user stops exercising
their own judgment and lets the system's answer stand. This is not a button
or a screen. It is the point where a person had a decision and no longer has
it, and it is usually earlier and quieter than the confirmation step.

Return JSON exactly in this shape:

{{"readings": [
   {{"dialect": "<id>", "assumes": "...", "misreads": "...", "decision": "..."}}
 ],
 "tensions": [
   {{"between": ["<id>", "<id>"], "about": "<what they disagree on here>"}}
 ],
 "delegation_moment": "<where in this flow the user stops deciding>",
 "question": "<one question about THIS system's design, answerable by a decision the team makes. Not a philosophical question about ethics in general.>"}}

Valid ids: {ids}."""


def _describe(dialects: dict) -> str:
    out = []
    for did, spec in dialects.items():
        out.append(
            f"- {did} ({spec['name']}, speaks {spec['speaks']})\n"
            f"    starts from: {' '.join(spec['starts_from'].split())}\n"
            f"    cannot say:  {' '.join(spec['blind_spot'].split())}"
        )
    return "\n".join(out)


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"no JSON in reply: {text[:200]!r}")
    return json.loads(match.group(0))


def review(endpoint, project: str, dialects: dict, context: str = "") -> dict:
    ctx = f"Additional context: {context}\n\n" if context else ""
    filled = TEMPLATE.format(
        dialects=_describe(dialects),
        project=project.strip(),
        context=ctx,
        ids=", ".join(dialects.keys()),
    )
    raw = endpoint.chat(filled, system=SYSTEM, temperature=0.2, max_tokens=2000)
    return _extract_json(raw)


def _wrap(text: str, width: int = 72, indent: str = "    ") -> str:
    import textwrap
    return textwrap.fill(str(text or "").strip(), width=width,
                         initial_indent=indent, subsequent_indent=indent)


def render(result: dict, dialects: dict) -> str:
    out = ["", "Six Dialects · project review", "=" * 60, ""]

    order = list(dialects.keys())
    readings = sorted(
        result.get("readings", []),
        key=lambda r: order.index(r["dialect"]) if r.get("dialect") in order else 99,
    )

    for r in readings:
        spec = dialects.get(r.get("dialect"), {})
        name = spec.get("name", r.get("dialect", "?"))
        speaks = spec.get("speaks", "")
        out.append(f"{name.upper()}  ·  {speaks}")
        out.append("  assumes")
        out.append(_wrap(r.get("assumes"), indent="    "))
        out.append("  reads as wrong")
        out.append(_wrap(r.get("misreads"), indent="    "))
        out.append("  design decision")
        out.append(_wrap(r.get("decision"), indent="    "))
        out.append("")

    tensions = result.get("tensions", [])
    if tensions:
        out.append("FORKS  ·  where two grammars contradict each other here")
        out.append("")
        for t in tensions:
            pair = t.get("between", [])
            names = " vs ".join(dialects.get(p, {}).get("name", p) for p in pair)
            out.append(f"  {names}")
            out.append(_wrap(t.get("about"), indent="    "))
            out.append("")

    if result.get("delegation_moment"):
        out.append("THE MOMENT")
        out.append(_wrap(result["delegation_moment"], indent="    "))
        out.append("")

    if result.get("question"):
        out.append("CARRY THIS")
        out.append(_wrap(result["question"], indent="    "))
        out.append("")

    return "\n".join(out)
