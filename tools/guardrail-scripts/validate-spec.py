#!/usr/bin/env python3
"""
Validate agent-ready spec completeness.

Usage:
    python validate-spec.py <spec-file>
    python validate-spec.py --dir <directory>

Exit codes:
    0 - All specs valid
    1 - Validation failed
    2 - Usage error
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple


REQUIRED_SECTIONS = [
    "Context",
    "Goal State",
    "Non-Negotiable Constraints",
    "Acceptance Criteria",
    "Edge Cases",
    "Rollback Conditions",
    "Data Classification",
    "Audit Trail Requirements",
]

REQUIRED_FRONTMATTER = [
    "spec_id",
    "title",
    "status",
    "priority",
]

OPTIONAL_BUT_RECOMMENDED = [
    "estimated_effort",
    "template_version",
]


def validate_frontmatter(content: str) -> Tuple[bool, List[str]]:
    """Validate YAML frontmatter."""
    errors = []
    
    # Check for frontmatter
    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter (should start with ---)")
        return False, errors
    
    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        errors.append("Malformed YAML frontmatter")
        return False, errors
    
    frontmatter = match.group(1)
    
    # Check required fields
    for field in REQUIRED_FRONTMATTER:
        if f"{field}:" not in frontmatter:
            errors.append(f"Missing frontmatter field: {field}")
    
    return len(errors) == 0, errors


def validate_sections(content: str) -> Tuple[bool, List[str]]:
    """Validate required sections exist."""
    errors = []
    
    for section in REQUIRED_SECTIONS:
        # Look for section header (## N. Section Name)
        pattern = rf'##\s+\d+\.\s*{re.escape(section)}'
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Missing required section: {section}")
    
    return len(errors) == 0, errors


def validate_acceptance_criteria(content: str) -> Tuple[bool, List[str]]:
    """Validate acceptance criteria are in Gherkin format."""
    errors = []
    
    # Look for Gherkin keywords
    gherkin_pattern = r'(Given|When|Then|And|But)\s+\[.*\]'
    if not re.search(gherkin_pattern, content, re.IGNORECASE):
        errors.append("Acceptance criteria should use Gherkin format (Given/When/Then)")
    
    # Check for executable tests
    if "```gherkin" not in content and "Scenario:" not in content:
        errors.append("Acceptance criteria should include executable Gherkin scenarios")
    
    return len(errors) == 0, errors


def validate_constraints(content: str) -> Tuple[bool, List[str]]:
    """Validate constraints are specified."""
    errors = []
    
    # Check for data classification
    if "Data Classification" in content:
        if not re.search(r'\[x\]\s*(Restricted|Confidential|Internal|Public)', content):
            errors.append("Data classification should have one option selected [x]")
    
    # Check for approval gates
    if "Approval Gates" in content:
        if not re.search(r'- \[.\]', content):
            errors.append("Approval gates should have checkboxes [- [ ]] or [- [x]]")
    
    return len(errors) == 0, errors


def validate_spec(spec_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single spec file."""
    errors = []
    
    try:
        content = spec_path.read_text()
    except Exception as e:
        return False, [f"Failed to read file: {e}"]
    
    # Validate frontmatter
    valid, frontmatter_errors = validate_frontmatter(content)
    errors.extend(frontmatter_errors)
    
    # Validate sections
    valid, section_errors = validate_sections(content)
    errors.extend(section_errors)
    
    # Validate acceptance criteria
    valid, ac_errors = validate_acceptance_criteria(content)
    errors.extend(ac_errors)
    
    # Validate constraints
    valid, constraint_errors = validate_constraints(content)
    errors.extend(constraint_errors)
    
    return len(errors) == 0, errors


def validate_directory(dir_path: Path) -> Tuple[int, int, List[str]]:
    """Validate all specs in a directory."""
    total = 0
    passed = 0
    all_errors = []
    
    for spec_file in dir_path.rglob("*.md"):
        if "spec" in spec_file.name.lower():
            total += 1
            valid, errors = validate_spec(spec_file)
            
            if valid:
                passed += 1
                print(f"✅ {spec_file}")
            else:
                print(f"❌ {spec_file}")
                for error in errors:
                    all_errors.append(f"  {spec_file}: {error}")
    
    return total, passed, all_errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate agent-ready specifications"
    )
    parser.add_argument(
        "spec_file",
        nargs="?",
        help="Path to spec file to validate"
    )
    parser.add_argument(
        "--dir",
        help="Validate all specs in directory"
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
        
        print(f"Validating specs in: {dir_path}\n")
        total, passed, errors = validate_directory(dir_path)
        
        print(f"\n{'='*60}")
        print(f"Results: {passed}/{total} specs passed")
        
        if errors:
            print("\nErrors:")
            for error in errors:
                print(error)
        
        sys.exit(0 if passed == total else 1)
    
    elif args.spec_file:
        spec_path = Path(args.spec_file)
        if not spec_path.exists():
            print(f"❌ Spec file not found: {spec_path}")
            sys.exit(1)
        
        print(f"Validating: {spec_path}\n")
        valid, errors = validate_spec(spec_path)
        
        if valid:
            print("✅ Spec validation passed")
            print("\nAll required sections found:")
            for section in REQUIRED_SECTIONS:
                print(f"  ✓ {section}")
            sys.exit(0)
        else:
            print("❌ Spec validation failed\n")
            print("Errors:")
            for error in errors:
                print(f"  • {error}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
