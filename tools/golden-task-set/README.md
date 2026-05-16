# Golden Task Set

## What Is a Golden Task Set?

A **golden task set** is a stable, curated collection of representative coding tasks used to measure AI agent performance over time. The term "golden" signals that the set is authoritative — it does not change week to week except during planned quarterly reviews. By holding the tasks constant, you can track whether your agent configuration is improving, regressing, or plateauing across sprints.

This is the **Evaluation** pillar of the FRAME methodology (Focus → Requirements → Automation → Multi-agent → **Evaluation**). Without consistent measurement against a fixed baseline, technique improvements are invisible and regressions go undetected until they reach production.

---

## How It Works in the FRAME Weekly Cadence

Every Friday (or at the end of each sprint), a senior engineer runs a subset of golden tasks through the agent under evaluation and records pass/fail results. The results accumulate in `results.jsonl`. After four weeks, the weekly scorecard (`templates/weekly-scorecard.md`) uses the task success rate trend as its primary quality indicator.

**Weekly investment:** ~2-3 hours for a senior engineer running 4-6 tasks (one per category).

**Quarterly investment:** ~1 day to retire stale tasks and add new ones as the codebase evolves.

---

## Task Categories

The 12 tasks are distributed evenly across four categories that reflect real Apex Lending Services work:

| Category | Count | What It Tests |
|----------|-------|---------------|
| `bug_fix` | 3 | Root-cause analysis, targeted fixes, no regressions |
| `api_extension` | 3 | Endpoint design, validation, documentation |
| `migration` | 3 | Schema safety, backward compatibility, rollback |
| `integration` | 3 | External system contracts, error handling, retry logic |

---

## Running the Evaluation

### Prerequisites

- Python 3.11+
- PyYAML: `pip install pyyaml`
- A Claude Code session (or equivalent agent runner)

### Run a Single Task

```bash
python tools/golden-task-set/evaluate.py --task GT-001
```

This prints the prompt seed for GT-001. Paste it into a Claude Code session, let the agent work, then record the result.

### Record a Result

```bash
python tools/golden-task-set/evaluate.py --record GT-001 --result pass --notes "Correct fix, no regressions, test coverage maintained"
python tools/golden-task-set/evaluate.py --record GT-003 --result fail --notes "Agent modified unrelated function, introduced null dereference"
```

Results are appended to `tools/golden-task-set/results.jsonl`.

### Generate Weekly Report Template

```bash
python tools/golden-task-set/evaluate.py --week
```

Outputs a Markdown report template pre-populated with the current week's recorded results, pass rates by category, and trend vs. prior week.

---

## Workflow: Weekly Evaluation Session

1. **Monday:** Review `tasks.yaml` — no changes unless quarterly review week.
2. **Tuesday–Thursday:** Agent completes sprints normally.
3. **Friday morning:** Senior engineer runs 1 task per category (4 tasks minimum, 12 for full coverage).
   - Use `--task GT-NNN` to get the prompt seed.
   - Run the agent in isolation (fresh context, no carry-over from sprint work).
   - Use `--record` to log each result immediately after evaluation.
4. **Friday afternoon:** Run `--week` to generate the report, paste into the weekly scorecard.
5. **If pass rate drops >10% vs. prior week:** Investigate before next sprint starts.

---

## Interpreting Results

| Pass Rate | Signal | Action |
|-----------|--------|--------|
| ≥85% | Healthy | Continue current configuration |
| 70–84% | Acceptable | Review failing tasks for pattern |
| 55–69% | Degrading | Audit recent model/prompt changes, consider rollback |
| <55% | Critical | Stop agentic work, investigate root cause |

**Watch for category skew.** A 75% overall pass rate may hide a 33% pass rate on `migration` tasks — a dangerous pattern for a banking codebase where schema changes carry high risk.

---

## Updating the Task Set

Tasks are versioned in `tasks.yaml`. When retiring a task:
1. Add `retired: true` and `retired_date: YYYY-MM-DD` to the entry.
2. Do **not** delete the entry — historical results reference the task ID.
3. Add the replacement task with the next sequential ID.

Quarterly review checklist:
- [ ] At least one task per category reflects current codebase patterns
- [ ] Acceptance criteria remain testable without major codebase changes
- [ ] Complexity distribution still covers low/medium/high
- [ ] Baseline pass rates in `tasks.yaml` are updated from `results.jsonl` averages

---

## File Reference

| File | Purpose |
|------|---------|
| `tasks.yaml` | The authoritative task definitions |
| `evaluate.py` | CLI tool for running, recording, and reporting |
| `results.jsonl` | Append-only result log (one JSON object per line) |
| `README.md` | This file |
