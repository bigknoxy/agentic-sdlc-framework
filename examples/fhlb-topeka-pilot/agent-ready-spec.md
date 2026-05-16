---
spec_id: SPEC-2026-05-15-001
title: Add GET /members/{member_id}/advance-eligibility endpoint
status: draft
priority: p1
estimated_effort: 16 hours
template_version: 1.0.0
data_classification: confidential
pilot_id: PILOT-2026-AFC-001
---

# Agent-Ready Specification: Advance Eligibility Check Endpoint

> **Purpose:** This document is the single source of truth for implementing the advance eligibility endpoint. Read every section before writing any code. Do not implement features not described here. Do not make assumptions about business rules — if a rule is ambiguous, treat the most conservative interpretation as correct and note the ambiguity in the PR description.

---

## 1. Context (Business Problem)

### Current State

Apex Financial Corp member institutions frequently call the Member Services team to ask whether they are eligible to request a new advance before submitting a formal advance application. The eligibility determination involves three checks:

1. **Collateral coverage ratio:** The member must have pledged collateral with a lendable value that covers their existing advance balance plus the requested new advance amount (at the applicable haircut rate).
2. **Advance balance limit:** No single member may hold more than $500,000,000 in aggregate outstanding advance principal.
3. **Member standing:** The member must not be in suspended or probationary status per the Member Status table.

Today, a Member Services representative performs these checks manually by querying three separate internal screens in the legacy Core Banking System (CBS), calculating the coverage ratio on a spreadsheet, and calling the member back — a process that takes 15–30 minutes per inquiry. Member institutions report this as a friction point when making time-sensitive funding decisions.

The API exists and serves the Member Portal and Advance Origination System, but no endpoint currently exposes an eligibility pre-check. The Advance Origination System performs a similar check at application submission time, but that is a blocking gate — members want a lightweight pre-check that does not create an application record.

### Desired State

A new GET endpoint that returns an eligibility determination for a given member and requested advance amount. The endpoint is non-mutating (read-only). It does not create an advance application, lock collateral, or modify any record. The Member Portal team will integrate this endpoint to surface an eligibility indicator on the member dashboard before the member initiates an advance application.

After implementation, a Member Services representative answering an eligibility inquiry can direct the member to the Member Portal dashboard for an instant answer, or the representative can call the API directly during a phone call. Either way, the 15–30 minute manual check is eliminated for the common case.

### Business Value

**Primary KPI Impact:**
- Metric: Time to answer member advance eligibility inquiry
- Current: 15–30 minutes (manual, via CBS screens + spreadsheet)
- Target: <2 seconds (API response)
- Measurement Method: Member Services call log time-to-resolution; API response time p95 from APM

**Secondary Benefits:**
- Member Portal team unblocked: they have been waiting for this endpoint to implement the eligibility indicator feature (estimated 2-sprint unblock)
- Reduces load on Member Services phone line during peak advance demand periods (month-end)
- Provides a consistent, auditable eligibility determination vs. ad-hoc manual checks that vary by representative

**Risk if Not Done:**
Member Portal team cannot ship their eligibility indicator feature. Member institutions continue to call Member Services for manual checks, consuming representative time. Manual checks introduce inconsistency risk — two representatives may reach different eligibility conclusions for the same member state.

---

## 2. Goal State (Definition of Done)

### Functional Requirements

**Must Have (P0):**
- [ ] `GET /members/{member_id}/advance-eligibility?requested_amount={amount}` returns an eligibility determination
- [ ] Response includes: `eligible` (boolean), `reason` (string, human-readable), `collateral_coverage_ratio` (decimal, 4 decimal places), `aggregate_advance_balance` (decimal), `available_capacity` (decimal)
- [ ] Collateral coverage check: `lendable_collateral_value >= aggregate_advance_balance + requested_amount`; lendable value = sum of `estimated_value * (1 - haircut_rate)` across all pledged collateral for the member
- [ ] Aggregate advance balance limit check: `aggregate_advance_balance + requested_amount <= 500000000.00`
- [ ] Member standing check: member status must be `active` (not `suspended` or `probationary`)
- [ ] Returns HTTP 404 with `MEMBER_NOT_FOUND` if `member_id` does not exist
- [ ] Returns HTTP 422 with `INVALID_AMOUNT` if `requested_amount` is missing, zero, or negative
- [ ] Audit log entry generated for every call (see Section 8)

**Should Have (P1):**
- [ ] Response includes `check_timestamp` (ISO 8601 UTC) so the caller knows the snapshot time of the determination
- [ ] Response includes `ineligibility_reasons` array (list of strings) when `eligible=false` — enumerates which checks failed (useful for Member Portal UI)
- [ ] OpenAPI schema annotation on the new endpoint (summary, description, response schema, error codes)

**Nice to Have (P2):**
- [ ] `requested_amount` defaults to 1.00 if not provided (allows a "can this member borrow at all?" check without specifying an amount)

### Non-Functional Requirements

**Performance:**
- Response time: p95 < 500ms under normal load (the CBS collateral query is the likely bottleneck; see implementation notes)
- Throughput: Must support 20 concurrent requests without degradation (not a high-traffic endpoint)
- Resource usage: No caching of eligibility results — always reads current state (regulatory requirement: stale eligibility data could mislead members)

**Security:**
- Authentication: OAuth 2.0 bearer token (existing middleware — no new auth logic needed)
- Authorization: Caller must have scope `member_services:read` OR `advance_eligibility:read` (existing RBAC middleware)
- Data protection: member financial data in response is confidential; TLS 1.3 required (existing)

**Compliance:**
- Audit logging: every call must produce a structured log entry (see Section 8)
- Data retention: audit log entries retained 7 years per SOX schedule
- No SSNs, TINs, or raw advance account numbers in any log output

**Reliability:**
- If the collateral subsystem is unavailable, return HTTP 503 with `COLLATERAL_SERVICE_UNAVAILABLE` and a human-readable message; do not return an eligibility determination when data may be incomplete
- Error handling: all errors must return a structured JSON error body (see Section 5)

---

## 3. Non-Negotiable Constraints

### Technical Constraints

**Language & Framework:**
- Primary language: Python 3.11+
- Framework: FastAPI (existing service uses FastAPI; do not introduce Flask or Django)
- ORM: SQLAlchemy 2.0 (async) — use the existing session factory; do not create a new database connection pool
- Decimal arithmetic: Use Python `Decimal` type for all monetary and ratio calculations — no float

**Architecture Patterns:**
- Follow the existing hexagonal architecture pattern in the Member Services API: route handler → service layer → repository layer
- Route handler in `src/api/routes/members.py` (add to existing file; do not create a new routes file)
- Service logic in `src/services/advance_eligibility.py` (new file)
- Repository queries in `src/repositories/member_repository.py` (add methods to existing file)
- Response models in `src/models/advance_eligibility.py` (new file)

**Dependencies:**
- **Approved (can use):** `fastapi`, `sqlalchemy`, `pydantic` v2, `python-decimal` (stdlib), `structlog` (existing audit logger)
- **Forbidden:** Do not introduce `httpx` calls to an external eligibility service — the calculation must be done in-service from database state. Do not use `float` for monetary arithmetic.

**Infrastructure:**
- Deployment target: existing Docker container on internal Kubernetes cluster (no change)
- Database: PostgreSQL 15 (read from existing `members`, `advances`, `collateral` tables)
- No new infrastructure required

### Security Constraints

**Data Classification:**
- [ ] Restricted (advance account numbers) — these appear in the `advances` table but must NOT be returned in the API response or logs. Use aggregate balance only.
- [x] Confidential (member financials, collateral valuations, advance balances) — all response fields are confidential; handled under existing TLS + RBAC controls
- [ ] Internal — not applicable to this endpoint
- [ ] Public — not applicable

**Authentication & Authorization:**
- Auth method: OAuth 2.0 bearer token via existing `verify_token` FastAPI dependency
- Required scope: `member_services:read` OR `advance_eligibility:read`
- MFA required: Yes (enforced at token issuance by Azure AD — no in-endpoint logic needed)

**Data Handling — CRITICAL:**
- `member_id` is confidential. In ALL log statements, use `sha256(str(member_id).encode()).hexdigest()[:16]` (first 16 hex chars of SHA-256) as the `member_id_hash`. Never log the raw `member_id`.
- `requested_amount`, `aggregate_advance_balance`, `collateral_coverage_ratio`, and `available_capacity` may appear in structured log fields at INFO level (these are financial figures, not PII — acceptable per data handling policy).
- Advance account numbers from the `advances` table are restricted. Do not select them in queries. Use `SUM(principal_balance)` only.
- SSN and TIN fields exist in the `members` table. Do not select them. The query must explicitly name only the columns needed (no `SELECT *`).

### Compliance Constraints

**Audit Requirements:**
- [x] Every eligibility determination call must be logged (success and error)
- [x] Authentication events are logged by existing middleware (no additional work)
- [x] The log entry must conform to the format in Section 8

**Approval Gates:**
- [x] Business stakeholder approval required (Member Portal PM + Member Services lead)
- [x] Technical lead review required
- [x] Security review required (data classification confirmed above; spot check log output in review)
- [x] Compliance review required (audit log entry format verified by Compliance Officer)

**Documentation Required:**
- [x] OpenAPI schema annotations on the endpoint (P1 requirement above)
- [x] Docstring on the service function explaining the three eligibility checks and their thresholds
- [ ] ADR not required — this follows existing patterns; no new architectural decision

---

## 4. Acceptance Criteria (Executable Tests)

### Test 1: Eligible Member with Sufficient Collateral

**Scenario:** Member in good standing with adequate collateral and headroom below the aggregate limit

```gherkin
Given a member with status="active"
  And aggregate outstanding advance principal = $150,000,000
  And pledged collateral lendable value = $200,000,000
  And requested_amount = $30,000,000
When GET /members/{member_id}/advance-eligibility?requested_amount=30000000 is called
  with a valid bearer token with scope "member_services:read"
Then the response is HTTP 200
  And "eligible" is true
  And "collateral_coverage_ratio" >= 1.0000
  And "aggregate_advance_balance" = 150000000.00
  And "available_capacity" > 0
  And "check_timestamp" is a valid ISO 8601 UTC timestamp
  And an audit log entry is written with result="success"
```

**Automation:** integration
**Priority:** P0
**Related Requirement:** Collateral coverage check; aggregate balance limit check

---

### Test 2: Ineligible — Insufficient Collateral Coverage

**Scenario:** Member has requested amount that would exceed their lendable collateral value

```gherkin
Given a member with status="active"
  And aggregate outstanding advance principal = $80,000,000
  And pledged collateral lendable value = $90,000,000
  And requested_amount = $20,000,000
  And lendable_collateral_value (90M) < aggregate_balance + requested_amount (100M)
When GET /members/{member_id}/advance-eligibility?requested_amount=20000000 is called
Then the response is HTTP 200
  And "eligible" is false
  And "reason" contains a human-readable explanation of the collateral shortfall
  And "ineligibility_reasons" contains "INSUFFICIENT_COLLATERAL_COVERAGE"
  And "collateral_coverage_ratio" < 1.0000
  And an audit log entry is written with result="ineligible" and reason="INSUFFICIENT_COLLATERAL_COVERAGE"
```

**Automation:** integration
**Priority:** P0

---

### Test 3: Ineligible — Aggregate Advance Balance Limit Exceeded

**Scenario:** Requested amount would push member over the $500M aggregate advance limit

```gherkin
Given a member with status="active"
  And aggregate outstanding advance principal = $490,000,000
  And pledged collateral lendable value = $600,000,000
  And requested_amount = $20,000,000
  And 490M + 20M = 510M which exceeds the 500M limit
When GET /members/{member_id}/advance-eligibility?requested_amount=20000000 is called
Then the response is HTTP 200
  And "eligible" is false
  And "ineligibility_reasons" contains "AGGREGATE_LIMIT_EXCEEDED"
  And "reason" explains that the requested amount would exceed the $500,000,000 aggregate limit
  And an audit log entry is written with result="ineligible" and reason="AGGREGATE_LIMIT_EXCEEDED"
```

**Automation:** integration
**Priority:** P0

---

### Test 4: Member Not Found

**Scenario:** Caller provides a member_id that does not exist in the members table

```gherkin
Given a member_id that does not exist in the members table
When GET /members/{member_id}/advance-eligibility?requested_amount=1000000 is called
Then the response is HTTP 404
  And the response body is {"error": "MEMBER_NOT_FOUND", "message": "No member found with the provided ID"}
  And an audit log entry is written with result="error" and error_code="MEMBER_NOT_FOUND"
  And the log entry contains member_id_hash (not raw member_id)
```

**Automation:** integration
**Priority:** P0

---

### Test 5: Suspended Member

**Scenario:** Member exists but is in suspended status and cannot borrow

```gherkin
Given a member with status="suspended"
  And otherwise sufficient collateral and headroom
When GET /members/{member_id}/advance-eligibility?requested_amount=1000000 is called
Then the response is HTTP 200
  And "eligible" is false
  And "ineligibility_reasons" contains "MEMBER_NOT_IN_GOOD_STANDING"
  And "reason" explains that the member's current status does not permit advance requests
```

**Automation:** integration
**Priority:** P0

---

### Test 6: Invalid requested_amount

**Scenario:** Caller omits requested_amount or provides a non-positive value

```gherkin
Given a valid member_id
When GET /members/{member_id}/advance-eligibility is called without requested_amount
Then the response is HTTP 422
  And the response body includes error_code="INVALID_AMOUNT"
  And the message explains that requested_amount is required and must be > 0

When GET /members/{member_id}/advance-eligibility?requested_amount=-5000 is called
Then the response is HTTP 422
  And the response body includes error_code="INVALID_AMOUNT"
```

**Automation:** unit
**Priority:** P0

---

### Test 7: Unauthorized Access

**Scenario:** Caller presents a token without the required scope

```gherkin
Given a bearer token with scope "advance_origination:write" (not "member_services:read")
When GET /members/{member_id}/advance-eligibility?requested_amount=1000000 is called
Then the response is HTTP 403
  And no eligibility determination is made
  And no member data is accessed
  And the existing auth middleware logs the access denial
```

**Automation:** integration
**Priority:** P0

---

### Test Matrix

| Test ID | Scenario | Type | Priority | Status |
|---------|----------|------|----------|--------|
| T001 | Eligible member, full happy path | integration | P0 | pending |
| T002 | Ineligible: collateral shortfall | integration | P0 | pending |
| T003 | Ineligible: aggregate limit exceeded | integration | P0 | pending |
| T004 | Member not found (404) | integration | P0 | pending |
| T005 | Suspended member | integration | P0 | pending |
| T006 | Invalid requested_amount (422) | unit | P0 | pending |
| T007 | Unauthorized scope (403) | integration | P0 | pending |
| T008 | Multiple ineligibility reasons (collateral + standing) | integration | P1 | pending |
| T009 | Member with zero collateral on file | integration | P1 | pending |
| T010 | Probationary member status | integration | P1 | pending |
| T011 | Collateral service unavailable (503) | integration | P1 | pending |
| T012 | Decimal precision: ratio exactly 1.0000 (boundary) | unit | P1 | pending |

---

## 5. Edge Cases & Error Handling

### Edge Cases

| Scenario | Expected Behavior | Test Coverage |
|----------|------------------|---------------|
| Member has no collateral on file (zero collateral records) | `eligible=false`, `collateral_coverage_ratio=0.0000`, `ineligibility_reasons=["INSUFFICIENT_COLLATERAL_COVERAGE"]`, `available_capacity=0.00` | T009 |
| Member has collateral records but all have `lendable_value=0` (e.g., zero-value pledges) | Same as no collateral — treat lendable value as 0 | T009 |
| Member has no open advances (first-time borrower) | `aggregate_advance_balance=0.00`; eligibility determined by collateral coverage vs. requested_amount alone | T001 variant |
| Member in `probationary` status | Treat same as `suspended` — ineligible; `ineligibility_reasons=["MEMBER_NOT_IN_GOOD_STANDING"]` | T010 |
| Multiple ineligibility conditions simultaneously | All failed checks appear in `ineligibility_reasons`; `eligible=false` | T008 |
| `requested_amount` exactly equals `available_capacity` (boundary) | `eligible=true`; `collateral_coverage_ratio` should be exactly 1.0000 | T012 |
| `collateral_coverage_ratio` exactly 1.0000 (coverage exactly meets requirement) | `eligible=true` (≥1.0000 is passing) | T012 |

### Error Handling

| Error Condition | HTTP Status | Error Code | User Message | Log Level |
|----------------|-------------|------------|--------------|-----------|
| member_id not found | 404 | MEMBER_NOT_FOUND | "No member found with the provided ID" | INFO |
| requested_amount missing | 422 | INVALID_AMOUNT | "requested_amount is required and must be a positive number" | INFO |
| requested_amount ≤ 0 | 422 | INVALID_AMOUNT | "requested_amount must be greater than zero" | INFO |
| Invalid token / no token | 401 | UNAUTHORIZED | (handled by existing middleware) | WARN |
| Insufficient token scope | 403 | FORBIDDEN | (handled by existing middleware) | WARN |
| Collateral service/DB unavailable | 503 | COLLATERAL_SERVICE_UNAVAILABLE | "Eligibility check is temporarily unavailable. Please try again in a few minutes." | ERROR |
| Unexpected server error | 500 | INTERNAL_ERROR | "An unexpected error occurred. Please contact Member Services." | ERROR |

**Error response shape (all errors must use this structure):**

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable explanation",
  "request_id": "uuid-v4-correlation-id"
}
```

### Recovery Procedures

**Automatic Recovery:**
- Database connection: SQLAlchemy connection pool handles transient connection failures with built-in retry (existing pool config — no changes)
- Collateral service unavailable: return HTTP 503 immediately (no retry at this layer); the caller (Member Portal) handles retry with user messaging

**Manual Intervention Required:**
- If HTTP 503 persists for >5 minutes during business hours: page on-call platform engineer (existing PagerDuty integration)
- Any HTTP 500 from this endpoint: alert fires in Splunk; Member Services on-call is notified

---

## 6. Rollback Conditions

### Automatic Rollback Triggers

| Metric | Threshold | Measurement Window | Action |
|--------|-----------|-------------------|--------|
| Error rate (5xx) on this endpoint | > 10% | 5 minutes | Alert on-call; manual rollback decision |
| Response time p95 | > 2 seconds | 10 minutes | Alert on-call; investigate CBS query |
| Failed health checks | 3 consecutive | 1 minute | Kubernetes liveness probe restarts pod |

*Note: This endpoint is read-only and non-mutating. Rollback risk is low. There is no data written to revert.*

### Manual Rollback Procedure

**Before Rollback:**
1. [ ] Confirm the issue is from this endpoint (check APM traces by endpoint path)
2. [ ] Notify team in `#member-services-api` Slack channel with incident number
3. [ ] Get approval from Tech Lead

**Rollback Steps:**
1. Revert the merge commit via `git revert <merge-commit-sha>` and push to main
2. GitHub Actions CI runs automatically; verify all checks pass on the revert commit
3. Deploy revert via existing Kubernetes rollout process
4. Verify `/health` endpoint returns 200 after deploy

**Post-Rollback:**
1. [ ] Verify Member Portal eligibility indicator is hidden (graceful degradation mode)
2. [ ] Document root cause in incident ticket
3. [ ] Schedule post-mortem within 24 hours

---

## 7. Data Classification & Handling

### Data Types Involved

| Data Type | Classification | Source | Destination | Handling |
|-----------|---------------|--------|-------------|----------|
| member_id (input) | Confidential | API request path | Audit log | Log as SHA-256 hash prefix only; never raw |
| member status | Confidential | `members.status` column | API response (indirectly via eligible=false reason) | Not returned directly; only reflected in reason string |
| aggregate_advance_balance | Confidential | `SUM(advances.principal_balance)` | API response | Returned as Decimal; not logged |
| collateral lendable value | Confidential | `SUM(collateral.estimated_value * (1-haircut_rate))` | API response | Returned as Decimal; not logged |
| advance account numbers | Restricted | `advances` table | NOT USED | Must not be SELECTed or logged |
| SSN / TIN | Restricted | `members` table | NOT USED | Must not be SELECTed or logged |
| requested_amount | Confidential | API query parameter | Audit log | Logged as a numeric value (financial figure, not PII) |
| collateral_coverage_ratio | Confidential | Calculated | API response | Returned; not logged |
| check_timestamp | Internal | Server timestamp | API response | UTC ISO 8601 |

### Data Flow Diagram

```
API Caller (Member Portal / Representative)
    |  GET /members/{member_id}/advance-eligibility?requested_amount=X
    |  Bearer token (OAuth 2.0)
    ▼
FastAPI Route Handler
    |  1. Validate token scope (existing middleware)
    |  2. Validate requested_amount > 0
    ▼
AdvanceEligibilityService
    |  3. Look up member status (members table) — select id, status only
    |  4. Compute aggregate advance balance (advances table) — SUM(principal_balance)
    |  5. Compute lendable collateral value (collateral table) — SUM(estimated_value * (1-haircut_rate))
    |  6. Run three eligibility checks
    |  7. Build response
    ▼
structlog audit logger → Splunk (7-year retention)
    |
    ▼
HTTP 200 Response (eligible, reason, ratios, timestamp)
```

### Retention & Deletion

**Retention Policy:**
- API response data: not persisted (read-only endpoint, no storage)
- Audit log entries: 7 years per SOX schedule
- No member data is written or modified by this endpoint

---

## 8. Audit Trail Requirements

### Events to Log

| Event | Data to Capture | Log Level | Retention |
|-------|----------------|-----------|-----------|
| Eligibility check completed (eligible=true) | member_id_hash, requested_amount, result=eligible, check_timestamp | INFO | 7 years |
| Eligibility check completed (eligible=false) | member_id_hash, requested_amount, result=ineligible, ineligibility_reasons, check_timestamp | INFO | 7 years |
| Member not found | member_id_hash, requested_amount, result=error, error_code=MEMBER_NOT_FOUND | INFO | 7 years |
| Validation error (invalid amount) | error_code=INVALID_AMOUNT (no member_id in log — request rejected before lookup) | INFO | 90 days |
| Service unavailable | error_code=COLLATERAL_SERVICE_UNAVAILABLE, exception_type | ERROR | 7 years |
| Unexpected error | error_code=INTERNAL_ERROR, exception_type (no stack trace to avoid leaking internals) | ERROR | 7 years |

### Log Format

Every audit log entry must use `structlog` (existing logger) and produce this JSON structure:

```json
{
  "timestamp": "2026-05-15T14:32:00.123456Z",
  "level": "info",
  "service": "member-services-api",
  "correlation_id": "uuid-v4-from-request-header-or-generated",
  "actor": {
    "type": "api-agent",
    "id": "claude-code",
    "human_supervisor": "j.knox@apexfinancial.example.com"
  },
  "action": "advance_eligibility.checked",
  "resource": {
    "type": "member",
    "id_hash": "a3f2c1b4e5d67890"
  },
  "request": {
    "requested_amount": 30000000.00,
    "endpoint": "GET /members/{member_id}/advance-eligibility"
  },
  "result": "eligible",
  "ineligibility_reasons": [],
  "check_timestamp": "2026-05-15T14:32:00.100Z",
  "duration_ms": 87,
  "metadata": {
    "spec_id": "SPEC-2026-05-15-001",
    "pilot_id": "PILOT-2026-AFC-001"
  }
}
```

**Implementation note:** Use `structlog.get_logger().info("advance_eligibility.checked", **log_fields)`. The `actor.human_supervisor` field must be populated from the JWT claim `email` on the bearer token. If the claim is absent, use `"unknown"`.

### Audit Review

**Frequency:** Monthly during pilot; quarterly thereafter
**Reviewer:** Compliance Officer, Apex Financial Corp
**Access:** Read-only Splunk role `compliance-audit` — log fields that include financial figures are visible; raw member IDs are never present

---

## 9. Implementation Notes

### Suggested Approach

**High-level strategy:**
Implement as a pure read path: three database queries, three boolean checks, one structured response. No external service calls. No caching. No writes.

**Key design decisions:**
1. **Use `Decimal` throughout:** The `collateral_coverage_ratio` must be precise to 4 decimal places. Convert all database numeric values to `Decimal` on arrival from SQLAlchemy. Use `ROUND(ratio, 4)` in Python before serializing.
2. **Do not aggregate in application code if avoidable:** Push `SUM(principal_balance)` and `SUM(estimated_value * (1 - haircut_rate))` to PostgreSQL. This is more efficient than loading all advance rows and summing in Python.
3. **Return HTTP 200 for ineligible members:** Ineligibility is a valid business outcome, not an error. Only use 4xx/5xx for request errors or system failures.
4. **`ineligibility_reasons` is always present in the response:** Empty list `[]` when eligible, one or more codes when ineligible. This simplifies Member Portal rendering logic.

### File Structure

```
src/
├── api/
│   └── routes/
│       └── members.py           ← ADD new route here (existing file)
├── services/
│   └── advance_eligibility.py   ← NEW: service layer with three eligibility checks
├── models/
│   └── advance_eligibility.py   ← NEW: Pydantic response/request models
└── repositories/
    └── member_repository.py     ← ADD new query methods here (existing file)

tests/
├── integration/
│   └── test_advance_eligibility.py   ← NEW: integration tests (T001–T011)
└── unit/
    └── test_advance_eligibility_service.py  ← NEW: unit tests (T006, T012)
```

### Dependencies to Add

No new dependencies required. All needed libraries (`fastapi`, `sqlalchemy`, `pydantic`, `structlog`, `decimal`) are already in `requirements.txt`.

### API Design

**Endpoint:** `GET /members/{member_id}/advance-eligibility`

**Path parameter:** `member_id` — integer (existing member ID format)

**Query parameter:** `requested_amount` — decimal string, required, must be > 0

**Response (200 — eligible):**
```json
{
  "eligible": true,
  "reason": "Member meets all eligibility requirements for the requested advance amount.",
  "ineligibility_reasons": [],
  "collateral_coverage_ratio": "1.3333",
  "aggregate_advance_balance": "150000000.00",
  "available_capacity": "50000000.00",
  "check_timestamp": "2026-05-15T14:32:00.100Z"
}
```

**Response (200 — ineligible):**
```json
{
  "eligible": false,
  "reason": "The requested advance amount would exceed your available collateral capacity.",
  "ineligibility_reasons": ["INSUFFICIENT_COLLATERAL_COVERAGE"],
  "collateral_coverage_ratio": "0.9000",
  "aggregate_advance_balance": "80000000.00",
  "available_capacity": "10000000.00",
  "check_timestamp": "2026-05-15T14:32:00.100Z"
}
```

**Response (404):**
```json
{
  "error": "MEMBER_NOT_FOUND",
  "message": "No member found with the provided ID",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (422):**
```json
{
  "error": "INVALID_AMOUNT",
  "message": "requested_amount is required and must be a positive number",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (503):**
```json
{
  "error": "COLLATERAL_SERVICE_UNAVAILABLE",
  "message": "Eligibility check is temporarily unavailable. Please try again in a few minutes.",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 10. Approval Checklist

### Pre-Implementation Approvals

- [ ] **Business Stakeholder (Member Services Lead)**
  - Name: _________________
  - Date: _______
  - Notes: Confirm $500M aggregate limit is the current regulatory threshold

- [ ] **Business Stakeholder (Member Portal PM)**
  - Name: _________________
  - Date: _______
  - Notes: Confirm response shape satisfies Member Portal integration requirements

- [ ] **Technical Lead (Member Services)**
  - Name: _________________
  - Date: _______
  - Notes: Confirm file placement and naming conventions

- [ ] **Security Review**
  - Name: _________________
  - Date: _______
  - Notes: Confirm member_id_hash approach satisfies data handling policy

- [ ] **Compliance Review**
  - Name: _________________
  - Date: _______
  - Notes: Confirm audit log format and retention satisfy SOX + FHFA requirements

### Spec Quality Checklist

- [x] All sections complete
- [x] Acceptance criteria are executable (Gherkin format)
- [x] Edge cases identified (zero collateral, suspended, probationary, boundary ratio)
- [x] Rollback procedure defined
- [x] Security constraints documented
- [x] Compliance requirements captured
- [x] Estimated effort realistic (16 hours)
- [x] Dependencies approved (no new dependencies)

### Agent Readiness Checklist

- [x] File paths specified for all new and modified files
- [x] Code patterns defined (Decimal arithmetic, structlog, SHA-256 hash for member_id)
- [x] Test expectations clear (12 test cases with Gherkin format)
- [x] Error handling specified (all HTTP status codes and error codes defined)
- [x] Constraints explicit (no SELECT *, no float, no advance account numbers in logs)

---

## Appendix A: Reference Materials

### Related Documents

- [Pilot Proposal](./pilot-proposal.md)
- [FRAME Framework Overview](../../docs/framework-overview.md)
- [Security Guardrails](../../docs/security-guardrails.md)
- [Agent-Ready Spec Template](../../templates/agent-ready-spec.md)
- [Golden Task Set](../../tools/golden-task-set/) — GT-004 and GT-005 are related API extension tasks

### Glossary

| Term | Definition |
|------|------------|
| Advance | A loan made by Apex Financial Corp to a member institution, collateralized by pledged assets |
| Lendable value | The pledged collateral value after applying the regulatory haircut rate (e.g., 20% haircut on whole loans means lendable value = 80% of estimated value) |
| Haircut rate | The regulatory discount applied to collateral estimated value to determine the amount the organization will lend against it |
| Aggregate advance balance | The total outstanding principal across all open advances for a single member |
| Member standing | The operational status of a member institution: `active`, `probationary`, or `suspended` |
| CBS | Core Banking System — the legacy system of record for member and advance data |
| FHFA | Federal Housing Finance Agency — primary regulator of regional financial institutions |

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-05-15 | J. Knox | Initial draft |

---

**Spec Status:** draft

**Last Updated:** 2026-05-15

**Next Review Date:** 2026-05-30 (before Week 1 kickoff)
