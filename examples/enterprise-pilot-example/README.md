# Enterprise Pilot Example: Internal Compliance Reporting

This example demonstrates the Agentic SDLC Framework for an enterprise environment — specifically for Apex Financial Corp or similar regulated financial institutions.

## Project Overview

**Goal:** Automate the generation of internal compliance reports to:
- Reduce manual effort from 4 hours to 15 minutes per month
- Eliminate copy-paste errors
- Improve audit trail completeness
- Demonstrate agentic development in regulated environment

**Why This Project:**
- Internal use only (low regulatory risk)
- Clear business value
- Repetitive, well-defined process
- Good learning opportunity
- Can demonstrate framework to stakeholders

**Tech Stack:**
- Python 3.11+
- Pandas for data processing
- SQLAlchemy for database access
- Jinja2 for report templating
- pytest for testing
- GitHub Enterprise for CI/CD

---

## Phase 0: Intake & Triage

### Intake Ticket

```markdown
---
intake_id: INTAKE-2025-01-001
date: 2025-01-15
requester: compliance-team@apexfinancial.example.com
business_unit: Compliance
---

# Project Intake: Compliance Report Automation

## Idea
Automate the monthly compliance report generation process.

## Business Value
- **Current pain:** Manual process takes 4 hours, error-prone
- **Desired outcome:** Automated generation with 15-minute review
- **Success metric:** Reduce manual effort by 90%, zero data errors

## Scope
- Read from 3 internal databases
- Apply business rules
- Generate formatted report
- Email to stakeholders
- Log all access for audit

## Technical Constraints
- Must use approved tech stack
- No external APIs (data stays internal)
- Must maintain audit trail
- FHFA compliance requirements

## Risk Assessment
- **Risk:** Data classification → Mitigation: Internal data only
- **Risk:** Audit requirements → Mitigation: Complete logging

## Compliance Notes
- Data classification: Internal
- Regulatory impact: Low (internal reporting)
- Audit requirements: All data access logged
- Approval needed: Compliance officer, IT security

## Decision: ✅ GO
- Clear scope
- Low risk
- High value
- Compliance approved
```

### Feasibility Assessment

**Technical Feasibility:** ✅ High
- Well-defined data sources
- Clear transformation logic
- Standard reporting format

**Regulatory Feasibility:** ✅ Approved
- Internal use only
- No member PII
- Audit trail maintained

**Resource Requirements:**
- 1 engineer, 4 weeks
- No additional infrastructure
- Uses existing databases

---

## Phase 1: Executable Spec

See [spec-compliance-reporting.md](spec-compliance-reporting.md) for the complete agent-ready specification.

### Key Decisions from Spec

1. **Data Access:** Read-only SQL views (no direct table access)
2. **Report Format:** Excel with multiple tabs (stakeholder requirement)
3. **Scheduling:** Airflow (existing enterprise scheduler)
4. **Distribution:** Secure email (existing infrastructure)
5. **Audit:** All actions logged to Splunk

### Spec Quality Notes

**What worked:**
- Explicit data classification helped security review
- Gherkin tests for business rules were clear
- Edge cases around data quality were well-defined

**Compliance additions:**
- Added data lineage requirements
- Specified retention policies
- Defined approval workflows

---

## Phase 2: Design & Architecture

### ADR-001: Report Generation Architecture

**Decision:** Use batch processing with Airflow

**Rationale:**
- Monthly cadence (not real-time)
- Existing Airflow infrastructure
- Audit trail built-in
- Retry capability

**Alternatives considered:**
- Real-time API: Rejected (overkill, no need)
- Direct SQL in Excel: Rejected (security, maintainability)
- Custom scheduler: Rejected (use existing infrastructure)

See [adr-001-report-architecture.md](adr-001-report-architecture.md)

### ADR-002: Data Access Pattern

**Decision:** Read-only SQL views with service account

**Rationale:**
- Least privilege principle
- Views encapsulate business logic
- Easy to audit (single service account)
- No direct table access

**Security considerations:**
- Service account credentials in HashiCorp Vault
- Connection encrypted (TLS 1.3)
- Query logging enabled

See [adr-002-data-access.md](adr-002-data-access.md)

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Airflow Scheduler                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   Extract   │───→│ Transform   │───→│   Load      │      │
│  │   (SQL)     │    │ (Pandas)    │    │ (Excel)     │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                  │                  │                │
│         ↓                  ↓                  ↓                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Audit Logger → Splunk                │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                           │
         ↓                           ↓
┌─────────────────┐         ┌─────────────────┐
│  Source DBs     │         │  Secure Email   │
│  (Read-only)    │         │  (Encrypted)    │
└─────────────────┘         └─────────────────┘
```

### Security Architecture

```
User Request → Airflow → Service Account → SQL Views
                  ↓            ↓
            Audit Log    Vault (creds)
                  ↓
              Splunk
```

---

## Phase 3: Implementation

### Milestone 1: Data Access Layer

**Handoff Packet:** [handoff-packets/handoff-001.md](handoff-packets/handoff-001.md)

**What was built:**
- Database connection manager
- SQL view abstractions
- Query logging
- Error handling
- Unit tests with mocked databases

**Time:** 3 days (vs estimated 5 days)

**Agent approach:**
1. Planner broke into 6 tasks
2. Executor implemented each
3. Security agent reviewed for SQL injection
4. Reviewer checked against spec

**Security findings:**
- 1 medium: Connection string logging (fixed)
- All queries parameterized ✅

### Milestone 2: Business Logic & Transformations

**Handoff Packet:** [handoff-packets/handoff-002.md](handoff-packets/handoff-002.md)

**What was built:**
- Data transformation functions
- Business rule validation
- Data quality checks
- Error handling for edge cases

**Time:** 4 days (vs estimated 6 days)

**Challenge:** Business rules were complex
- Required clarification from compliance
- Updated spec with examples
- Agent adapted to new requirements

**Quality metrics:**
- 96% test coverage
- All business rules have tests
- Data quality checks catch 100% of known bad data patterns

### Milestone 3: Report Generation & Distribution

**Handoff Packet:** [handoff-packets/handoff-003.md](handoff-packets/handoff-003.md)

**What was built:**
- Excel report generation
- Email distribution
- Airflow DAG
- Monitoring and alerting

**Time:** 3 days (vs estimated 5 days)

**Compliance additions:**
- Pre-send validation
- Recipient authorization check
- Delivery confirmation logging

---

## Phase 4: Validation & Security Pass

### Security Scan Results

| Check | Status | Findings |
|-------|--------|----------|
| Secrets scanning | ✅ | Clean |
| SAST (Bandit) | ✅ | No issues |
| SCA (Snyk) | ✅ | No vulnerabilities |
| SQL injection | ✅ | All queries parameterized |
| Data classification | ✅ | Internal only |
| Access controls | ✅ | Service account properly scoped |

### Compliance Review

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Audit logging | ✅ | All actions logged to Splunk |
| Data lineage | ✅ | Source to report tracked |
| Retention policy | ✅ | 7-year retention configured |
| Approval workflow | ✅ | Compliance sign-off obtained |
| Access review | ✅ | Service account documented |

### Test Results

| Suite | Tests | Passed | Coverage |
|-------|-------|--------|----------|
| Unit | 45 | 45 ✅ | 96% |
| Integration | 18 | 18 ✅ | - |
| E2E | 6 | 6 ✅ | - |
| Security | 12 | 12 ✅ | - |

### Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Report generation | < 5 min | 2.3 min | ✅ |
| Data extraction | < 2 min | 1.1 min | ✅ |
| Email delivery | < 1 min | 0.4 min | ✅ |
| Total runtime | < 10 min | 3.8 min | ✅ |

---

## Phase 5: Deployment

### Pre-Deployment Checklist

- [x] Security scan clean
- [x] Compliance review passed
- [x] Performance requirements met
- [x] Runbook created
- [x] Monitoring configured
- [x] Rollback tested
- [x] Stakeholder training complete

### Deployment Strategy

**Week 1:** Shadow mode
- Run alongside manual process
- Compare outputs
- No stakeholder notification

**Week 2:** Canary (5%)
- Send to 1 stakeholder
- Monitor for issues
- Manual backup ready

**Week 3:** Expanded (50%)
- Send to half of stakeholders
- Daily check-ins
- Full rollback capability

**Week 4:** Full rollout
- All stakeholders
- Manual process deprecated
- Monitor for 2 weeks

### Rollback Triggers

- Data quality check failures > 0
- Delivery failures > 1
- Stakeholder complaints
- Security alerts

### Rollback Procedure

1. Disable Airflow DAG
2. Re-enable manual process
3. Notify stakeholders
4. Investigate issue
5. Fix and redeploy

---

## Phase 6: Operations

### Monitoring Dashboard

| Metric | Current | Alert Threshold |
|--------|---------|-----------------|
| Success rate | 100% | < 95% |
| Runtime | 3.8 min | > 10 min |
| Data quality | 100% | < 99% |
| Delivery success | 100% | < 95% |

### Incident Response

**Severity 1 (P0):**
- Report not generated
- Page on-call immediately
- Manual process activated
- Root cause within 4 hours

**Severity 2 (P1):**
- Report generated but data quality issues
- Notify during business hours
- Manual review required
- Fix within 24 hours

**Severity 3 (P2):**
- Minor formatting issues
- Ticket created
- Fix next sprint

### Continuous Improvement

**Monthly review:**
- Stakeholder feedback
- Error rates
- Performance trends
- Security scan results

**Quarterly review:**
- Framework effectiveness
- Process improvements
- Tool updates
- Training needs

---

## Metrics & Results

### Framework Effectiveness

| Metric | Traditional | Agentic | Improvement |
|--------|-------------|---------|-------------|
| Development time | 6 weeks | 2.5 weeks | 58% faster |
| First-pass PR rate | 45% | 78% | +33 points |
| Defects found | 12 | 3 | 75% fewer |
| Security issues | 3 | 1 | 67% fewer |
| Documentation | 40% | 95% | +55 points |

### Business Value

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Monthly effort | 4 hours | 15 minutes | 94% reduction |
| Error rate | 2/year | 0 | 100% reduction |
| Audit findings | 1/quarter | 0 | 100% reduction |
| Stakeholder satisfaction | 6/10 | 9/10 | +3 points |

### Spec Quality Impact

Specs that produced clean first drafts:
- Data access layer (clear requirements)
- Report generation (explicit format requirements)

Specs that needed rework:
- Business rules (complexity underestimated)
- Email distribution (security requirements added)

### Lessons Learned

**What worked:**
1. Executable specs with Gherkin tests
2. Multi-agent coordination
3. Automated security scanning
4. Compliance review early in process
5. Shadow deployment caught issues

**What to improve:**
1. Spend more time on business rule examples
2. Include compliance earlier in spec process
3. Add more data quality edge cases
4. Document stakeholder communication preferences

**Surprises:**
- Agent was conservative with dependencies (good for compliance)
- Generated audit logging was comprehensive
- Compliance team appreciated the transparency

---

## Files

```
enterprise-pilot-example/
├── README.md                          # This file
├── spec-compliance-reporting.md       # Agent-ready spec
├── adr-001-report-architecture.md   # Architecture decision
├── adr-002-data-access.md           # Security decision
├── compliance-checklist.md          # Compliance requirements
├── handoff-packets/
│   ├── handoff-001.md              # Milestone 1
│   ├── handoff-002.md              # Milestone 2
│   └── handoff-003.md              # Milestone 3
├── src/
│   ├── __init__.py
│   ├── extract.py                   # Data extraction
│   ├── transform.py                 # Business logic
│   ├── load.py                      # Report generation
│   ├── audit.py                     # Audit logging
│   ├── config.py                    # Configuration
│   └── exceptions.py                # Custom exceptions
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── dags/
│   └── compliance_report.py         # Airflow DAG
├── templates/
│   └── report_template.xlsx         # Excel template
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Stakeholder Feedback

### Compliance Team

> "The audit trail is exactly what we needed. Every data access is logged with context. This sets the standard for future automation projects."

### IT Security

> "The security review was straightforward because the spec explicitly addressed our concerns. The agent-generated code followed our patterns."

### Business Stakeholders

> "Reports arrive on time, every time. The data quality checks caught an issue that would have taken hours to find manually."

### Engineering Team

> "The framework forced us to think through requirements upfront. The executable specs meant less back-and-forth during implementation."

---

## Using This Example

To use this framework for your own enterprise pilot:

1. **Select a workflow:**
   - Internal use (low risk)
   - Clear business value
   - Well-defined process
   - Stakeholder support

2. **Customize the spec template:**
   - Add your compliance requirements
   - Define your data classification
   - Specify your approval workflows

3. **Run the guardrail scripts:**
   ```bash
   python tools/guardrail-scripts/validate-spec.py spec-your-project.md
   ```

4. **Get approvals early:**
   - Compliance review
   - Security review
   - Business sponsor

5. **Start with shadow mode:**
   - Prove value before full rollout
   - Build confidence with stakeholders
   - Learn and iterate

See the [main framework documentation](../README.md) for full details.

---

## Next Steps

This pilot demonstrated the framework in a regulated environment. Next steps:

1. **Expand to more workflows:**
   - Data validation pipelines
   - Report generation (other types)
   - Internal tools

2. **Improve the framework:**
   - Refine templates based on learnings
   - Add more compliance automation
   - Build stakeholder training materials

3. **Scale the approach:**
   - Train more teams
   - Establish center of excellence
   - Share patterns across organization

4. **Measure long-term value:**
   - Track over 6-12 months
   - Compare to traditional projects
   - Calculate ROI
