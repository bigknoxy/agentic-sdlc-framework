#!/usr/bin/env python3
"""
Validate handoff packet completeness.

Usage:
    python check-handoff-packet.py <packet-file>
    python check-handoff-packet.py --dir <directory>

Exit codes:
    0 - All packets valid
    1 - Validation failed
    2 - Usage error
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Dict


REQUIRED_FIELDS = [
    "packet_id",
    "milestone",
    "date",
    "agent",
    "supervisor",
]

REQUIRED_SECTIONS = [
    "Milestone Summary",
    "Work Completed",
    "Test Results",
    "Security Scan Results",
    "Next Steps",
    "Next Prompt Seed",
    "Audit Trail Entry",
]

REQUIRED_TABLES = [
    "Files Created",
    "Files Modified",
]

SECURITY_CHECKS = [
    "Secret Scanning",
    "Static Analysis",
    "Dependency Scanning",
]


def validate_frontmatter(content: str) -> Tuple[bool, List[str], Dict]:
    """Validate YAML frontmatter."""
    errors = []
    metadata = {}
    
    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter")
        return False, errors, metadata
    
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        errors.append("Malformed YAML frontmatter")
        return False, errors, metadata
    
    frontmatter = match.group(1)
    
    # Parse frontmatter
    for line in frontmatter.split('\n'):
        if ':' in line and not line.startswith('#'):
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"Missing frontmatter field: {field}")
        elif not metadata[field] or metadata[field] == '[required]':
            errors.append(f"Empty frontmatter field: {field}")
    
    # Validate packet_id format
    if 'packet_id' in metadata:
        if not re.match(r'HANDOFF-(planner|executor)-\d+', metadata['packet_id']):
            errors.append("packet_id should follow format: HANDOFF-[planner|executor]-###")
    
    # Validate date format
    if 'date' in metadata:
        if not re.match(r'\d{4}-\d{2}-\d{2}', metadata['date']):
            errors.append("date should be in YYYY-MM-DD format")
    
    return len(errors) == 0, errors, metadata


def validate_sections(content: str) -> Tuple[bool, List[str]]:
    """Validate required sections exist."""
    errors = []
    
    for section in REQUIRED_SECTIONS:
        pattern = rf'##\s+{re.escape(section)}'
        if not re.search(pattern, content):
            errors.append(f"Missing required section: {section}")
    
    return len(errors) == 0, errors


def validate_milestone_status(content: str) -> Tuple[bool, List[str]]:
    """Validate milestone status is set."""
    errors = []
    
    # Check for status
    status_pattern = r'- \[([ x])\]\s*(✅|⚠️|❌)\s*Completed'
    if not re.search(status_pattern, content):
        errors.append("Milestone status not set (should have - [x] or - [ ] with emoji)")
    
    return len(errors) == 0, errors


def validate_security_scans(content: str) -> Tuple[bool, List[str]]:
    """Validate security scan results are documented."""
    errors = []
    warnings = []
    
    for check in SECURITY_CHECKS:
        if check not in content:
            errors.append(f"Missing security check: {check}")
        else:
            # Check if status is documented
            pattern = rf'{re.escape(check)}.*?(✅|❌)'
            if not re.search(pattern, content, re.DOTALL | re.IGNORECASE):
                warnings.append(f"Security check '{check}' missing status (✅/❌)")
    
    # Check for critical/high vulnerabilities
    critical_pattern = r'\|\s*Critical\s*\|\s*(\d+)'
    match = re.search(critical_pattern, content)
    if match:
        count = int(match.group(1))
        if count > 0:
            errors.append(f"Found {count} critical vulnerabilities - must be resolved before handoff")
    
    high_pattern = r'\|\s*High\s*\|\s*(\d+)'
    match = re.search(high_pattern, content)
    if match:
        count = int(match.group(1))
        if count > 5:  # Threshold
            warnings.append(f"Found {count} high vulnerabilities - review recommended")
    
    return len(errors) == 0, errors + warnings


def validate_test_results(content: str) -> Tuple[bool, List[str]]:
    """Validate test results are documented."""
    errors = []
    
    # Check for test tables
    if "Unit Tests" not in content:
        errors.append("Unit test results not documented")
    
    # Check for failed tests
    failed_pattern = r'\|\s*Failed\s*\|\s*(\d+)'
    match = re.search(failed_pattern, content)
    if match:
        count = int(match.group(1))
        if count > 0:
            errors.append(f"Found {count} failed tests - must be resolved before handoff")
    
    # Check for test coverage
    coverage_pattern = r'Coverage\s*\|\s*(\d+)%'
    match = re.search(coverage_pattern, content)
    if match:
        coverage = int(match.group(1))
        if coverage < 80:
            errors.append(f"Test coverage {coverage}% below 80% threshold")
    
    return len(errors) == 0, errors


def validate_next_steps(content: str) -> Tuple[bool, List[str]]:
    """Validate next steps are defined."""
    errors = []
    
    if "### Immediate" not in content:
        errors.append("Immediate next steps not defined")
    
    # Check for numbered steps
    step_pattern = r'^\d+\.\s*\[.+\]'
    if not re.search(step_pattern, content, re.MULTILINE):
        errors.append("Next steps should be numbered action items")
    
    return len(errors) == 0, errors


def validate_prompt_seed(content: str) -> Tuple[bool, List[str]]:
    """Validate next prompt seed is populated."""
    errors = []
    
    if "## Next Prompt Seed" not in content:
        errors.append("Missing Next Prompt Seed section")
        return False, errors
    
    # Extract prompt seed content
    match = re.search(r'## Next Prompt Seed\n\n```(.*?)```', content, re.DOTALL)
    if not match:
        errors.append("Next Prompt Seed should be in code block")
        return False, errors
    
    seed_content = match.group(1)
    
    # Check for placeholder content
    placeholders = ['[What', '[Current', '[Next', '[Key', '[Important']
    for placeholder in placeholders:
        if placeholder in seed_content:
            errors.append(f"Prompt seed contains placeholder: {placeholder}")
    
    # Check minimum length
    if len(seed_content.strip()) < 100:
        errors.append("Prompt seed too short - should provide meaningful context")
    
    return len(errors) == 0, errors


def validate_audit_trail(content: str) -> Tuple[bool, List[str]]:
    """Validate audit trail entry is complete."""
    errors = []
    
    if "## Audit Trail Entry" not in content:
        errors.append("Missing Audit Trail Entry section")
        return False, errors
    
    # Check for required audit fields
    audit_fields = ["Action", "Actor", "Timestamp", "Correlation ID"]
    for field in audit_fields:
        pattern = rf'\*\*{re.escape(field)}\*\*'
        if not re.search(pattern, content):
            errors.append(f"Missing audit field: {field}")
    
    # Check for JSON block
    if "```json" not in content:
        errors.append("Audit trail should include JSON summary")
    
    return len(errors) == 0, errors


def validate_packet(packet_path: Path, strict: bool = False) -> Tuple[bool, List[str]]:
    """Validate a single handoff packet."""
    errors = []
    
    try:
        content = packet_path.read_text()
    except Exception as e:
        return False, [f"Failed to read file: {e}"]
    
    # Validate frontmatter
    valid, frontmatter_errors, metadata = validate_frontmatter(content)
    errors.extend(frontmatter_errors)
    
    # Validate sections
    valid, section_errors = validate_sections(content)
    errors.extend(section_errors)
    
    # Validate milestone status
    valid, status_errors = validate_milestone_status(content)
    errors.extend(status_errors)
    
    # Validate security scans
    valid, security_errors = validate_security_scans(content)
    errors.extend(security_errors)
    
    # Validate test results
    valid, test_errors = validate_test_results(content)
    errors.extend(test_errors)
    
    # Validate next steps
    valid, step_errors = validate_next_steps(content)
    errors.extend(step_errors)
    
    # Validate prompt seed
    valid, seed_errors = validate_prompt_seed(content)
    errors.extend(seed_errors)
    
    # Validate audit trail
    valid, audit_errors = validate_audit_trail(content)
    errors.extend(audit_errors)
    
    return len(errors) == 0, errors


def validate_directory(dir_path: Path, strict: bool = False) -> Tuple[int, int, List[str]]:
    """Validate all packets in a directory."""
    total = 0
    passed = 0
    all_errors = []
    
    for packet_file in dir_path.rglob("*.md"):
        if "handoff" in packet_file.name.lower():
            total += 1
            valid, errors = validate_packet(packet_file, strict)
            
            if valid:
                passed += 1
                print(f"✅ {packet_file}")
            else:
                print(f"❌ {packet_file}")
                for error in errors:
                    all_errors.append(f"  {packet_file}: {error}")
    
    return total, passed, all_errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate handoff packet completeness"
    )
    parser.add_argument(
        "packet_file",
        nargs="?",
        help="Path to handoff packet to validate"
    )
    parser.add_argument(
        "--dir",
        help="Validate all packets in directory"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    
    args = parser.parse_args()
    
    if args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists():
            print(f"❌ Directory not found: {dir_path}")
            sys.exit(1)
        
        print(f"Validating handoff packets in: {dir_path}\n")
        total, passed, errors = validate_directory(dir_path, args.strict)
        
        print(f"\n{'='*60}")
        print(f"Results: {passed}/{total} packets passed")
        
        if errors:
            print("\nErrors:")
            for error in errors:
                print(error)
        
        sys.exit(0 if passed == total else 1)
    
    elif args.packet_file:
        packet_path = Path(args.packet_file)
        if not packet_path.exists():
            print(f"❌ Packet file not found: {packet_path}")
            sys.exit(1)
        
        print(f"Validating: {packet_path}\n")
        valid, errors = validate_packet(packet_path, args.strict)
        
        if valid:
            print("✅ Handoff packet validation passed")
            print("\nAll required sections found:")
            for section in REQUIRED_SECTIONS:
                print(f"  ✓ {section}")
            print("\nAll security checks documented:")
            for check in SECURITY_CHECKS:
                print(f"  ✓ {check}")
            sys.exit(0)
        else:
            print("❌ Handoff packet validation failed\n")
            print("Errors:")
            for error in errors:
                print(f"  • {error}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
