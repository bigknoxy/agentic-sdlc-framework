# Personal Project Example: Task Management API

This example demonstrates the complete Agentic SDLC Framework on a simple task management API — the kind of project you might build for personal use.

## Project Overview

**Goal:** Build a REST API for personal task management with:
- CRUD operations for tasks
- Due date tracking
- Priority levels
- Simple authentication

**Why This Project:**
- Clear scope (not too big, not too small)
- Real-world patterns (applicable to work projects)
- Can be built incrementally
- Good for demonstrating framework value

**Tech Stack:**
- Python 3.11+
- FastAPI
- SQLite (for simplicity)
- pytest for testing
- GitHub Actions for CI/CD

---

## Phase 0: Intake & Triage

### Intake Ticket

```markdown
---
intake_id: INTAKE-2025-01-001
date: 2025-01-15
requester: josh@personal.com
---

# Project Intake: Personal Task API

## Idea
Build a simple REST API to manage personal tasks with due dates and priorities.

## Business Value
- **Current pain:** Using spreadsheets for task tracking
- **Desired outcome:** API I can call from anywhere (CLI, web, mobile)
- **Success metric:** Reduce task entry time from 2 minutes to 10 seconds

## Scope
- Create, read, update, delete tasks
- Set due dates
- Set priorities (low, medium, high)
- Mark complete/incomplete
- Simple auth (just me)

## Technical Constraints
- Must run locally
- SQLite is fine (no external DB)
- Python preferred
- Open source (GitHub)

## Risk Assessment
- **Risk:** Scope creep → Mitigation: Strict MVP definition
- **Risk:** Over-engineering → Mitigation: Time-box to 2 weekends

## Decision: ✅ GO
- Clear scope
- Low risk
- Good learning opportunity
- Can demonstrate framework
```

---

## Phase 1: Executable Spec

See [spec-task-api.md](spec-task-api.md) for the complete agent-ready specification.

### Key Decisions from Spec

1. **Framework:** FastAPI (modern, auto-docs, easy testing)
2. **Database:** SQLite with SQLAlchemy (simple, no external deps)
3. **Auth:** JWT tokens (overkill for personal use, but good practice)
4. **Priority levels:** Enum (low=1, medium=2, high=3)

### Spec Quality Notes

What worked:
- Explicit file structure helped agent understand project layout
- Gherkin acceptance criteria were directly testable
- Edge cases caught issues early (e.g., due dates in past)

What could improve:
- Initially missed rate limiting spec
- Added after first draft

---

## Phase 2: Design & Architecture

### ADR-001: FastAPI vs Flask vs Django

**Decision:** Use FastAPI

**Rationale:**
- Automatic OpenAPI documentation
- Built-in data validation with Pydantic
- Async support for future scaling
- Type hints throughout

**Trade-offs:**
- Newer framework (smaller community than Flask)
- Learning curve for advanced features
- Worth it for this project

See [adr-001-framework-choice.md](adr-001-framework-choice.md)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                               │
│                   (curl, browser, CLI)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/JSON
┌───────────────────────▼─────────────────────────────────────┐
│                   FastAPI Application                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Routes    │→ │   Services  │→ │   Repository        │ │
│  │  (API layer)│  │(Business logic)│  │   (Data access)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         │                                    │              │
│         │                              ┌─────▼─────┐        │
│         │                              │  SQLite   │        │
│         │                              │  (tasks)  │        │
│         │                              └───────────┘        │
│  ┌──────▼──────┐                                            │
│  │  JWT Auth   │                                            │
│  │ Middleware  │                                            │
│  └─────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 3: Implementation

### Milestone 1: Project Setup & Models

**Handoff Packet:** [handoff-packets/handoff-001.md](handoff-packets/handoff-001.md)

**What was built:**
- Project structure
- Database models (SQLAlchemy)
- Pydantic schemas
- Initial migration

**Time:** 45 minutes (vs estimated 2 hours manually)

**Agent approach:**
1. Gave spec to planner agent
2. Planner broke into 5 tasks
3. Executor agent implemented each
4. Reviewer agent checked against spec

### Milestone 2: CRUD Endpoints

**Handoff Packet:** [handoff-packets/handoff-002.md](handoff-packets/handoff-002.md)

**What was built:**
- POST /tasks (create)
- GET /tasks (list with filters)
- GET /tasks/{id} (read)
- PUT /tasks/{id} (update)
- DELETE /tasks/{id} (delete)

**Time:** 1 hour (vs estimated 3 hours manually)

**Challenge:** Agent initially missed pagination on list endpoint
- Caught in review
- Fixed in 10 minutes

### Milestone 3: Authentication & Testing

**Handoff Packet:** [handoff-packets/handoff-003.md](handoff-packets/handoff-003.md)

**What was built:**
- JWT authentication
- Protected endpoints
- Comprehensive test suite
- CI/CD workflow

**Time:** 1.5 hours (vs estimated 4 hours manually)

**Quality:**
- 94% test coverage (target: 80%)
- All security scans passed
- No critical/high vulnerabilities

---

## Phase 4: Validation

### Security Scan Results

| Check | Status | Notes |
|-------|--------|-------|
| Secrets scanning | ✅ | Clean |
| SAST (Bandit) | ✅ | No issues |
| Dependency scan | ✅ | All clean |
| JWT implementation | ✅ | Using python-jose correctly |

### Test Results

| Suite | Tests | Passed | Coverage |
|-------|-------|--------|----------|
| Unit | 24 | 24 ✅ | 94% |
| Integration | 12 | 12 ✅ | - |
| E2E | 8 | 8 ✅ | - |

### Performance

| Endpoint | p50 | p95 | p99 |
|----------|-----|-----|-----|
| POST /tasks | 45ms | 89ms | 120ms |
| GET /tasks | 32ms | 67ms | 95ms |

All within SLA (< 200ms).

---

## Phase 5: Deployment

### Local Deployment

```bash
# Run locally
uvicorn main:app --reload

# Or with Docker
docker-compose up
```

### CI/CD

GitHub Actions workflow:
- Lint with ruff
- Test with pytest
- Security scan with Bandit
- Build Docker image

See `.github/workflows/ci.yml`

---

## Metrics & Results

### Framework Effectiveness

| Metric | Traditional | Agentic | Improvement |
|--------|-------------|---------|-------------|
| Total time | ~16 hours | ~6 hours | 62% faster |
| First-pass PR rate | ~40% | 75% | +35 points |
| Test coverage | ~70% | 94% | +24 points |
| Defects found | 5-8 | 2 | 75% fewer |

### Spec Quality Impact

Specs that produced clean first drafts:
- Database models (clear requirements)
- CRUD endpoints (explicit HTTP methods)

Specs that needed rework:
- Authentication (initially underspecified token expiry)
- Pagination (missed in first draft)

### Lessons Learned

**What worked:**
1. Executable specs with Gherkin tests
2. Multi-agent coordination (planner → executor → reviewer)
3. Automated guardrails caught issues early
4. Handoff packets maintained context

**What to improve:**
1. Spend more time on edge cases in specs
2. Add explicit performance requirements
3. Include more security constraints upfront
4. Document "why" not just "what"

**Surprises:**
- Agent was conservative with dependencies (good!)
- Generated docstrings were excellent
- Test cases often caught edge cases I missed

---

## Files

```
personal-project-example/
├── README.md                    # This file
├── spec-task-api.md             # Agent-ready spec
├── adr-001-framework-choice.md   # Architecture decision
├── handoff-packets/
│   ├── handoff-001.md          # Milestone 1
│   ├── handoff-002.md          # Milestone 2
│   └── handoff-003.md          # Milestone 3
├── src/
│   ├── main.py                 # FastAPI app
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── crud.py                 # Database operations
│   ├── auth.py                 # JWT authentication
│   └── database.py             # DB connection
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Next Steps

This project demonstrates the framework on a simple API. Next steps:

1. **Add features:** Recurring tasks, tags, search
2. **Build frontend:** Simple React or Vue UI
3. **Mobile app:** React Native or Flutter
4. **Deploy to cloud:** AWS/GCP with proper infrastructure

Each would follow the same framework phases.

---

## Using This Example

To use this framework on your own personal project:

1. **Copy the spec template** from [spec-task-api.md](spec-task-api.md)
2. **Fill in your project details**
3. **Run the guardrail scripts:**
   ```bash
   python tools/guardrail-scripts/validate-spec.py spec-your-project.md
   ```
4. **Use multi-agent coordination** (or just work through the spec yourself)
5. **Track metrics** with the weekly scorecard

See the [main framework documentation](../README.md) for full details.
