# Security Guardrails

## Overview

This document defines the security controls for the Agentic SDLC Framework. Every layer — pre-commit, CI/CD, pre-deploy, and runtime — is covered with concrete configuration examples. The financial services context (banking) shapes the data classification model and the regulated industry requirements section.

The underlying principle: guardrails are not checkboxes. They are the mechanism that makes agentic development safe. Without them, agents that move fast will move fast in the wrong direction.

---

## Data Classification

### Classification Levels

Four levels, ordered from most to least sensitive. Every piece of data your agents touch must be classified before implementation begins.

#### Restricted

Data that, if exposed, would result in regulatory enforcement action, civil liability, or material harm to individuals.

```yaml
restricted:
  description: "Highest sensitivity — regulatory or legal consequence if exposed"
  allowed_endpoints: []          # No AI model endpoints permitted
  ai_model_use: prohibited       # Cannot be sent to any external AI model
  requires_approval: true        # Explicit CISO + legal approval for any new handling
  encryption_at_rest: AES-256
  encryption_in_transit: TLS-1.3
  audit_required: true
  retention: "7 years minimum (regulatory)"
  examples:
    - Social Security Numbers (SSN)
    - Tax Identification Numbers (TIN)
    - customer account numbers
    - customer advance account balances (individual)
    - Wire transfer details
    - Loan collateral records (individual)
    - HMDA reportable loan data (combined with PII)
    - regional financial institution regulatory examination findings
    - Employee payroll data
    - Authentication credentials and private keys
```

#### Confidential

Data that is sensitive to the organization or its members but does not carry individual-level regulatory liability if handled properly.

```yaml
confidential:
  description: "Business-sensitive — member relationships, financials, internal strategy"
  allowed_endpoints:
    - internal-api              # Internal tooling only
    - on-premise-llm            # Locally hosted models only
  ai_model_use: internal_only   # On-premise or VPC-hosted models only
  requires_approval: true       # Technical lead approval for new data flows
  encryption_at_rest: AES-256
  encryption_in_transit: TLS-1.3
  audit_required: true
  retention: "7 years (financial records)"
  examples:
    - member institution financial statements
    - Aggregated advance and collateral positions
    - Capital adequacy calculations
    - ALM model outputs and assumptions
    - Dividend records (institution-level)
    - Member institution examination summaries
    - Internal credit ratings
    - Vendor contracts and pricing
    - Strategic planning documents
    - Non-public market analysis
```

#### Internal

Data used in normal business operations that is not intended for public consumption but carries limited risk if exposed.

```yaml
internal:
  description: "Business operational data — limited external risk"
  allowed_endpoints:
    - internal-api
    - approved-saas             # Approved SaaS vendors with DPA in place
    - cloud-llm-with-dpa        # Cloud AI models with signed data processing agreements
  ai_model_use: approved_vendors_only
  requires_approval: false      # Standard use permitted within policy
  encryption_at_rest: AES-256
  encryption_in_transit: TLS-1.2+
  audit_required: false         # Recommended, not required
  retention: "3 years or per business need"
  examples:
    - Internal project documentation
    - Process runbooks and SOPs
    - Aggregated (anonymized) reporting metrics
    - Architecture diagrams (non-sensitive systems)
    - Meeting notes and action items
    - Staff directory
    - Internal software documentation
    - Test data (synthetic, no real member data)
    - Application logs (no PII)
```

#### Public

Data explicitly approved for external publication or that is already publicly available.

```yaml
public:
  description: "No restriction — approved for external use"
  allowed_endpoints: ["*"]
  ai_model_use: unrestricted
  requires_approval: false
  encryption_at_rest: recommended
  encryption_in_transit: TLS-1.2+
  audit_required: false
  examples:
    - Published annual reports
    - Public regulatory filings (FHFA)
    - Public press releases
    - public website content
    - Published interest rate indices
    - Publicly available market data
    - Open source code
    - Marketing materials
```

### Data Classification Decision Tree

Use this when classifying a new data type before writing a spec:

```
Does this data identify a specific individual? (SSN, TIN, account number)
  YES → RESTRICTED

Is this data about a specific AFC member institution's financial position,
relationship, or strategy?
  YES → CONFIDENTIAL

Is this data used internally for operations but not intended for public release?
  YES → INTERNAL

Is this data already published or approved for public release?
  YES → PUBLIC
```

When in doubt, classify up. Reclassifying down requires compliance review.

### Enforcing Classification in Specs

Every agent-ready spec must declare data classification in Section 3 (Non-Negotiable Constraints). The validation script checks for this:

```bash
python tools/guardrail-scripts/validate-spec.py specs/SPEC-001.md
# ✅ Data classification: internal
# ✅ Classification consistent with allowed endpoints
```

If a spec lists `confidential` or `restricted` data, the CI pipeline blocks deployment until a security review approval is recorded in the audit trail.

---

## Pre-Commit Hooks

Pre-commit hooks run on every `git commit`. They are the first and cheapest line of defense. Configuration goes in `.pre-commit-config.yaml` at the repository root.

### Complete Pre-Commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  # ─── Secret Scanning ─────────────────────────────────────────────────────

  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.63.11
    hooks:
      - id: trufflehog
        name: TruffleHog (verified secrets)
        entry: trufflehog filesystem --no-update --only-verified .
        language: system
        pass_filenames: false
        always_run: true

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        name: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: >
          (?x)^(
            .*\.example|
            .*\.template|
            tests/.*|
            examples/.*
          )$

  # ─── Python Linting ───────────────────────────────────────────────────────

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        name: ruff (lint + fix)
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
        name: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        name: mypy (type check)
        additional_dependencies: [types-all]

  # ─── General File Hygiene ─────────────────────────────────────────────────

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        args: [--allow-multiple-documents]
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: detect-private-key
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: no-commit-to-branch
        args: ['--branch', 'main', '--branch', 'master']

  # ─── Security File Checks ─────────────────────────────────────────────────

  - repo: local
    hooks:
      - id: no-sensitive-files
        name: Block sensitive file types
        entry: bash -c 'files=$(git diff --cached --name-only | grep -E "\.(pem|key|p12|pfx|jks|keystore|env)$"); if [ -n "$files" ]; then echo "Blocked: $files"; exit 1; fi'
        language: system
        pass_filenames: false

      - id: check-data-classification
        name: Check spec data classification
        entry: bash -c 'for spec in $(git diff --cached --name-only | grep "specs/.*\.md$"); do python tools/guardrail-scripts/validate-spec.py "$spec"; done'
        language: system
        pass_filenames: false
```

### Installing and Verifying

```bash
# Install
pip install pre-commit
pre-commit install

# Run against all files (initial setup, verify nothing breaks)
pre-commit run --all-files

# Create detect-secrets baseline (run once per repo)
detect-secrets scan > .secrets.baseline
git add .secrets.baseline
```

### When a Pre-Commit Hook Fails

**TruffleHog fires on a real secret:**
1. Do not suppress the hook
2. Revoke the credential immediately (rotate API key, change password)
3. Check git log to confirm the secret was never pushed
4. If it was pushed, treat as a security incident — contact security team

**TruffleHog fires on a false positive:**
```bash
# Add to .trufflehog-ignore (per-file exceptions)
echo "path/to/false-positive-file" >> .trufflehog-ignore

# Or annotate the line in code
API_EXAMPLE = "sk-example-not-real"  # trufflehog:ignore
```

**detect-secrets fires on a false positive:**
```bash
# Update the baseline to acknowledge the false positive
detect-secrets scan > .secrets.baseline
# Review the diff carefully before committing the updated baseline
```

---

## Pre-Build Checks (CI/CD)

Pre-build checks run in CI on every pull request and every push to main. These catch issues that are too slow or environment-dependent for pre-commit.

### SAST (Static Application Security Testing)

SAST analyzes source code without executing it, finding common vulnerability patterns.

**Bandit (Python):**

```yaml
# In CI workflow
- name: Bandit SAST
  run: |
    pip install bandit[toml]
    bandit -r src/ \
      --level medium \
      --confidence medium \
      --format json \
      --output bandit-report.json
    # Also print human-readable for CI log
    bandit -r src/ --level medium --confidence medium
```

**Bandit configuration for financial services (stricter defaults):**

```toml
# pyproject.toml
[tool.bandit]
targets = ["src"]
skips = []          # Do not skip any test classes
level = "medium"    # Fail on medium and above
confidence = "medium"

# Financial services: key test classes to enforce
# B105/B106/B107 - hardcoded password patterns
# B303/B304/B305 - weak cryptography (MD5, ECB mode)
# B311          - random module (not cryptographically secure)
# B501          - requests without cert validation
# B602/B603     - subprocess with shell=True (injection risk)
# B608          - hardcoded SQL expressions (injection risk)
tests = [
  "B105", "B106", "B107",
  "B303", "B304", "B305",
  "B311",
  "B501", "B502", "B503",
  "B602", "B603", "B608",
]
```

**Semgrep (multi-language):**

```yaml
# In CI workflow
- name: Semgrep SAST
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/security-audit
      p/owasp-top-ten
      p/cwe-top-25
      p/secrets
      p/python
      p/sql-injection
  env:
    SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
```

**Semgrep custom rules for financial services:**

```yaml
# .semgrep/financial-services.yml
rules:
  - id: no-plaintext-pii
    patterns:
      - pattern: |
          $X = $FUNC(...)
          ...
          log.$LEVEL($X)
    message: "Potential PII in log statement — verify no SSN, TIN, or account numbers"
    languages: [python]
    severity: WARNING

  - id: sql-string-format
    patterns:
      - pattern: |
          cursor.execute("..." % ...)
      - pattern: |
          cursor.execute(f"...")
      - pattern: |
          cursor.execute("..." + ...)
    message: "SQL constructed with string formatting — use parameterized queries"
    languages: [python]
    severity: ERROR

  - id: no-md5-sha1
    patterns:
      - pattern: hashlib.md5(...)
      - pattern: hashlib.sha1(...)
    message: "MD5 and SHA-1 are not approved for financial services — use SHA-256 or SHA-3"
    languages: [python]
    severity: ERROR

  - id: hardcoded-credentials
    patterns:
      - pattern: |
          $KEY = "..."
      - metavariable-regex:
          metavariable: $KEY
          regex: (password|secret|token|api_key|apikey|passwd|pwd)
    message: "Hardcoded credential detected — use environment variables or vault"
    languages: [python]
    severity: ERROR
```

### SCA (Software Composition Analysis)

SCA checks your dependencies for known vulnerabilities.

```yaml
# In CI workflow
- name: pip-audit (Python dependencies)
  run: |
    pip install pip-audit
    pip-audit \
      --requirement requirements.txt \
      --format json \
      --output pip-audit-report.json \
      --fail-on-vulnerability-found
    # Print summary
    pip-audit --requirement requirements.txt

- name: npm audit (Node dependencies, if applicable)
  if: hashFiles('package.json') != ''
  run: npm audit --audit-level=moderate

- name: License compliance
  run: |
    pip install pip-licenses
    pip-licenses \
      --format=json \
      --with-urls \
      --output-file=license-report.json
    # Fail on non-approved licenses (copyleft in financial services)
    pip-licenses --allow-only="MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC;Python-2.0;PSF" \
      --fail-on-violation
```

**Approved license policy (financial services):**

| License | Status | Notes |
|---------|--------|-------|
| MIT | Approved | Standard permissive |
| Apache-2.0 | Approved | Standard permissive |
| BSD-2-Clause | Approved | Standard permissive |
| BSD-3-Clause | Approved | Standard permissive |
| ISC | Approved | Standard permissive |
| GPL-2.0 | Prohibited | Copyleft — legal review required |
| GPL-3.0 | Prohibited | Copyleft — legal review required |
| AGPL-3.0 | Prohibited | Copyleft — legal review required |
| LGPL | Conditional | Legal review required before use |
| Commercial | Conditional | Procurement required |

### Dependency Pinning

```bash
# Pin all dependencies to exact versions in production
pip install pip-tools

# Generate requirements.txt from requirements.in
pip-compile requirements.in --generate-hashes --output-file requirements.txt

# Lock file enforces hash verification
pip install -r requirements.txt --require-hashes
```

---

## Pre-Deploy Validation

Pre-deploy checks run after code merges to main and before any artifact reaches a deployment target. These are the last automated gate before human deployment approval.

### Complete Pre-Deploy Workflow

```yaml
# .github/workflows/pre-deploy.yml
name: Pre-Deploy Validation

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
        description: "Target environment: staging | production"
      artifact_sha:
        required: true
        type: string

jobs:
  compliance-gate:
    name: Compliance Validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Validate audit trail and data classification compliance
        run: |
          # Compliance checks run via CLI
          agentic-sdlc check --all
          # Fails if any required audit event is missing or data classification is violated

      - name: Check for restricted data in agent context
        run: |
          python - << 'EOF'
          import re, sys, pathlib

          RESTRICTED_PATTERNS = [
              r'\b\d{3}-\d{2}-\d{4}\b',   # SSN format
              r'\b\d{9}\b',                # TIN format
              r'\bSSN\b', r'\bTIN\b',
              r'account.number', r'acct_num',
          ]

          prompt_files = list(pathlib.Path('src').rglob('*prompt*'))
          prompt_files += list(pathlib.Path('src').rglob('*system_prompt*'))

          violations = []
          for f in prompt_files:
              content = f.read_text()
              for pattern in RESTRICTED_PATTERNS:
                  if re.search(pattern, content, re.IGNORECASE):
                      violations.append(f"{f}: pattern '{pattern}'")

          if violations:
              print("FAIL: Restricted data patterns in agent prompts:")
              for v in violations:
                  print(f"  {v}")
              sys.exit(1)

          print("PASS: No restricted data patterns in agent prompts")
          EOF

  model-vulnerability-scan:
    name: Model Vulnerability Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Scan for prompt injection vulnerabilities
        run: |
          python - << 'EOF'
          import pathlib, sys, re

          # Patterns indicating potential prompt injection exposure
          INJECTION_RISKS = [
              r'user_input.*system_prompt',
              r'format\(.*user',
              r'f".*{user',
              r'f".*{request',
              r'\.format\(.*input',
          ]

          src_files = list(pathlib.Path('src').rglob('*.py'))
          violations = []

          for f in src_files:
              content = f.read_text()
              for pattern in INJECTION_RISKS:
                  matches = [(i+1, line) for i, line in enumerate(content.splitlines())
                             if re.search(pattern, line, re.IGNORECASE)]
                  for lineno, line in matches:
                      violations.append(f"{f}:{lineno}: {line.strip()}")

          if violations:
              print("WARN: Potential prompt injection vectors — manual review required:")
              for v in violations:
                  print(f"  {v}")
          else:
              print("PASS: No obvious prompt injection vectors detected")
          EOF

      - name: Verify model endpoint allowlist
        run: |
          APPROVED_ENDPOINTS=(
            "api.anthropic.com"
            "api.openai.com"
          )

          FOUND=$(grep -r "\.anthropic\.\|openai\.\|googleapis\.\|bedrock" \
            --include="*.py" src/ | grep -v "test\|example\|mock" || true)

          if [ -n "$FOUND" ]; then
            echo "AI endpoint calls found — verify against approved list:"
            echo "$FOUND"
          fi

  container-security:
    name: Container Security
    if: hashFiles('Dockerfile') != ''
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build container
        run: docker build -t pre-deploy-scan:${{ inputs.artifact_sha }} .

      - name: Trivy container scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: pre-deploy-scan:${{ inputs.artifact_sha }}
          exit-code: 1
          severity: CRITICAL,HIGH
          format: json
          output: trivy-container-report.json

      - name: Hadolint Dockerfile scan
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: warning

  approval-gate:
    name: Deployment Approval Gate
    needs: [compliance-gate, model-vulnerability-scan]
    runs-on: ubuntu-latest
    environment:
      name: ${{ inputs.environment }}-approval
    steps:
      - name: Deployment approved
        run: |
          echo "All pre-deploy checks passed."
          echo "Environment: ${{ inputs.environment }}"
          echo "Artifact: ${{ inputs.artifact_sha }}"

          python tools/guardrail-scripts/generate-audit-trail.py \
            --action "deployment.approved" \
            --actor "${{ github.actor }}" \
            --actor-type "user" \
            --resource "${{ inputs.artifact_sha }}" \
            --resource-type "deployment" \
            --result "success" \
            --metadata '{"environment": "${{ inputs.environment }}"}'
```

---

## Runtime Monitoring

Runtime monitoring is the final layer. It assumes something got through the pre-deploy gates and catches it in production.

### Anomaly Detection

Configure these alerts in your SIEM or APM tool:

```yaml
# runtime-monitoring-policy.yml
anomaly_detection:

  # Authentication anomalies
  auth_failures:
    threshold: 5 per user per minute
    action: lock_account, alert_security

  auth_from_new_geography:
    action: require_mfa, alert_user

  service_account_interactive_login:
    action: alert_security_immediate

  # Data access anomalies
  unusual_data_volume:
    threshold: 10x baseline for user/role
    window: 15 minutes
    action: alert_security, log_session

  restricted_data_access_spike:
    threshold: 3x baseline
    action: alert_data_owner, alert_security

  after_hours_restricted_access:
    hours: "outside 0600-2200 local"
    data_level: restricted
    action: alert_security, require_justification

  # Agent-specific anomalies
  agent_action_volume:
    threshold: 100 actions per hour per agent session
    action: suspend_session, alert_supervisor

  agent_data_exfiltration:
    pattern: large_output + restricted_data_access
    action: terminate_session, alert_security_immediate

  # API anomalies
  error_rate_spike:
    threshold: 5% per 5-minute window (10x normal)
    action: alert_on_call

  latency_spike:
    threshold: 2x p95 baseline
    window: 10 minutes
    action: alert_on_call
```

### Audit Logging

Every agent action, data access event, and security event must produce a structured audit log entry. The log format matches the output of `generate-audit-trail.py`.

**Required events:**

| Event | Trigger | Retention |
|-------|---------|-----------|
| `auth.login` | Every login (user or service) | 1 year |
| `auth.logout` | Every logout | 1 year |
| `auth.failure` | Every failed authentication | 7 years |
| `spec.created` | Spec file created | 7 years |
| `spec.approved` | Spec status set to approved | 7 years |
| `code.generated` | Agent produces code | 7 years |
| `code.reviewed` | Human code review completed | 7 years |
| `data.read` | Read of Confidential or Restricted data | 7 years |
| `data.write` | Write of Confidential or Restricted data | 7 years |
| `deployment.approved` | Deployment gate passed | 7 years |
| `deployment.executed` | Code deployed to environment | 7 years |
| `deployment.rollback` | Rollback triggered | 7 years |
| `security.alert` | Any security control fired | 7 years |
| `config.changed` | Any configuration change | 7 years |

**Mandatory fields for Confidential and Restricted data events:**

| Field | Required | Notes |
|-------|---------|-------|
| `timestamp` | Yes | ISO 8601 with UTC timezone |
| `correlation_id` | Yes | UUID v4, trace across systems |
| `actor.type` | Yes | `user`, `agent`, or `system` |
| `actor.id` | Yes | Unique identifier, not display name |
| `actor.supervisor` | If actor is agent | Human supervisor ID |
| `action` | Yes | Dot-notation event name |
| `resource.type` | Yes | What kind of thing was touched |
| `resource.id` | Yes | Specific identifier |
| `result` | Yes | `success`, `failure`, `partial` |
| `data_classification` | If data accessed | Classification level of data |

---

## Audit Trail Format

This section documents the complete JSON schema for audit trail entries. The schema matches the output of `tools/guardrail-scripts/generate-audit-trail.py`.

### Full Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AuditEntry",
  "type": "object",
  "required": [
    "timestamp",
    "level",
    "service",
    "correlation_id",
    "actor",
    "action",
    "resource",
    "result"
  ],
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of the event"
    },
    "level": {
      "type": "string",
      "enum": ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
    },
    "service": {
      "type": "string",
      "description": "Service or component that generated the entry"
    },
    "correlation_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID v4 for tracing across systems and log entries"
    },
    "actor": {
      "type": "object",
      "required": ["type", "id"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["user", "agent", "system"]
        },
        "id": {
          "type": "string",
          "description": "Unique actor identifier (email, service account, agent ID)"
        },
        "supervisor": {
          "type": "string",
          "description": "Human supervisor ID — required when type is agent"
        }
      }
    },
    "action": {
      "type": "string",
      "description": "Dot-notation event name: noun.verb (e.g., spec.approved, code.generated)"
    },
    "resource": {
      "type": "object",
      "required": ["type", "id"],
      "properties": {
        "type": {
          "type": "string",
          "description": "Resource category: spec, code, deployment, config, data"
        },
        "id": {
          "type": "string",
          "description": "Specific resource identifier"
        }
      }
    },
    "result": {
      "type": "string",
      "enum": ["success", "failure", "partial"]
    },
    "duration_ms": {
      "type": "integer",
      "description": "Operation duration in milliseconds (optional)"
    },
    "context": {
      "type": "object",
      "description": "Additional context: IP address, session ID, request ID",
      "properties": {
        "ip_address": { "type": "string" },
        "session_id": { "type": "string" },
        "request_id": { "type": "string" },
        "user_agent": { "type": "string" }
      }
    },
    "data_classification": {
      "type": "string",
      "enum": ["restricted", "confidential", "internal", "public"],
      "description": "Classification level of data accessed — required for data events"
    },
    "metadata": {
      "type": "object",
      "description": "Event-specific additional fields",
      "additionalProperties": true
    }
  }
}
```

### Canonical Examples

**Spec approval (standard event):**

```json
{
  "timestamp": "2025-05-15T14:32:00Z",
  "level": "INFO",
  "service": "agentic-sdlc",
  "correlation_id": "a3f1b2c4-d5e6-7890-abcd-ef1234567890",
  "actor": {
    "type": "user",
    "id": "joshua.knox@apexfinancial.example.com"
  },
  "action": "spec.approved",
  "resource": {
    "type": "spec",
    "id": "SPEC-2025-05-15-001"
  },
  "result": "success",
  "metadata": {
    "spec_title": "Automated Advance Confirmation Report",
    "data_classification": "internal",
    "approver_role": "technical_lead"
  }
}
```

**Agent code generation (agent event with supervisor):**

```json
{
  "timestamp": "2025-05-15T15:10:22Z",
  "level": "INFO",
  "service": "agentic-sdlc",
  "correlation_id": "b4c2d3e5-f6a7-8901-bcde-f23456789012",
  "actor": {
    "type": "agent",
    "id": "claude-code-v3.7",
    "supervisor": "joshua.knox@apexfinancial.example.com"
  },
  "action": "code.generated",
  "resource": {
    "type": "milestone",
    "id": "SPEC-2025-05-15-001-M2"
  },
  "result": "success",
  "duration_ms": 42300,
  "metadata": {
    "files_created": ["src/reports/advance_confirmation.py"],
    "files_modified": ["src/reports/__init__.py"],
    "tests_written": 8,
    "tests_passing": 8
  }
}
```

**Confidential data read (compliance-critical event):**

```json
{
  "timestamp": "2025-05-15T16:45:00Z",
  "level": "INFO",
  "service": "reporting-service",
  "correlation_id": "c5d3e4f6-a7b8-9012-cdef-345678901234",
  "actor": {
    "type": "system",
    "id": "reporting-service-prod"
  },
  "action": "data.read",
  "resource": {
    "type": "data",
    "id": "member-advance-accounts"
  },
  "result": "success",
  "data_classification": "confidential",
  "context": {
    "request_id": "req_7f8a9b0c1d2e",
    "triggered_by": "monthly-compliance-report-job"
  },
  "metadata": {
    "record_count": 847,
    "fields_accessed": ["member_id", "advance_balance", "maturity_date"],
    "fields_excluded": ["account_number", "routing_number"]
  }
}
```

**Security alert (incident event):**

```json
{
  "timestamp": "2025-05-15T02:17:33Z",
  "level": "CRITICAL",
  "service": "auth-service",
  "correlation_id": "d6e4f5a7-b8c9-0123-defa-456789012345",
  "actor": {
    "type": "user",
    "id": "unknown"
  },
  "action": "auth.failure",
  "resource": {
    "type": "application",
    "id": "internal-portal"
  },
  "result": "failure",
  "context": {
    "ip_address": "203.0.113.42",
    "user_agent": "python-requests/2.31.0"
  },
  "metadata": {
    "failure_reason": "invalid_credentials",
    "attempt_count": 12,
    "geo_location": "Unknown/International",
    "alert_triggered": "brute_force_detected"
  }
}
```

### Generating Audit Entries

Use `generate-audit-trail.py` from the CI pipeline or directly:

```bash
# Manual entry
python tools/guardrail-scripts/generate-audit-trail.py \
  --action "spec.approved" \
  --actor "joshua.knox@apexfinancial.example.com" \
  --actor-type "user" \
  --resource "SPEC-2025-05-15-001" \
  --resource-type "spec" \
  --result "success" \
  --metadata '{"data_classification": "internal", "approver_role": "technical_lead"}' \
  --log-file audit/audit.jsonl

# From handoff packet
python tools/guardrail-scripts/generate-audit-trail.py \
  --file handoffs/handoff-M2.md \
  --log-file audit/audit.jsonl

# Output as markdown table row (for inclusion in handoff packets)
python tools/guardrail-scripts/generate-audit-trail.py \
  --action "milestone.completed" \
  --actor "claude-code" \
  --actor-type "agent" \
  --resource "SPEC-001-M2" \
  --output markdown
```

### Log Storage and Rotation

```bash
# Audit logs are append-only JSONL files
# One file per day, retained per policy

audit/
├── audit-2025-05-15.jsonl
├── audit-2025-05-14.jsonl
└── ...

# Ship to SIEM in real-time using Splunk Universal Forwarder or similar
# Do not rely on file-based logs as the primary audit record in production
```

---

## Regulated Industry Requirements (banking)

This section documents controls required specifically for regional financial institution and broader banking regulatory compliance. These are not optional for production deployments.

### Regulatory Framework

The organization operates under oversight from the Federal Housing Finance Agency (FHFA) and is subject to:

- **FHFA Advisory Bulletin AB 2023-06**: Third-party risk management
- **FFIEC Cybersecurity Assessment Tool (CAT)**: Cybersecurity maturity requirements
- **NIST SP 800-53**: Security and privacy controls (financial sector alignment)
- **SOX (if applicable)**: Financial reporting controls
- **GLBA**: Gramm-Leach-Bliley Act — member financial data protection

### Required Controls

**1. Human oversight for all agent actions on Confidential or Restricted data**

No agent may read, write, or transform Confidential or Restricted data without a named human supervisor in the audit trail entry. The `actor.supervisor` field is mandatory for these events.

```python
# Enforcement in code
def agent_data_access(data_classification: str, actor_id: str, supervisor_id: str | None):
    if data_classification in ("confidential", "restricted"):
        if not supervisor_id:
            raise ValueError(
                f"Supervisor required for {data_classification} data access. "
                "Set actor.supervisor in the audit trail entry."
            )

    generate_audit_entry(
        action="data.read",
        actor_id=actor_id,
        actor_type="agent",
        supervisor=supervisor_id,
        data_classification=data_classification,
    )
```

**2. Segregation of duties on deployment approvals**

The engineer who wrote the code cannot be the sole approver for its deployment. Enforce this in branch protection:

```bash
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_pull_request_reviews='{"required_approving_review_count":2,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions='{"users":[],"teams":["security-team"]}'
```

**3. Immutable audit logs**

Audit logs must be write-once, read-many. In practice, this means:

```yaml
# Splunk configuration example
[audit_log_index]
homePath   = $SPLUNK_DB/audit/db
coldPath   = $SPLUNK_DB/audit/colddb
thawedPath = $SPLUNK_DB/audit/thaweddb
maxTotalDataSizeMB = unlimited

# Retain for 7 years (220752000 seconds)
frozenTimePeriodInSecs = 220752000

# Enable log integrity validation in CloudTrail / Azure Monitor equivalent
```

**4. Data residency**

customer data must remain within US data centers. Enforce in code and in vendor agreements:

```python
# Environment validation at startup
import os

REQUIRED_REGION = os.environ.get("DEPLOYMENT_REGION", "")
APPROVED_REGIONS = {"us-east-1", "us-east-2", "us-west-1", "us-west-2", "us-gov-west-1"}

if REQUIRED_REGION not in APPROVED_REGIONS:
    raise EnvironmentError(
        f"Deployment region {REQUIRED_REGION!r} not in approved US regions. "
        "Member data cannot leave US jurisdiction."
    )
```

**5. Annual penetration testing**

AI-augmented development changes attack surface. Include these in annual pen test scope:
- Agent prompt injection vectors
- Model output injection into downstream systems
- Audit trail tampering
- Privilege escalation via agent actions

**6. Vendor AI model assessment**

Before using any external AI model endpoint with Internal or above data:

```
Required documentation:
- [ ] Data Processing Agreement (DPA) signed
- [ ] SOC 2 Type II report reviewed (within 12 months)
- [ ] Data residency confirmed (US only for AFC)
- [ ] Retention policy confirmed (no training on submitted data)
- [ ] Incident notification SLA confirmed (<72 hours)
- [ ] Third-party risk assessment completed
- [ ] CISO approval documented
```

**7. Change management integration**

Every spec that deploys to production must reference a change management ticket:

```yaml
# Spec frontmatter (required for production deployments)
---
spec_id: SPEC-2025-05-15-001
title: Automated Advance Confirmation Report
status: approved
change_ticket: CHG-2025-12345   # Required for production
data_classification: internal
compliance_review_date: 2025-05-10
compliance_reviewer: compliance@apexfinancial.example.com
---
```

### Examination Readiness

When FHFA or internal audit examines AI-augmented development, they will request:

1. **Evidence of human oversight** — Audit trail entries with `actor.supervisor` populated
2. **Evidence of security controls** — CI/CD scan results, pre-commit logs
3. **Evidence of data handling compliance** — Data classification records, DPAs with vendors
4. **Evidence of change management** — Spec to change ticket to deployment audit trail
5. **Evidence of testing** — Test results, coverage reports, pen test reports

Maintain these records for 7 years. The audit JSONL files plus CI/CD artifacts satisfy most examination requests.

---

## GitHub Actions Configuration Examples

### Complete Security Scan Workflow

The framework ships with `.github/workflows/security-scan.yml`. Key jobs:

```yaml
# Nightly + on push to main
on:
  schedule:
    - cron: '0 0 * * *'    # Daily at midnight UTC
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  dependency-scan:
    # SCA: pip-audit, npm audit, GitHub Dependency Review

  sast-scan:
    # CodeQL + Semgrep with financial services rulesets

  secret-scan:
    # TruffleHog (full history on schedule, incremental on push)

  iac-scan:
    # Hadolint (Dockerfile), Trivy (filesystem)

  compliance-check:
    needs: [dependency-scan, sast-scan, secret-scan]
    # Validates required files, audit trail, data classification
```

### CODEOWNERS for Security-Sensitive Paths

```
# .github/CODEOWNERS

# Security configuration — security team must approve changes
/.github/workflows/security-scan.yml    @security-team
/.pre-commit-config.yaml                @security-team
/.semgrep/                              @security-team
/tools/guardrail-scripts/               @security-team

# Data classification policy
/.security/                             @security-team @compliance-team

# Specs handling Confidential or Restricted data
/specs/SPEC-*-CONF-*                    @security-team @technical-lead
/specs/SPEC-*-RESTR-*                   @security-team @compliance-team @ciso
```

### Environment Protection Rules

Configure environment protection in GitHub Settings > Environments:

```yaml
# Staging environment
staging:
  required_reviewers: [technical-lead]
  wait_timer: 0
  deployment_branch_policy:
    protected_branches: true

# Production environment
production:
  required_reviewers:
    - technical-lead
    - security-team
  wait_timer: 30    # 30-minute wait after approval before deploy
  deployment_branch_policy:
    protected_branches: true
  prevent_self_review: true   # Deployer cannot be the approver
```

### Secrets Management in GitHub Actions

Never put credentials in workflow files. Use GitHub Secrets for all credentials:

```bash
# Set secrets via GitHub CLI
gh secret set SEMGREP_APP_TOKEN --body "your-token-here"
gh secret set SNYK_TOKEN --body "your-token-here"
gh secret set VAULT_TOKEN --body "your-token-here"

# Reference in workflows as:
# ${{ secrets.SEMGREP_APP_TOKEN }}
```

For enterprise, replace GitHub Secrets with HashiCorp Vault or Azure Key Vault:

```yaml
# Azure Key Vault integration
- name: Get secrets from Key Vault
  uses: azure/get-keyvault-secrets@v1
  with:
    keyvault: agentic-sdlc-vault
    secrets: 'semgrep-token, snyk-token, audit-db-password'
  id: myGetSecretAction

- name: Run Semgrep
  env:
    SEMGREP_APP_TOKEN: ${{ steps.myGetSecretAction.outputs.semgrep-token }}
  run: semgrep ci
```

### Notification on Security Scan Failure

```yaml
notify-on-failure:
  needs: [dependency-scan, sast-scan, secret-scan]
  if: failure()
  runs-on: ubuntu-latest
  steps:
    - name: Notify security team
      uses: slackapi/slack-github-action@v1
      with:
        channel-id: security-alerts
        slack-message: |
          Security scan failed on `${{ github.repository }}`
          Branch: `${{ github.ref_name }}`
          Actor: `${{ github.actor }}`
          Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
      env:
        SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

---

## Security Gate Summary

| Layer | When | What | Block on Failure? |
|-------|------|------|--------------------|
| Pre-commit | Every `git commit` | Secrets, linting, file hygiene | Yes — commit blocked |
| CI — SAST | Every PR and push to main | Bandit, Semgrep, CodeQL | Yes — merge blocked |
| CI — SCA | Every PR and push to main | pip-audit, npm audit, license check | Yes — merge blocked |
| CI — Secrets | Every PR and push to main | TruffleHog (incremental) | Yes — merge blocked |
| Pre-deploy | After merge, before deploy | Audit completeness, data classification, model scan | Yes — deployment blocked |
| Runtime | Continuous | Anomaly detection, audit logging | Alert + possible auto-rollback |
| Nightly | 00:00 UTC daily | Full TruffleHog scan, full dependency audit | Alert security team |

---

## References

- [Framework Overview](../docs/framework-overview.md)
- [Implementation Guide](../docs/implementation-guide.md)
- [Agent-Ready Spec Template](../templates/agent-ready-spec.md) — Data Classification section
- [Generate Audit Trail Script](../tools/guardrail-scripts/generate-audit-trail.py)
- [CI Workflow](../.github/workflows/ci.yml)
- [Security Scan Workflow](../.github/workflows/security-scan.yml)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [FFIEC Cybersecurity Assessment Tool](https://www.ffiec.gov/cyberassessmenttool.htm)
- [FHFA Advisory Bulletins](https://www.fhfa.gov/supervision/advisory-bulletins)
- [TruffleHog Documentation](https://github.com/trufflesecurity/trufflehog)
- [Semgrep Rule Registry](https://semgrep.dev/r)
