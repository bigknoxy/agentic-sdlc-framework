# Contributing to Agentic SDLC Framework

Thank you for your interest in contributing! This document provides guidelines for contributing to the framework.

## Development Philosophy

We practice what we preach — this framework is developed using the Agentic SDLC Framework itself.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists
2. Create a new issue with:
   - Clear title
   - Detailed description
   - Steps to reproduce (if applicable)
   - Expected vs actual behavior

### Proposing Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Write an agent-ready spec** for significant changes
4. **Implement** following the framework
5. **Pass all guardrails**: linting, tests, security scans
6. **Submit a pull request**

### Pull Request Process

1. Update documentation if needed
2. Ensure all CI checks pass
3. Request review from maintainers
4. Address feedback
5. Squash commits if requested

## Code of Conduct

### Our Standards

- **Be respectful**: Treat everyone with respect
- **Be constructive**: Provide helpful feedback
- **Be collaborative**: Work together toward solutions
- **Be inclusive**: Welcome newcomers and diverse perspectives

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing others' private information

## Development Setup

This project is Python-based (Python 3.11+). There is no Node.js or npm dependency.

```bash
# Clone your fork
git clone https://github.com/your-username/agentic-sdlc-framework.git
cd agentic-sdlc-framework

# Install Python dependencies (Python 3.11+ required)
pip install -e ".[dev]"

# Verify CLI works
agentic-sdlc --help

# Run tests
pytest

# Create a branch
git checkout -b feature/your-feature

# Make changes following the framework
# - Write spec for significant changes
# - Follow existing patterns
# - Add tests
# - Update docs

# Commit
git commit -m "feat: description"

# Push
git push origin feature/your-feature
```

## Commit Message Guidelines

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Formatting, no code change
- `refactor:` Code restructuring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## Questions?

- Open an issue for questions
- Join discussions in existing issues
- Reach out to maintainers

## Recognition

Contributors will be recognized in our README and release notes.

Thank you for contributing!
