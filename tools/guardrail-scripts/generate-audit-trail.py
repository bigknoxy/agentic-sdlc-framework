#!/usr/bin/env python3
"""
Generate audit trail entry for agent actions.

Usage:
    python generate-audit-trail.py --action "spec.created" --actor "claude-code" \
        --resource "SPEC-2025-01-15-001" --result "success"
    
    python generate-audit-trail.py --file <handoff-packet.md>

Outputs JSON formatted audit entry to stdout and optionally to file.
"""

import sys
import json
import uuid
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


def generate_correlation_id() -> str:
    """Generate unique correlation ID."""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def create_audit_entry(
    action: str,
    actor: str,
    actor_type: str = "system",
    resource: str = "",
    resource_type: str = "",
    result: str = "success",
    correlation_id: Optional[str] = None,
    supervisor: Optional[str] = None,
    duration_ms: Optional[int] = None,
    metadata: Optional[Dict] = None,
    context: Optional[Dict] = None
) -> Dict:
    """Create standardized audit entry."""
    
    entry = {
        "timestamp": get_timestamp(),
        "level": "INFO",
        "service": "agentic-sdlc",
        "correlation_id": correlation_id or generate_correlation_id(),
        "actor": {
            "type": actor_type,
            "id": actor
        },
        "action": action,
        "resource": {
            "type": resource_type,
            "id": resource
        },
        "result": result,
        "metadata": metadata or {}
    }
    
    if supervisor:
        entry["actor"]["supervisor"] = supervisor
    
    if duration_ms:
        entry["duration_ms"] = duration_ms
    
    if context:
        entry["context"] = context
    
    return entry


def extract_from_handoff(packet_path: Path) -> Optional[Dict]:
    """Extract audit info from handoff packet."""
    try:
        content = packet_path.read_text()
        
        # Simple parsing - in production, use proper YAML parser
        import re
        
        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        
        frontmatter = match.group(1)
        
        # Parse frontmatter
        data = {}
        for line in frontmatter.split('\n'):
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        # Extract from audit trail section
        audit_match = re.search(r'## Audit Trail Entry\n\n\| Field \| Value \|\n\|[-\|]+\n((?:\|[^\|]+\|[^\|]+\|\n?)+)', content)
        if audit_match:
            audit_table = audit_match.group(1)
            for line in audit_table.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        key = parts[1].strip().lower().replace(' ', '_')
                        value = parts[2].strip()
                        if value and value != '[value]':
                            data[key] = value
        
        return data
    except Exception as e:
        print(f"Error parsing handoff packet: {e}", file=sys.stderr)
        return None


def format_audit_entry(entry: Dict, format: str = "json") -> str:
    """Format audit entry for output."""
    if format == "json":
        return json.dumps(entry, indent=2)
    elif format == "log":
        # Format as structured log line
        return f"{entry['timestamp']} [{entry['level']}] {entry['action']}: {entry['result']} - {entry['resource']['id']}"
    elif format == "markdown":
        # Format as markdown table row
        return f"| {entry['timestamp']} | {entry['actor']['id']} | {entry['action']} | {entry['resource']['id']} | {entry['result']} |"
    else:
        return json.dumps(entry, indent=2)


def append_to_log(entry: Dict, log_file: Path):
    """Append audit entry to log file."""
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        return True
    except Exception as e:
        print(f"Error writing to log file: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate audit trail entries for agent actions"
    )
    
    # Manual entry arguments
    parser.add_argument(
        "--action",
        help="Action performed (e.g., 'spec.created', 'code.implemented')"
    )
    parser.add_argument(
        "--actor",
        help="Agent or user ID that performed the action"
    )
    parser.add_argument(
        "--actor-type",
        default="system",
        choices=["user", "system", "agent"],
        help="Type of actor"
    )
    parser.add_argument(
        "--resource",
        help="Resource affected by the action"
    )
    parser.add_argument(
        "--resource-type",
        help="Type of resource (e.g., 'spec', 'code', 'test')"
    )
    parser.add_argument(
        "--result",
        default="success",
        choices=["success", "failure", "partial"],
        help="Result of the action"
    )
    parser.add_argument(
        "--correlation-id",
        help="Correlation ID for tracing (generated if not provided)"
    )
    parser.add_argument(
        "--supervisor",
        help="Human supervisor overseeing the action"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Duration in milliseconds"
    )
    parser.add_argument(
        "--metadata",
        help="Additional metadata as JSON string"
    )
    
    # File-based arguments
    parser.add_argument(
        "--file",
        type=Path,
        help="Extract audit info from handoff packet file"
    )
    
    # Output arguments
    parser.add_argument(
        "--output",
        choices=["json", "log", "markdown"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Append entry to log file"
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Write entry to output file"
    )
    
    args = parser.parse_args()
    
    # Extract from file or use manual arguments
    if args.file:
        data = extract_from_handoff(args.file)
        if not data:
            print("Error: Could not extract audit data from file", file=sys.stderr)
            sys.exit(1)
        
        entry = create_audit_entry(
            action=data.get('action', 'milestone.completed'),
            actor=data.get('agent', 'unknown'),
            actor_type="agent",
            resource=data.get('milestone', 'unknown'),
            resource_type="milestone",
            result=data.get('result', 'success').lower(),
            correlation_id=data.get('correlation_id'),
            supervisor=data.get('supervisor')
        )
    else:
        # Validate required arguments
        if not args.action or not args.actor:
            print("Error: --action and --actor are required (or use --file)", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
        
        # Parse metadata if provided
        metadata = None
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("Error: --metadata must be valid JSON", file=sys.stderr)
                sys.exit(1)
        
        entry = create_audit_entry(
            action=args.action,
            actor=args.actor,
            actor_type=args.actor_type,
            resource=args.resource or "",
            resource_type=args.resource_type or "",
            result=args.result,
            correlation_id=args.correlation_id,
            supervisor=args.supervisor,
            duration_ms=args.duration,
            metadata=metadata
        )
    
    # Format output
    output = format_audit_entry(entry, args.output)
    
    # Write to file(s) if specified
    if args.output_file:
        try:
            args.output_file.write_text(output)
            print(f"Audit entry written to: {args.output_file}")
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            sys.exit(1)
    
    if args.log_file:
        if append_to_log(entry, args.log_file):
            print(f"Audit entry appended to: {args.log_file}")
        else:
            sys.exit(1)
    
    # Always print to stdout
    print(output)


if __name__ == "__main__":
    main()
