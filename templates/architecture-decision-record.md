---
adr_id: ADR-YYYY-###
title: [Short title describing the decision]
date: YYYY-MM-DD
status: proposed | accepted | deprecated | superseded
---

# [Title]

## Context

### Problem Statement
[What is the issue that we're seeing that is motivating this decision or change?]

### Constraints
- [Constraint 1: e.g., "Must use existing tech stack"]
- [Constraint 2: e.g., "Must comply with regulation X"]
- [Constraint 3: e.g., "Budget limitation of $Y"]

### Assumptions
- [Assumption 1]
- [Assumption 2]

## Decision

### Chosen Solution
[What is the change that we're proposing or have agreed to implement?]

### Rationale
[Why was this solution chosen? What factors were considered?]

| Factor | Weight | Option A | Option B | Option C |
|--------|--------|----------|----------|----------|
| [Criterion 1] | High | ✅ | ⚠️ | ❌ |
| [Criterion 2] | Medium | ✅ | ✅ | ❌ |
| [Criterion 3] | Low | ⚠️ | ✅ | ✅ |
| **Total** | | **X** | **Y** | **Z** |

## Consequences

### Positive
- [Benefit 1: e.g., "Improved performance by 40%"]
- [Benefit 2: e.g., "Reduced complexity"]
- [Benefit 3]

### Negative
- [Drawback 1: e.g., "Learning curve for team"]
- [Drawback 2: e.g., "Additional infrastructure cost"]

### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Strategy] |
| [Risk 2] | High/Med/Low | High/Med/Low | [Strategy] |

## Alternatives Considered

### [Alternative 1: e.g., "Use PostgreSQL instead of MongoDB"]

**Description:**
[What was this alternative?]

**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

**Why Rejected:**
[Clear explanation]

### [Alternative 2]

**Description:**
[...]

**Pros:**
- [...]

**Cons:**
- [...]

**Why Rejected:**
[...]

## Related Decisions

- **Depends on:** [Links to ADRs this depends on]
- **Supersedes:** [Links to ADRs this replaces]
- **Superseded by:** [Link to newer ADR if deprecated]
- **Related:** [Links to related ADRs]

## Implementation Notes

### Migration Strategy
[If this replaces something, how will migration work?]

### Rollback Plan
[How can we undo this if needed?]

### Timeline
| Phase | Target Date | Deliverables |
|-------|-------------|--------------|
| Phase 1 | YYYY-MM-DD | [Deliverables] |
| Phase 2 | YYYY-MM-DD | [Deliverables] |

## Monitoring & Success Criteria

### Metrics
| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| [Metric 1] | [Value] | [Value] | [Method] |
| [Metric 2] | [Value] | [Value] | [Method] |

### Review Date
[When will we review this decision?]

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | | | |
| Technical Lead | | | |
| Security (if applicable) | | | |
| Architecture Board | | | |

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | YYYY-MM-DD | [Name] | Initial draft |
| 1.0 | YYYY-MM-DD | [Name] | Approved |
