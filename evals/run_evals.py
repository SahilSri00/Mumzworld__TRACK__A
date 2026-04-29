"""
Automated eval runner — runs all test cases through the parser and scores them.
Usage: python -m evals.run_evals
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import parse_mom_message
from evals.rubric import score_test_case


async def run_single_test(test_case: dict) -> dict:
    """Run one test case and return scored results."""
    test_id = test_case["id"]
    message = test_case["input"]
    expected = test_case["expected"]

    print(f"\n{'='*60}")
    print(f"  Test: {test_id}")
    print(f"  Input: {message[:80]}{'...' if len(message) > 80 else ''}")
    print(f"{'='*60}")

    try:
        result = await parse_mom_message(message)
        result_dict = result.model_dump()
        scores = score_test_case(result_dict, expected)

        for name, data in scores.items():
            if name != "total":
                print(f"  {data['detail']}")

        total = scores["total"]
        print(f"\n  Score: {total['score']}/{total['max']} ({total['percentage']}%)")

        return {
            "test_id": test_id,
            "input": message,
            "scores": scores,
            "result": result_dict,
            "error": None,
        }
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return {
            "test_id": test_id,
            "input": message,
            "scores": {"total": {"score": 0, "max": 7, "percentage": 0}},
            "result": None,
            "error": str(e),
        }


async def main():
    # Load test cases
    test_file = Path(__file__).parent.parent / "data" / "test_cases.json"
    with open(test_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print(f"\n{'#'*60}")
    print(f"  Mumzworld Shopping List Parser — Eval Suite")
    print(f"  Running {len(test_cases)} test cases")
    print(f"{'#'*60}")

    results = []
    for tc in test_cases:
        result = await run_single_test(tc)
        results.append(result)
        # Small delay to respect rate limits
        await asyncio.sleep(6)

    # Aggregate scores
    total_score = sum(r["scores"]["total"]["score"] for r in results)
    total_max = sum(r["scores"]["total"]["max"] for r in results)
    overall_pct = round(total_score / total_max * 100, 1) if total_max > 0 else 0

    failed = [r for r in results if r["error"] or r["scores"]["total"]["percentage"] < 50]
    passed = [r for r in results if not r["error"] and r["scores"]["total"]["percentage"] >= 50]

    print(f"\n\n{'#'*60}")
    print(f"  RESULTS SUMMARY")
    print(f"{'#'*60}")
    print(f"  Total Score: {total_score}/{total_max} ({overall_pct}%)")
    print(f"  Passed: {len(passed)}/{len(results)}")
    print(f"  Failed: {len(failed)}/{len(results)}")

    if failed:
        print(f"\n  Failed tests:")
        for r in failed:
            err = f" (Error: {r['error']})" if r["error"] else ""
            print(f"    - {r['test_id']}: {r['scores']['total']['percentage']}%{err}")

    # Save detailed results
    output_path = Path(__file__).parent.parent / "eval_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Detailed results saved to: {output_path}")

    # Generate EVALS.md
    generate_evals_md(results, overall_pct, len(passed), len(failed))


def generate_evals_md(results, overall_pct, passed, failed):
    """Generate the EVALS.md markdown file from results."""
    md = f"""# Evaluation Results

## Summary

| Metric | Value |
|--------|-------|
| Overall Score | **{overall_pct}%** |
| Tests Passed | {passed}/{len(results)} |
| Tests Failed | {failed}/{len(results)} |

## Rubric

Each test case is scored on 7 criteria (1 point each):

| Criterion | Description |
|-----------|-------------|
| Language Detection | Correct EN/AR detection |
| Item Count | Extracted at least the expected number of items |
| Categories | Correct product category assignment |
| Calendar Events | Detected events when present |
| Out-of-Scope | Correctly refused irrelevant messages |
| Uncertainty | Expressed uncertainty when appropriate |
| Schema Validity | Valid JSON with no empty required fields |

## Per-Test Results

| Test ID | Score | Details |
|---------|-------|---------|
"""
    for r in results:
        total = r["scores"]["total"]
        status = "✅" if total["percentage"] >= 70 else "⚠️" if total["percentage"] >= 50 else "❌"
        md += f"| {r['test_id']} | {status} {total['percentage']}% | "

        details = []
        for name, data in r["scores"].items():
            if name != "total":
                icon = "✅" if data["score"] >= data["max"] else "❌"
                details.append(f"{icon} {name}")
        md += ", ".join(details) + " |\n"

    md += """
## Failure Analysis

"""
    failures = [r for r in results if r["scores"]["total"]["percentage"] < 70]
    if not failures:
        md += "No significant failures.\n"
    else:
        for r in failures:
            md += f"### {r['test_id']} ({r['scores']['total']['percentage']}%)\n\n"
            if r["error"]:
                md += f"**Error:** {r['error']}\n\n"
            for name, data in r["scores"].items():
                if name != "total" and data["score"] < data["max"]:
                    md += f"- {data['detail']}\n"
            md += "\n"

    md += """## Honest Assessment

These eval results reflect real model behavior. Known limitations:
- Arabic output quality varies by model and may occasionally read as translated
- Mixed EN/AR (code-switching) messages are harder to parse consistently
- Very vague inputs may sometimes produce items with low confidence rather than flagging as out-of-scope
- Calendar date inference is approximate when only relative dates are given ("next month")
"""

    output_path = Path(__file__).parent.parent / "EVALS.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  EVALS.md generated at: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
