"""six-dialects · command line.

Two verbs:

  probe    measure which grammar a model reaches for first
  review   read what you are building in six grammars
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from .client import Endpoint, EndpointError
from .report import render as render_probe
from .review import render as render_review
from .review import review as run_review
from .run import load_dialects, load_scenarios, probe


def _endpoint_args(ap):
    ap.add_argument("--base-url", default=os.environ.get("SIXD_BASE_URL"),
                    help="OpenAI-compatible base URL, e.g. https://host/v1")
    ap.add_argument("--model", default=os.environ.get("SIXD_MODEL"),
                    help="model name on that endpoint")
    ap.add_argument("--api-key", default=os.environ.get("SIXD_API_KEY", ""),
                    help="your key. Read, used, never stored.")
    ap.add_argument("--out", help="write the full result to this JSON file")
    ap.add_argument("--quiet", action="store_true")


def build_parser():
    ap = argparse.ArgumentParser(
        prog="six-dialects",
        description="Six ethical grammars, as an instrument.",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("probe", help="measure a model's ethical grammar")
    _endpoint_args(p)
    p.add_argument("--judge-base-url", default=os.environ.get("SIXD_JUDGE_BASE_URL"))
    p.add_argument("--judge-model", default=os.environ.get("SIXD_JUDGE_MODEL"),
                   help="judge model; omit to run the transparent scorer only")
    p.add_argument("--judge-api-key", default=os.environ.get("SIXD_JUDGE_API_KEY"))
    p.add_argument("--scenarios", help="path to your own scenarios.yaml")

    r = sub.add_parser("review", help="read your project in six grammars")
    _endpoint_args(r)
    r.add_argument("project", nargs="?",
                   help="what you are building, in your own words. Omit to read stdin.")
    r.add_argument("--file", help="read the project description from a file")
    r.add_argument("--used-by", default="",
                   help="the person operating it (e.g. a council clerk)")
    r.add_argument("--affects", default="",
                   help="the people it affects, if not the same person")
    r.add_argument("--region", default="",
                   help="where it is used, and in which language")
    r.add_argument("--decides", default="",
                   help="what the system decides or recommends")
    r.add_argument("--context", default="", help="anything else worth knowing")

    return ap


def _need_endpoint(ap, args):
    if not args.base_url or not args.model:
        ap.error("--base-url and --model are required (or set SIXD_BASE_URL / SIXD_MODEL)")
    return Endpoint(args.base_url, args.model, args.api_key)


def _cmd_probe(ap, args) -> int:
    target = _need_endpoint(ap, args)
    judge = None
    if args.judge_model:
        judge = Endpoint(args.judge_base_url or args.base_url,
                         args.judge_model,
                         args.judge_api_key or args.api_key)

    dialects = load_dialects()
    scenarios = load_scenarios(args.scenarios)

    if not args.quiet:
        print(f"Probing {args.model} with {len(scenarios)} scenarios", file=sys.stderr)

    result = probe(target, scenarios, dialects, judge=judge,
                   on_event=None if args.quiet else lambda s: print(f"  … {s}", file=sys.stderr))
    print(render_probe(result, dialects, args.model))
    return _write(args, result)


def _cmd_review(ap, args) -> int:
    endpoint = _need_endpoint(ap, args)

    if args.file:
        project = open(args.file, encoding="utf-8").read()
    elif args.project:
        project = args.project
    elif not sys.stdin.isatty():
        project = sys.stdin.read()
    else:
        ap.error("give a project description as an argument, with --file, or on stdin")

    if not project.strip():
        ap.error("the project description is empty")

    if not args.quiet:
        print("Reading it in six grammars", file=sys.stderr)

    dialects = load_dialects()
    result = run_review(
        endpoint, project, dialects,
        context=args.context,
        used_by=args.used_by,
        affects=args.affects,
        region=args.region,
        decides=args.decides,
    )
    print(render_review(result, dialects))
    return _write(args, result)


def _write(args, result) -> int:
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
        print(f"Written to {args.out}")
    return 0


def main(argv=None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    try:
        if args.command == "probe":
            return _cmd_probe(ap, args)
        return _cmd_review(ap, args)
    except EndpointError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
