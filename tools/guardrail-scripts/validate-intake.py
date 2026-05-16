#!/usr/bin/env python3
"""
Validate intake/pilot-proposal document completeness.

Usage:
    python validate-intake.py <proposal-file>
    python validate-intake.py --dir <directory>

Exit codes:
    0 - All proposals valid
    1 - Validation failed
    2 - Usage error
"""

import sys
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict


REQUIRED_FRONTMATTER = [
    "title",
    "status",
    "workflow",
    "start_date",
]

# proposal_id or id — either is acceptable
PROPOSAL_ID_FIELDS = ["proposal_id", "id"]

REQUIRED_SECTIONS = [
    "Business Case",
    "Scope",
    "Success Criteria",
    "Risk Assessment",
    "Compliance & Security",
    "Timeline",
]

# Strict-mode only
STRICT_SECTIONS = [
    "Approval Gates",
]

# Columns that must appear in the Success Criteria table
SUCCESS_CRITERIA_TABLE_COLUMNS = ["Metric", "Target"]

# Data classification checkboxes from the pilot-proposal template
DATA_CLASSIFICATION_PATTERN = re.compile(
    r'- \[[ x]\]\s*(Restricted|Confidential|Internal|Public)',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def _extract_frontmatter(content: str) -> Tuple[bool, str, List[str]]:
    """Return (found, raw_frontmatter_text, errors)."""
    errors: List[str] = []

    if not content.startswith("---"):
        errors.append(
            "Missing YAML frontmatter — the file must begin with --- "
            "(needed so automation can index proposals)"
        )
        return False, "", errors

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        errors.append(
            "Malformed YAML frontmatter — could not find closing --- line"
        )
        return False, "", errors

    return True, match.group(1), errors


def _parse_frontmatter(raw: str) -> Dict[str, str]:
    """Parse key: value pairs from raw frontmatter text."""
    metadata: Dict[str, str] = {}
    for line in raw.split('\n'):
        if ':' in line and not line.startswith('#'):
            key, _, value = line.partition(':')
            metadata[key.strip()] = value.strip()
    return metadata


def validate_frontmatter(
    content: str, strict: bool = False
) -> Tuple[bool, List[str]]:
    """Validate YAML frontmatter fields."""
    errors: List[str] = []

    found, raw, extract_errors = _extract_frontmatter(content)
    errors.extend(extract_errors)
    if not found:
        return False, errors

    metadata = _parse_frontmatter(raw)

    # Check proposal_id / id (either field is acceptable)
    has_id = any(f in metadata for f in PROPOSAL_ID_FIELDS)
    if not has_id:
        errors.append(
            "Missing frontmatter field: proposal_id (or id) — "
            "a unique identifier is required so the proposal can be tracked "
            "in the audit log"
        )
    else:
        # Warn if the value looks like a placeholder
        for field in PROPOSAL_ID_FIELDS:
            if field in metadata:
                val = metadata[field]
                if not val or val in ('[required]', 'null', '~', ''):
                    errors.append(
                        f"Empty frontmatter field: {field} — "
                        "provide a real proposal identifier (e.g. PILOT-2024-001)"
                    )

    # Check remaining required fields
    for field in REQUIRED_FRONTMATTER:
        if field not in metadata:
            errors.append(
                f"Missing frontmatter field: {field} — "
                f"this field is required for workflow routing and reporting"
            )
        elif not metadata[field] or metadata[field] in ('[required]', 'null', '~'):
            errors.append(
                f"Empty frontmatter field: {field} — "
                f"fill in a real value before submitting"
            )

    # Strict: validate start_date is a parseable date
    if strict and 'start_date' in metadata:
        date_val = metadata['start_date'].strip('"\'')
        if not _is_valid_date(date_val):
            errors.append(
                f"Invalid start_date value '{date_val}' — "
                "must be a real calendar date in YYYY-MM-DD format "
                "(strict mode requires a parseable date)"
            )

    return len(errors) == 0, errors


def _is_valid_date(value: str) -> bool:
    """Return True if value is a parseable YYYY-MM-DD date."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Section helpers
# ---------------------------------------------------------------------------

def validate_sections(
    content: str, strict: bool = False
) -> Tuple[bool, List[str]]:
    """Validate that required (and in strict mode, additional) sections exist."""
    errors: List[str] = []

    sections_to_check = list(REQUIRED_SECTIONS)
    if strict:
        sections_to_check.extend(STRICT_SECTIONS)

    for section in sections_to_check:
        # Match ## Section Name (with or without leading numbers/emojis)
        pattern = rf'##\s+(?:\d+\.\s*)?{re.escape(section)}'
        if not re.search(pattern, content, re.IGNORECASE):
            hint = _section_hint(section, strict=strict)
            errors.append(
                f"Missing required section: '{section}' — {hint}"
            )

    return len(errors) == 0, errors


def _section_hint(section: str, strict: bool = False) -> str:
    hints: Dict[str, str] = {
        "Business Case": (
            "explain the problem, evidence of pain, and expected value; "
            "without this, reviewers cannot assess ROI"
        ),
        "Scope": (
            "list what is In Scope and Out of Scope; "
            "prevents scope creep and sets clear boundaries for the pilot"
        ),
        "Success Criteria": (
            "define measurable targets with Metric and Target columns; "
            "needed to evaluate whether the pilot succeeded"
        ),
        "Risk Assessment": (
            "include a risk matrix table; "
            "required by the FRAME methodology before approval"
        ),
        "Compliance & Security": (
            "specify data classification and regulatory requirements; "
            "mandatory for regulated environments"
        ),
        "Timeline": (
            "provide a phase breakdown or milestone table; "
            "needed so stakeholders can track progress"
        ),
        "Approval Gates": (
            "list each gate with required approver and criteria; "
            "required in strict mode to ensure sign-off chain is documented"
        ),
    }
    return hints.get(section, "add this section before submitting the proposal")


# ---------------------------------------------------------------------------
# Content-level validators
# ---------------------------------------------------------------------------

def validate_success_criteria(content: str) -> Tuple[bool, List[str]]:
    """Check that the Success Criteria section contains a Metric/Target table."""
    errors: List[str] = []

    # Find the Success Criteria section (everything up to the next ## heading)
    section_match = re.search(
        r'##\s+(?:\d+\.\s*)?Success Criteria(.*?)(?=\n##\s|\Z)',
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if not section_match:
        # Section absence is already caught by validate_sections; skip here
        return True, []

    section_body = section_match.group(1)

    # Look for a markdown table that has both Metric and Target header columns
    table_header_pattern = re.compile(
        r'\|[^\n]*Metric[^\n]*\|[^\n]*Target[^\n]*\|',
        re.IGNORECASE,
    )
    if not table_header_pattern.search(section_body):
        errors.append(
            "Success Criteria section is missing a table with 'Metric' and "
            "'Target' columns — add a table so targets are measurable and "
            "reviewers can validate outcomes (see pilot-proposal template § Success Criteria)"
        )

    return len(errors) == 0, errors


def validate_risk_assessment(content: str) -> Tuple[bool, List[str]]:
    """Check that the Risk Assessment section contains a table."""
    errors: List[str] = []

    section_match = re.search(
        r'##\s+(?:\d+\.\s*)?Risk Assessment(.*?)(?=\n##\s|\Z)',
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if not section_match:
        return True, []

    section_body = section_match.group(1)

    # A markdown table has at least one | ... | line followed by a separator
    table_pattern = re.compile(r'\|[^\n]+\|', re.MULTILINE)
    if not table_pattern.search(section_body):
        errors.append(
            "Risk Assessment section is missing a risk matrix table — "
            "add a table with Risk, Likelihood, Impact, and Mitigation columns "
            "so risks can be prioritised before the pilot begins"
        )

    return len(errors) == 0, errors


def validate_compliance_and_security(content: str) -> Tuple[bool, List[str]]:
    """Check that Compliance & Security has a data classification checkbox."""
    errors: List[str] = []

    section_match = re.search(
        r'##\s+(?:\d+\.\s*)?Compliance\s*&\s*Security(.*?)(?=\n##\s|\Z)',
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if not section_match:
        return True, []

    section_body = section_match.group(1)

    if not DATA_CLASSIFICATION_PATTERN.search(section_body):
        errors.append(
            "Compliance & Security section does not specify data classification — "
            "add a checkbox list with at least one option marked [x] "
            "(Restricted / Confidential / Internal / Public) so security "
            "reviewers know what data protection controls apply"
        )

    return len(errors) == 0, errors


def validate_strict_approval_gates(content: str) -> Tuple[bool, List[str]]:
    """Strict mode: check Approval Gates section has a table."""
    errors: List[str] = []

    section_match = re.search(
        r'##\s+(?:\d+\.\s*)?Approval\s*Gates(.*?)(?=\n##\s|\Z)',
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if not section_match:
        # validate_sections already reports this missing section in strict mode
        return True, []

    section_body = section_match.group(1)

    table_pattern = re.compile(r'\|[^\n]+\|', re.MULTILINE)
    if not table_pattern.search(section_body):
        errors.append(
            "Approval Gates section exists but has no table — "
            "add a table with Gate, Required, Approver, and Criteria columns "
            "so the sign-off chain is unambiguous (strict mode requirement)"
        )

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Top-level file validator
# ---------------------------------------------------------------------------

def validate_intake(
    proposal_path: Path, strict: bool = False
) -> Tuple[bool, List[str]]:
    """Validate a single intake/pilot-proposal file."""
    errors: List[str] = []

    try:
        content = proposal_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, [f"Failed to read file: {exc}"]

    # 1. Frontmatter
    _, fm_errors = validate_frontmatter(content, strict=strict)
    errors.extend(fm_errors)

    # 2. Required sections (+ strict extras)
    _, sec_errors = validate_sections(content, strict=strict)
    errors.extend(sec_errors)

    # 3. Success Criteria table
    _, sc_errors = validate_success_criteria(content)
    errors.extend(sc_errors)

    # 4. Risk Assessment table
    _, ra_errors = validate_risk_assessment(content)
    errors.extend(ra_errors)

    # 5. Compliance & Security — data classification
    _, cs_errors = validate_compliance_and_security(content)
    errors.extend(cs_errors)

    # 6. Strict: Approval Gates table
    if strict:
        _, ag_errors = validate_strict_approval_gates(content)
        errors.extend(ag_errors)

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Directory scanner
# ---------------------------------------------------------------------------

def validate_directory(
    dir_path: Path, strict: bool = False
) -> Tuple[int, int, List[str]]:
    """Validate all intake/proposal markdown files in a directory tree."""
    total = 0
    passed = 0
    all_errors: List[str] = []

    # Match filenames that look like intake docs or pilot proposals
    name_pattern = re.compile(
        r'(intake|proposal|pilot)', re.IGNORECASE
    )

    for md_file in dir_path.rglob("*.md"):
        if name_pattern.search(md_file.name):
            total += 1
            valid, errors = validate_intake(md_file, strict=strict)

            if valid:
                passed += 1
                print(f"✅ {md_file}")
            else:
                print(f"❌ {md_file}")
                for error in errors:
                    all_errors.append(f"  {md_file}: {error}")

    return total, passed, all_errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate intake / pilot-proposal documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate-intake.py proposals/my-pilot.md
  python validate-intake.py proposals/my-pilot.md --strict
  python validate-intake.py --dir proposals/
  python validate-intake.py --dir proposals/ --strict

Exit codes:
  0  All proposals valid
  1  One or more validation failures
  2  Usage error (bad arguments)
        """,
    )
    parser.add_argument(
        "proposal_file",
        nargs="?",
        help="Path to a single intake / pilot-proposal file to validate",
    )
    parser.add_argument(
        "--dir",
        metavar="DIRECTORY",
        help="Validate all intake/proposal markdown files found recursively in DIRECTORY",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Enable strict mode: also require Approval Gates section, "
            "validate that start_date is a real calendar date"
        ),
    )

    args = parser.parse_args()

    # ------------------------------------------------------------------ --dir
    if args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists():
            print(f"❌ Directory not found: {dir_path}")
            sys.exit(1)

        mode_label = " [strict]" if args.strict else ""
        print(f"Validating intake proposals in: {dir_path}{mode_label}\n")
        total, passed, errors = validate_directory(dir_path, strict=args.strict)

        print(f"\n{'='*60}")
        if total == 0:
            print(
                "⚠️  No intake/proposal files found "
                "(filenames must contain 'intake', 'proposal', or 'pilot')"
            )
            sys.exit(0)

        print(f"Results: {passed}/{total} proposals passed")

        if errors:
            print("\nErrors:")
            for error in errors:
                print(error)

        sys.exit(0 if passed == total else 1)

    # ----------------------------------------------------------- single file
    elif args.proposal_file:
        proposal_path = Path(args.proposal_file)
        if not proposal_path.exists():
            print(f"❌ Proposal file not found: {proposal_path}")
            sys.exit(1)

        mode_label = " [strict mode]" if args.strict else ""
        print(f"Validating{mode_label}: {proposal_path}\n")
        valid, errors = validate_intake(proposal_path, strict=args.strict)

        if valid:
            print("✅ Intake proposal validation passed\n")
            print("Required sections confirmed:")
            for section in REQUIRED_SECTIONS:
                print(f"  ✓ {section}")
            if args.strict:
                for section in STRICT_SECTIONS:
                    print(f"  ✓ {section}")
            print("\nContent checks passed:")
            print("  ✓ Success Criteria table (Metric / Target columns)")
            print("  ✓ Risk Assessment table")
            print("  ✓ Compliance & Security — data classification specified")
            if args.strict:
                print("  ✓ Approval Gates table")
                print("  ✓ start_date is a valid calendar date")
            sys.exit(0)
        else:
            print("❌ Intake proposal validation failed\n")
            print("Errors:")
            for error in errors:
                print(f"  • {error}")
            print(
                f"\n⚠️  Fix the {len(errors)} issue(s) above, then re-run this script."
            )
            print(
                "   Reference: templates/pilot-proposal.md"
            )
            sys.exit(1)

    # ---------------------------------------------------------- no arguments
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
