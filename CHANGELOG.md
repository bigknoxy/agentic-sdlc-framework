# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial FRAME methodology implementation
- CLI with init, spec, handoff, check, metrics commands
- MCP server for Claude Desktop integration (5 framework tools)
- 12-task golden task set for weekly evaluation
- Guardrail scripts: validate-spec, check-handoff, generate-audit-trail
- CI/CD workflows: lint, security scan, spec validation, structure checks
- Template library: agent-ready-spec, handoff-packet, weekly-scorecard, pilot-proposal, ADR
- 3 pilot examples: regulated financial, personal project, enterprise
- Comprehensive documentation: framework overview, security guardrails, implementation guide
- **Golden task baseline data** (91.7% pass rate) with leadership package and ROI analysis
- **Before/after case study** demonstrating 58% cycle time reduction and 200% quarterly ROI
- CHANGELOG.md following Keep a Changelog format
- docs/methodology.md symlink to framework overview
- README venv installation instructions for Python 3.11+ compatibility

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2026-05-16

### Added
- Initial public release
- Full FRAME methodology documentation
- Production-ready guardrail scripts with strict mode support
- GitHub Actions CI/CD integration
- Golden task evaluation framework with baseline tracking
- Regulatory compliance templates (data classification, audit trail)
- Multi-agent handoff packet coordination pattern
- MCP server for IDE integration

### Security
- TruffleHog secret scanning in CI pipeline
- Data classification built into spec templates
- Audit trail generation for compliance requirements

### Documentation
- Complete framework overview (452 lines)
- Security guardrails guide
- Implementation guide
- How-to-use guide
- Delivery strategy
- 3 fully-worked pilot examples with READMEs