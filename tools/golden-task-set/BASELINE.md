# Golden Task Set — Baseline Data

## What This Is

This directory contains **example baseline data** for the golden task set evaluation framework. These results demonstrate realistic performance metrics for a well-functioning AI agent setup in a financial services context.

**Important:** These are **template/example results**, not production metrics from a specific organization. Teams implementing this framework should run the tasks against their own codebase and establish their own baseline.

---

## Baseline Summary

### Overall Performance

| Metric | Value |
|--------|-------|
| **Total Tasks Evaluated** | 12 of 12 |
| **Overall Pass Rate** | **91.7%** — healthy |
| **Total Time** | ~9.3 hours (46.4 min avg per task) |
| **Avg Rework Cycles** | 0.42 per task |

### Category Breakdown

| Category | Pass Rate | Status | Notes |
|----------|-----------|--------|-------|
| `bug_fix` | 100% (3/3) | ✅ Healthy | All bug fixes correct with proper regression tests |
| `api_extension` | 100% (3/3) | ✅ Healthy | Endpoints implemented with validation and docs |
| `migration` | 66.7% (2/3) | ⚠️ Degrading | One high-complexity migration failed (GT-008) |
| `integration` | 100% (3/3) | ✅ Healthy | External integrations working with retry logic |

---

## Task-by-Task Results

| Task ID | Category | Complexity | Est. Time | Actual Time | Result | Rework |
|---------|----------|------------|-----------|-------------|--------|--------|
| GT-001 | bug_fix | low | 20m | 22m | ✅ PASS | 0 |
| GT-002 | bug_fix | low | 15m | 18m | ✅ PASS | 0 |
| GT-003 | bug_fix | medium | 35m | 38m | ✅ PASS | 1 |
| GT-004 | api_extension | medium | 45m | 48m | ✅ PASS | 0 |
| GT-005 | api_extension | medium | 40m | 42m | ✅ PASS | 0 |
| GT-006 | api_extension | high | 60m | 65m | ✅ PASS | 1 |
| GT-007 | migration | low | 25m | 27m | ✅ PASS | 0 |
| GT-008 | migration | high | 75m | 80m | ❌ FAIL | 2 |
| GT-009 | migration | low | 20m | 22m | ✅ PASS | 0 |
| GT-010 | integration | high | 70m | 75m | ✅ PASS | 1 |
| GT-011 | integration | high | 65m | 68m | ✅ PASS | 0 |
| GT-012 | integration | medium | 50m | 52m | ✅ PASS | 0 |

---

## Failed Task Analysis

### GT-008: Migrate member_id format from integer to UUID

**Result:** ❌ FAIL
**Complexity:** high (75m estimated, 80m actual)
**Rework Cycles:** 2
**Failure Reason:** UUID migration incomplete — missed foreign key references in 2 tables. Partial rollback required.

**What Went Wrong:**
- Agent implemented UUID conversion in primary table
- **Missed** foreign key references in related tables (collateral, advances)
- Inconsistent state required rollback

**Root Cause:**
- Insufficient database schema analysis before implementation
- Agent did not trace all foreign key relationships

**Lesson:**
- High-complexity migrations require comprehensive schema analysis
- Pre-implementation dependency graph review is critical
- Migration tasks need additional validation checkpoints

---

## Performance Insights

### Strengths

1. **Bug Fix Excellence** (100% pass rate)
   - Agent correctly identifies root causes
   - Regression tests consistently included
   - Edge cases properly handled

2. **API Extension Reliability** (100% pass rate)
   - Input validation comprehensive
   - API documentation automatically updated
   - Error handling thorough

3. **Integration Robustness** (100% pass rate)
   - Retry logic implemented correctly
   - Idempotency working
   - Structured error responses match contracts

### Areas for Improvement

1. **High-Complexity Migrations** (66.7% pass rate)
   - Need pre-migration schema analysis step
   - Dependency graph tracing required
   - Rollback testing before execution

2. **Rework Cycles**
   - Average 0.42 cycles per task is acceptable but could be lower
   - Most rework occurred on high-complexity tasks
   - Consider breaking complex tasks into smaller milestones

---

## How Teams Should Use This Baseline

### Step 1: Establish Your Own Baseline

Don't use these results as-is! They're examples for a specific banking domain. Run the evaluation against **your** codebase:

```bash
# Run all 12 tasks over 1-2 weeks
for task in GT-001 GT-002 GT-003 GT-004 GT-005 GT-006 GT-007 GT-008 GT-009 GT-010 GT-011 GT-012; do
    python tools/golden-task-set/evaluate.py --task $task
    # Run the task with your agent
    # Record result:
    python tools/golden-task-set/evaluate.py --record $task --result pass --notes "..."
done

# Generate your weekly report
python tools/golden-task-set/evaluate.py --week
```

### Step 2: Track Weekly Trends

Run a subset (4-6 tasks) every Friday to track improvement over time:

```bash
# Week 2: Run 4 tasks (one per category)
python tools/golden-task-set/evaluate.py --record GT-001 --result pass
python tools/golden-task-set/evaluate.py --record GT-004 --result pass
python tools/golden-task-set/evaluate.py --record GT-007 --result pass
python tools/golden-task-set/evaluate.py --record GT-010 --result pass

# Generate trend report
python tools/golden-task-set/evaluate.py --week
```

### Step 3: Investigate Regressions

If pass rate drops >10% vs. prior week:

1. Identify which category declined
2. Review failed task notes for patterns
3. Audit recent model/prompt changes
4. Consider rollback if regression is severe

### Step 4: Quarterly Review

Every 3 months:
- Retire stale tasks (add `retired: true` to tasks.yaml)
- Add new tasks reflecting current work patterns
- Update baseline targets
- Adjust task complexity estimates if needed

---

## Interpreting Pass Rates

| Pass Rate | Signal | Action |
|-----------|--------|--------|
| **≥85%** | ✅ Healthy | Continue current configuration |
| **70–84%** | ⚠️ Acceptable | Review failing tasks for pattern |
| **55–69%** | 🔄 Degrading | Audit recent changes, consider rollback |
| **<55%** | 🚨 Critical | Stop agentic work, investigate root cause |

**Watch for category skew.** A 75% overall pass rate may hide a 33% pass rate on `migration` tasks — dangerous pattern for financial systems where schema changes carry high risk.

---

## File Structure

```
tools/golden-task-set/
├── tasks.yaml                     # Task definitions (12 tasks)
├── evaluate.py                    # Evaluation CLI tool
├── baseline-results.jsonl         # Example baseline data (THIS FILE)
├── baseline-weekly-report.md      # Example weekly report (THIS FILE)
├── BASELINE.md                    # This file
└── README.md                      # Full usage documentation
```

---

## Cost-Benefit Analysis

### Weekly Investment

| Activity | Time | Frequency |
|----------|------|-----------|
| Run 4-6 tasks | 2-3 hours | Weekly |
| Review results | 30 minutes | Weekly |
| Quarterly review | 1 day | Quarterly |

### ROI Calculation

Assuming a team of 5 engineers using AI agents:

**Without evaluation:**
- Agent regressions detected in production: 2-3 per quarter
- Production incident cost: $10,000–$50,000 per incident
- Total quarterly risk: $20,000–$150,000

**With golden task evaluation:**
- Weekly time cost: 3 hours × $150/hour = $450/week = $1,800/quarter
- Regressions detected early: 80% reduction
- Production incidents: 0-1 per quarter
- Total quarterly cost: $1,800 + $0–$50,000 = **$1,800–$51,800**

**Net savings:** $18,200–$148,200 per quarter

**Break-even:** 1-2 weeks

---

## Leadership Talking Points

### When Presenting This Framework

**"Why do we need this?"**
> "Without consistent measurement, we can't tell if our AI agents are improving or regressing. The golden task set gives us objective data to track performance week over week."

**"Is this worth the time?"**
> "Yes. A 3-hour weekly investment prevents $20,000–$150,000 in production incident costs per quarter. The ROI is 10-80x."

**"What's a healthy target?"**
> "≥85% overall pass rate, with no single category below 70%. Our baseline example shows 91.7% — strong performance that demonstrates the framework is working."

**"What if we're below target?"**
> "That's actionable data. We'll investigate which category is struggling, review the failing tasks, and adjust our approach. The point is to catch problems early, not hide them."

**"How do we know this isn't just gaming the test?"**
> "The tasks are real work drawn from our actual codebase (or the banking domain example here). They're not artificial test cases. If we pass them, we're genuinely improving our development process."

---

## Contact & Support

For questions about the golden task set or FRAME methodology:

- Documentation: See `README.md` in this directory
- Framework overview: `docs/framework-overview.md`
- GitHub Issues: Report bugs or request features

---

*Last updated: 2026-05-16*
*Baseline week: 2026-W20*
*Baseline pass rate: 91.7%*