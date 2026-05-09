# Guardrail Scripts

This directory contains validation and automation scripts for the Agentic SDLC Framework.

## Scripts

### validate-spec.py

Validates agent-ready specification documents for completeness.

**Usage:**
```bash
# Validate single spec
python validate-spec.py path/to/spec.md

# Validate all specs in directory
python validate-spec.py --dir ./specs

# Strict mode (treat warnings as errors)
python validate-spec.py --strict path/to/spec.md
```

**Validates:**
- YAML frontmatter (spec_id, title, status, priority)
- Required sections (Context, Goal State, Acceptance Criteria, etc.)
- Gherkin format for acceptance criteria
- Data classification selection
- Approval gates

**Exit codes:**
- 0: Validation passed
- 1: Validation failed
- 2: Usage error

### check-handoff-packet.py

Validates handoff packets for completeness and security.

**Usage:**
```bash
# Validate single packet
python check-handoff-packet.py path/to/handoff.md

# Validate all packets in directory
python check-handoff-packet.py --dir ./handoffs

# Strict mode
python check-handoff-packet.py --strict path/to/handoff.md
```

**Validates:**
- YAML frontmatter (packet_id, milestone, date, agent, supervisor)
- Required sections (Milestone Summary, Test Results, Security Scans, etc.)
- Security scan results (no critical vulnerabilities)
- Test results (no failures, coverage >80%)
- Next steps defined
- Prompt seed populated
- Audit trail complete

**Exit codes:**
- 0: Validation passed
- 1: Validation failed
- 2: Usage error

### generate-audit-trail.py

Generates standardized audit trail entries.

**Usage:**
```bash
# Manual entry
python generate-audit-trail.py \
    --action "spec.created" \
    --actor "claude-code" \
    --resource "SPEC-2025-01-15-001" \
    --result "success"

# Extract from handoff packet
python generate-audit-trail.py --file handoff-packet.md

# Output formats
python generate-audit-trail.py --action "..." --output json
python generate-audit-trail.py --action "..." --output log
python generate-audit-trail.py --action "..." --output markdown

# Write to files
python generate-audit-trail.py --action "..." --output-file audit.json
python generate-audit-trail.py --action "..." --log-file audit.log
```

**Output formats:**
- `json`: Full JSON object (default)
- `log`: Single-line log format
- `markdown`: Markdown table row

## CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Validate Specs
  run: |
    python tools/guardrail-scripts/validate-spec.py --dir ./specs
    
- name: Validate Handoff Packets
  run: |
    python tools/guardrail-scripts/check-handoff-packet.py --dir ./handoffs
```

## Development

### Adding New Validations

1. Edit the appropriate script
2. Add validation function following existing patterns
3. Update tests
4. Update documentation

### Testing

```bash
# Test spec validation
python -m pytest tests/test_validate_spec.py

# Test handoff validation
python -m pytest tests/test_check_handoff.py
```
