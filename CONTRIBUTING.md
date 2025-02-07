# Contributing to OfferDocGenerator

## Development Environment Setup

1. Install Nix package manager
```bash
curl -L https://nixos.org/nix/install | sh
```

2. Clone and setup development environment:
```bash
git clone https://github.com/yourusername/offerdocgenerator.git
cd offerdocgenerator
nix develop  # Enters development shell
uv pip install -e ".[dev]"
```

## Code Standards

- Type hints required for all functions
- Docstrings following Google style
- 100% test coverage required
- Black code formatting
- Ruff for linting

## Testing

Run the test suite:
```bash
pytest tests/
```

Check coverage:
```bash
pytest --cov=offerdoc tests/
```

## Pull Request Process

1. Create feature branch from main
2. Add tests for new functionality
3. Ensure CI passes
4. Request review from maintainers

## Commit Messages

Follow conventional commits:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- test: Test additions
- refactor: Code refactoring
