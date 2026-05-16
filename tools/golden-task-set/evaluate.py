#!/usr/bin/env python3
"""
evaluate.py — Golden Task Set Evaluation CLI

Usage:
  # Print prompt seed for a single task
  python evaluate.py --task GT-001

  # Record a result for a completed task
  python evaluate.py --record GT-001 --result pass --notes "Correct fix, all tests pass"
  python evaluate.py --record GT-003 --result fail --notes "Agent introduced null dereference in edge case"

  # Generate weekly evaluation report template (Markdown)
  python evaluate.py --week

  # List all tasks (optionally filter by category)
  python evaluate.py --list
  python evaluate.py --list --category bug_fix
"""

import argparse
import json
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
TASKS_FILE = SCRIPT_DIR / "tasks.yaml"
RESULTS_FILE = SCRIPT_DIR / "results.jsonl"


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_tasks() -> list[dict]:
    """Load and return all task definitions from tasks.yaml."""
    if not TASKS_FILE.exists():
        print(f"ERROR: tasks.yaml not found at {TASKS_FILE}", file=sys.stderr)
        sys.exit(2)
    with TASKS_FILE.open() as f:
        data = yaml.safe_load(f)
    tasks = data.get("tasks", [])
    if not tasks:
        print("ERROR: tasks.yaml contains no tasks.", file=sys.stderr)
        sys.exit(2)
    return tasks


def load_results() -> list[dict]:
    """Load all recorded results from results.jsonl."""
    if not RESULTS_FILE.exists():
        return []
    results = []
    with RESULTS_FILE.open() as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(
                    f"WARNING: Skipping malformed JSON on line {lineno} of results.jsonl: {exc}",
                    file=sys.stderr,
                )
    return results


def find_task(tasks: list[dict], task_id: str) -> dict | None:
    """Return the task with the given ID, or None."""
    task_id = task_id.upper()
    for t in tasks:
        if t.get("id", "").upper() == task_id:
            return t
    return None


# ── Prompt Seed Generation ────────────────────────────────────────────────────

PROMPT_TEMPLATE = """\
=== GOLDEN TASK PROMPT SEED ===
Task ID:    {id}
Category:   {category}
Complexity: {complexity}
Est. Time:  {estimated_minutes} minutes
Tags:       {tags}

--- TASK ---
{title}

{description}

--- ACCEPTANCE CRITERIA ---
{criteria}

--- INSTRUCTIONS FOR AGENT ---
You are an executor agent working on the Apex Lending Services API.
Your job is to implement exactly what is described above, nothing more.

Before writing any code:
1. Restate the problem in one sentence.
2. List the files you expect to modify.
3. Confirm that your approach satisfies every acceptance criterion.

Then implement the fix or feature. When done:
- Run the existing test suite and report pass/fail counts.
- Confirm no previously passing tests have regressed.
- State which acceptance criteria are satisfied and which (if any) are not.
- If data classification is "confidential", confirm that no raw member_id
  or PII appears in log output (only hashed values).

=== END PROMPT SEED ===
"""


def print_prompt_seed(task: dict) -> None:
    """Print a Claude Code prompt seed for the given task."""
    criteria_lines = "\n".join(
        f"  [{i+1}] {c}" for i, c in enumerate(task.get("acceptance_criteria", []))
    )
    tags = ", ".join(task.get("tags", []))
    description = task.get("description", "").strip()
    prompt = PROMPT_TEMPLATE.format(
        id=task["id"],
        category=task["category"],
        complexity=task["complexity"],
        estimated_minutes=task["estimated_minutes"],
        tags=tags,
        title=task["title"],
        description=description,
        criteria=criteria_lines,
    )
    print(prompt)


# ── Result Recording ──────────────────────────────────────────────────────────

def record_result(task_id: str, result: str, notes: str, tasks: list[dict]) -> None:
    """Append a result entry to results.jsonl."""
    task = find_task(tasks, task_id)
    if task is None:
        print(f"ERROR: Task '{task_id}' not found in tasks.yaml.", file=sys.stderr)
        sys.exit(1)

    if result not in ("pass", "fail"):
        print("ERROR: --result must be 'pass' or 'fail'.", file=sys.stderr)
        sys.exit(2)

    entry = {
        "task_id": task["id"],
        "category": task["category"],
        "complexity": task["complexity"],
        "result": result,
        "notes": notes or "",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "week": _iso_week(),
    }

    with RESULTS_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Recorded: {task['id']} → {result.upper()}")
    print(f"  Week:  {entry['week']}")
    print(f"  Notes: {notes or '(none)'}")
    print(f"  File:  {RESULTS_FILE}")


def _iso_week() -> str:
    """Return the current ISO week string, e.g. '2026-W20'."""
    now = datetime.now(timezone.utc)
    return f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"


# ── Weekly Report ─────────────────────────────────────────────────────────────

def generate_weekly_report(tasks: list[dict], results: list[dict]) -> None:
    """Print a Markdown weekly evaluation report template."""
    current_week = _iso_week()
    all_weeks = sorted({r["week"] for r in results}, reverse=True)

    # Current week results
    week_results = [r for r in results if r["week"] == current_week]
    prior_week = all_weeks[1] if len(all_weeks) > 1 else None
    prior_results = [r for r in results if r["week"] == prior_week] if prior_week else []

    def pass_rate(result_list: list[dict]) -> float | None:
        if not result_list:
            return None
        passes = sum(1 for r in result_list if r["result"] == "pass")
        return passes / len(result_list) * 100

    def category_pass_rate(result_list: list[dict], category: str) -> float | None:
        cat = [r for r in result_list if r["category"] == category]
        return pass_rate(cat)

    overall = pass_rate(week_results)
    prior_overall = pass_rate(prior_results)

    categories = ["bug_fix", "api_extension", "migration", "integration"]

    # Build the report
    lines = [
        f"# Golden Task Set — Weekly Evaluation Report",
        f"",
        f"**Week:** {current_week}",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Tasks Evaluated:** {len(week_results)} of {len(tasks)}",
        f"",
        f"---",
        f"",
        f"## Overall Pass Rate",
        f"",
    ]

    if overall is not None:
        trend = ""
        if prior_overall is not None:
            delta = overall - prior_overall
            trend = f" ({'+' if delta >= 0 else ''}{delta:.1f}% vs {prior_week})"
        health = _health_label(overall)
        lines.append(f"**{overall:.1f}%** {trend} — {health}")
    else:
        lines.append("No results recorded for the current week. Run tasks and use --record to log results.")

    lines += [
        f"",
        f"---",
        f"",
        f"## Results by Category",
        f"",
        f"| Category | This Week | Prior Week | Status |",
        f"|----------|-----------|------------|--------|",
    ]

    for cat in categories:
        this = category_pass_rate(week_results, cat)
        prior = category_pass_rate(prior_results, cat)
        this_str = f"{this:.1f}%" if this is not None else "—"
        prior_str = f"{prior:.1f}%" if prior is not None else "—"
        status = _health_label(this) if this is not None else "no data"
        lines.append(f"| {cat} | {this_str} | {prior_str} | {status} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## Task Results This Week",
        f"",
        f"| Task ID | Category | Complexity | Result | Notes |",
        f"|---------|----------|------------|--------|-------|",
    ]

    task_ids_run = {r["task_id"] for r in week_results}
    for result in sorted(week_results, key=lambda r: r["task_id"]):
        result_badge = "PASS" if result["result"] == "pass" else "FAIL"
        notes = result.get("notes", "").replace("|", "/")
        lines.append(
            f"| {result['task_id']} | {result['category']} | {result['complexity']} "
            f"| {result_badge} | {notes} |"
        )

    not_run = [t for t in tasks if t["id"] not in task_ids_run and not t.get("retired")]
    if not_run:
        lines += [
            f"",
            f"**Tasks not evaluated this week ({len(not_run)}):** "
            + ", ".join(t["id"] for t in not_run),
        ]

    lines += [
        f"",
        f"---",
        f"",
        f"## Observations",
        f"",
        f"<!-- Fill in manually after reviewing results -->",
        f"",
        f"- [ ] Any category below 70%? Investigate before next sprint.",
        f"- [ ] Any category that regressed >10% vs. prior week?",
        f"- [ ] Any consistent failure pattern (e.g., agent always fails on audit logging)?",
        f"- [ ] Recommended action for next week:",
        f"",
        f"---",
        f"",
        f"## Action Items",
        f"",
        f"| Item | Owner | Due |",
        f"|------|-------|-----|",
        f"| (add items) | | |",
        f"",
        f"---",
        f"",
        f"*Generated by `tools/golden-task-set/evaluate.py --week`*",
    ]

    print("\n".join(lines))


def _health_label(rate: float | None) -> str:
    if rate is None:
        return "no data"
    if rate >= 85:
        return "healthy"
    if rate >= 70:
        return "acceptable"
    if rate >= 55:
        return "degrading"
    return "CRITICAL"


# ── List Tasks ────────────────────────────────────────────────────────────────

def list_tasks(tasks: list[dict], category: str | None) -> None:
    """Print a summary table of all tasks."""
    header = f"{'ID':<10} {'Category':<16} {'Complexity':<12} {'Est.':<8} {'Title'}"
    print(header)
    print("-" * 80)
    for t in tasks:
        if t.get("retired"):
            continue
        if category and t["category"] != category:
            continue
        print(
            f"{t['id']:<10} {t['category']:<16} {t['complexity']:<12} "
            f"{str(t['estimated_minutes'])+'m':<8} {t['title']}"
        )


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Golden Task Set evaluation tool for the FRAME methodology.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--task",
        metavar="TASK_ID",
        help="Print the prompt seed for a specific task (e.g. GT-001).",
    )
    group.add_argument(
        "--record",
        metavar="TASK_ID",
        help="Record a result for a completed task evaluation.",
    )
    group.add_argument(
        "--week",
        action="store_true",
        help="Generate the weekly evaluation report template (Markdown).",
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="List all tasks in the golden set.",
    )

    parser.add_argument(
        "--result",
        choices=["pass", "fail"],
        help="Result to record (required with --record).",
    )
    parser.add_argument(
        "--notes",
        default="",
        metavar="TEXT",
        help="Optional notes to attach to a recorded result.",
    )
    parser.add_argument(
        "--category",
        choices=["bug_fix", "api_extension", "migration", "integration"],
        help="Filter by category (used with --list).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    tasks = load_tasks()

    if args.task:
        task = find_task(tasks, args.task)
        if task is None:
            print(f"ERROR: Task '{args.task}' not found.", file=sys.stderr)
            available = [t["id"] for t in tasks if not t.get("retired")]
            print(f"Available task IDs: {', '.join(available)}", file=sys.stderr)
            sys.exit(1)
        print_prompt_seed(task)

    elif args.record:
        if not args.result:
            print("ERROR: --result pass|fail is required when using --record.", file=sys.stderr)
            sys.exit(2)
        record_result(args.record, args.result, args.notes, tasks)

    elif args.week:
        results = load_results()
        generate_weekly_report(tasks, results)

    elif args.list:
        list_tasks(tasks, args.category)


if __name__ == "__main__":
    main()
