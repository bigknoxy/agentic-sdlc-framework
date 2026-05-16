"""Shared validation logic for specs and handoff packets.

Ported from tools/guardrail-scripts/validate-spec.py and
tools/guardrail-scripts/check-handoff-packet.py with a clean Python API
(no argparse, no sys.exit — callers decide what to do with results).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple, Dict


# ---------------------------------------------------------------------------
# Spec validation
# ---------------------------------------------------------------------------

SPEC_REQUIRED_SECTIONS = [
    "Context",
    "Goal State",
    "Non-Negotiable Constraints",
    "Acceptance Criteria",
    "Edge Cases",
    "Rollback Conditions",
    "Data Classification",
    "Audit Trail Requirements",
]

SPEC_REQUIRED_FRONTMATTER = [
    "spec_id",
    "title",
    "status",
    "priority",
]

SPEC_OPTIONAL_RECOMMENDED = [
    "estimated_effort",
    "template_version",
]


def validate_spec_frontmatter(content: str) -> Tuple[bool, List[str]]:
    """Validate YAML frontmatter of a spec file."""
    errors: List[str] = []

    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter (should start with ---)")
        return False, errors

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        errors.append("Malformed YAML frontmatter")
        return False, errors

    frontmatter = match.group(1)

    for field in SPEC_REQUIRED_FRONTMATTER:
        if f"{field}:" not in frontmatter:
            errors.append(f"Missing frontmatter field: {field}")

    return len(errors) == 0, errors


def validate_spec_sections(content: str) -> Tuple[bool, List[str]]:
    """Validate that all required sections exist in the spec."""
    errors: List[str] = []

    for section in SPEC_REQUIRED_SECTIONS:
        pattern = rf"##\s+\d+\.\s*{re.escape(section)}"
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Missing required section: {section}")

    return len(errors) == 0, errors


def validate_spec_acceptance_criteria(content: str) -> Tuple[bool, List[str]]:
    """Validate acceptance criteria use Gherkin format."""
    errors: List[str] = []

    gherkin_pattern = r"(Given|When|Then|And|But)\s+\[.*\]"
    if not re.search(gherkin_pattern, content, re.IGNORECASE):
        errors.append("Acceptance criteria should use Gherkin format (Given/When/Then)")

    if "```gherkin" not in content and "Scenario:" not in content:
        errors.append("Acceptance criteria should include executable Gherkin scenarios")

    return len(errors) == 0, errors


def validate_spec_constraints(content: str) -> Tuple[bool, List[str]]:
    """Validate that constraints section has expected content."""
    errors: List[str] = []

    if "Data Classification" in content:
        if not re.search(r"\[x\]\s*(Restricted|Confidential|Internal|Public)", content):
            errors.append("Data classification should have one option selected [x]")

    if "Approval Gates" in content:
        if not re.search(r"- \[.\]", content):
            errors.append("Approval gates should have checkboxes [- [ ]] or [- [x]]")

    return len(errors) == 0, errors


def validate_spec(spec_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single spec file.

    Returns (is_valid, list_of_errors).
    """
    errors: List[str] = []

    try:
        content = spec_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, [f"Failed to read file: {exc}"]

    _, fm_errors = validate_spec_frontmatter(content)
    errors.extend(fm_errors)

    _, sec_errors = validate_spec_sections(content)
    errors.extend(sec_errors)

    _, ac_errors = validate_spec_acceptance_criteria(content)
    errors.extend(ac_errors)

    _, con_errors = validate_spec_constraints(content)
    errors.extend(con_errors)

    return len(errors) == 0, errors


def validate_spec_directory(dir_path: Path) -> Tuple[int, int, List[str]]:
    """Validate all spec markdown files in a directory.

    Returns (total, passed, list_of_error_strings).
    """
    total = 0
    passed = 0
    all_errors: List[str] = []

    for spec_file in sorted(dir_path.rglob("*.md")):
        if spec_file.name == ".gitkeep":
            continue
        total += 1
        valid, errors = validate_spec(spec_file)
        if valid:
            passed += 1
        else:
            for e in errors:
                all_errors.append(f"{spec_file}: {e}")

    return total, passed, all_errors


# ---------------------------------------------------------------------------
# Handoff validation
# ---------------------------------------------------------------------------

HANDOFF_REQUIRED_FIELDS = [
    "packet_id",
    "milestone",
    "date",
    "agent",
    "supervisor",
]

HANDOFF_REQUIRED_SECTIONS = [
    "Milestone Summary",
    "Work Completed",
    "Test Results",
    "Security Scan Results",
    "Next Steps",
    "Next Prompt Seed",
    "Audit Trail Entry",
]

HANDOFF_SECURITY_CHECKS = [
    "Secret Scanning",
    "Static Analysis",
    "Dependency Scanning",
]


def validate_handoff_frontmatter(content: str) -> Tuple[bool, List[str], Dict[str, str]]:
    """Validate YAML frontmatter of a handoff packet."""
    errors: List[str] = []
    metadata: Dict[str, str] = {}

    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter")
        return False, errors, metadata

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        errors.append("Malformed YAML frontmatter")
        return False, errors, metadata

    frontmatter = match.group(1)
    for line in frontmatter.splitlines():
        if ":" in line and not line.startswith("#"):
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()

    for field in HANDOFF_REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"Missing frontmatter field: {field}")
        elif not metadata[field] or metadata[field] == "[required]":
            errors.append(f"Empty frontmatter field: {field}")

    if "packet_id" in metadata:
        if not re.match(r"HANDOFF-(planner|executor)-\d+", metadata["packet_id"]):
            errors.append("packet_id should follow format: HANDOFF-[planner|executor]-###")

    if "date" in metadata:
        if not re.match(r"\d{4}-\d{2}-\d{2}", metadata["date"]):
            errors.append("date should be in YYYY-MM-DD format")

    return len(errors) == 0, errors, metadata


def validate_handoff_sections(content: str) -> Tuple[bool, List[str]]:
    """Validate required sections exist in a handoff packet."""
    errors: List[str] = []

    for section in HANDOFF_REQUIRED_SECTIONS:
        pattern = rf"##\s+{re.escape(section)}"
        if not re.search(pattern, content):
            errors.append(f"Missing required section: {section}")

    return len(errors) == 0, errors


def validate_handoff_milestone_status(content: str) -> Tuple[bool, List[str]]:
    """Validate milestone status is set."""
    errors: List[str] = []

    status_pattern = r"- \[([ x])\]\s*(✅|⚠️|❌)\s*Completed"
    if not re.search(status_pattern, content):
        errors.append(
            "Milestone status not set (should have - [x] or - [ ] with emoji)"
        )

    return len(errors) == 0, errors


def validate_handoff_security_scans(content: str) -> Tuple[bool, List[str]]:
    """Validate security scan results are documented."""
    errors: List[str] = []

    for check in HANDOFF_SECURITY_CHECKS:
        if check not in content:
            errors.append(f"Missing security check: {check}")
        else:
            pattern = rf"{re.escape(check)}.*?(✅|❌)"
            if not re.search(pattern, content, re.DOTALL | re.IGNORECASE):
                errors.append(f"Security check '{check}' missing status (✅/❌)")

    critical_match = re.search(r"\|\s*Critical\s*\|\s*(\d+)", content)
    if critical_match and int(critical_match.group(1)) > 0:
        errors.append(
            f"Found {critical_match.group(1)} critical vulnerabilities — must be resolved before handoff"
        )

    return len(errors) == 0, errors


def validate_handoff_test_results(content: str) -> Tuple[bool, List[str]]:
    """Validate test results are documented."""
    errors: List[str] = []

    if "Unit Tests" not in content:
        errors.append("Unit test results not documented")

    failed_match = re.search(r"\|\s*Failed\s*\|\s*(\d+)", content)
    if failed_match and int(failed_match.group(1)) > 0:
        errors.append(
            f"Found {failed_match.group(1)} failed tests — must be resolved before handoff"
        )

    coverage_match = re.search(r"Coverage\s*\|\s*(\d+)%", content)
    if coverage_match and int(coverage_match.group(1)) < 80:
        errors.append(
            f"Test coverage {coverage_match.group(1)}% below 80% threshold"
        )

    return len(errors) == 0, errors


def validate_handoff_next_steps(content: str) -> Tuple[bool, List[str]]:
    """Validate next steps are defined."""
    errors: List[str] = []

    if "### Immediate" not in content:
        errors.append("Immediate next steps not defined")

    step_pattern = r"^\d+\.\s*\[.+\]"
    if not re.search(step_pattern, content, re.MULTILINE):
        errors.append("Next steps should be numbered action items")

    return len(errors) == 0, errors


def validate_handoff_prompt_seed(content: str) -> Tuple[bool, List[str]]:
    """Validate the next prompt seed section is populated."""
    errors: List[str] = []

    if "## Next Prompt Seed" not in content:
        errors.append("Missing Next Prompt Seed section")
        return False, errors

    match = re.search(r"## Next Prompt Seed\n\n```(.*?)```", content, re.DOTALL)
    if not match:
        errors.append("Next Prompt Seed should be in a code block")
        return False, errors

    seed_content = match.group(1)
    placeholders = ["[What", "[Current", "[Next", "[Key", "[Important"]
    for placeholder in placeholders:
        if placeholder in seed_content:
            errors.append(f"Prompt seed contains placeholder: {placeholder}")

    if len(seed_content.strip()) < 100:
        errors.append("Prompt seed too short — should provide meaningful context")

    return len(errors) == 0, errors


def validate_handoff_audit_trail(content: str) -> Tuple[bool, List[str]]:
    """Validate audit trail entry is present."""
    errors: List[str] = []

    if "## Audit Trail Entry" not in content:
        errors.append("Missing Audit Trail Entry section")
        return False, errors

    for field in ["Action", "Actor", "Timestamp", "Correlation ID"]:
        if not re.search(rf"\*\*{re.escape(field)}\*\*", content):
            errors.append(f"Missing audit field: {field}")

    if "```json" not in content:
        errors.append("Audit trail should include JSON summary")

    return len(errors) == 0, errors


def validate_handoff(packet_path: Path, strict: bool = False) -> Tuple[bool, List[str]]:
    """Validate a single handoff packet.

    Returns (is_valid, list_of_errors).
    """
    errors: List[str] = []

    try:
        content = packet_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, [f"Failed to read file: {exc}"]

    _, fm_errors, _ = validate_handoff_frontmatter(content)
    errors.extend(fm_errors)

    _, sec_errors = validate_handoff_sections(content)
    errors.extend(sec_errors)

    _, status_errors = validate_handoff_milestone_status(content)
    errors.extend(status_errors)

    _, security_errors = validate_handoff_security_scans(content)
    errors.extend(security_errors)

    _, test_errors = validate_handoff_test_results(content)
    errors.extend(test_errors)

    _, step_errors = validate_handoff_next_steps(content)
    errors.extend(step_errors)

    _, seed_errors = validate_handoff_prompt_seed(content)
    errors.extend(seed_errors)

    _, audit_errors = validate_handoff_audit_trail(content)
    errors.extend(audit_errors)

    return len(errors) == 0, errors


def validate_handoff_directory(dir_path: Path, strict: bool = False) -> Tuple[int, int, List[str]]:
    """Validate all handoff packet markdown files in a directory.

    Returns (total, passed, list_of_error_strings).
    """
    total = 0
    passed = 0
    all_errors: List[str] = []

    for packet_file in sorted(dir_path.rglob("*.md")):
        if packet_file.name == ".gitkeep":
            continue
        total += 1
        valid, errors = validate_handoff(packet_file, strict)
        if valid:
            passed += 1
        else:
            for e in errors:
                all_errors.append(f"{packet_file}: {e}")

    return total, passed, all_errors
