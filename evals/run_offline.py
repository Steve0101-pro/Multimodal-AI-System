"""Run deterministic offline regression checks for response quality."""

import argparse
import json
from pathlib import Path


EVAL_VERSION = "2026-09-05"


def judge_case(case: dict, response: str) -> dict:
    normalized = response.casefold()
    required = [term.casefold() for term in case.get("expected_contains", [])]
    forbidden = [term.casefold() for term in case.get("must_not_contain", [])]
    required_ok = all(term in normalized for term in required)
    forbidden_ok = all(term not in normalized for term in forbidden)
    return {
        "id": case["id"],
        "passed": required_ok and forbidden_ok,
        "criteria": {"required_terms": required_ok, "forbidden_terms": forbidden_ok},
    }


def run(cases_path: Path, responses_path: Path) -> dict:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    responses = json.loads(responses_path.read_text(encoding="utf-8"))
    results = [judge_case(case, responses.get(case["id"], "")) for case in cases]
    passed = sum(result["passed"] for result in results)
    return {
        "eval_version": EVAL_VERSION,
        "passed": passed,
        "total": len(results),
        "pass_rate": passed / len(results) if results else 0.0,
        "results": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path, help="JSON mapping case IDs to model responses")
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("golden.json"))
    parser.add_argument("--min-pass-rate", type=float, default=1.0)
    args = parser.parse_args()
    report = run(args.cases, args.responses)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["pass_rate"] >= args.min_pass_rate else 1)
