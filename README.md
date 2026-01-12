# Golden Thread Framework - Developer Documentation
## 📖 Open Source

## Overview

The **Golden Thread Framework** provides end-to-end traceability from business requirements through architecture, implementation, testing, and deployment. This ensures every line of code can be traced back to a business need, and every business requirement can be traced forward to its implementation.

## Why Use Golden Thread Traceability?

### Benefits

✅ **Accountability**: Every code change ties to a business requirement  
✅ **Completeness**: Ensure all requirements are implemented  
✅ **Impact Analysis**: Understand what's affected when requirements change  
✅ **Audit Trail**: Track decisions and their rationale  
✅ **Onboarding**: New developers understand *why* code exists  
✅ **Quality**: Requirements drive testing, ensuring coverage  

### The Problem Without It

❌ Orphaned code with unknown purpose  
❌ Missed requirements discovered late  
❌ Unclear impact of changes  
❌ Difficulty understanding architectural decisions  
❌ Technical debt accumulation  

---

## Golden Thread Documentation References:
- [Golden Thread Framework — Full Guide](https://github.com/CodingWizard-AI/golden-thread-framework/blob/aace298b54a46960cb9f7c8bea2b267604326467/docs/guides/golden-thread-framework.md#golden-thread-traceability-framework) — detailed framework and process

- [Golden Thread — Quick Reference ](https://github.com/CodingWizard-AI/golden-thread-framework/blob/aace298b54a46960cb9f7c8bea2b267604326467/docs/guides/golden-thread-quick-reference.md)— TL;DR, ID conventions, quick workflow

- [Traceability GitHub Actions workflow](https://github.com/CodingWizard-AI/golden-thread-framework/blob/aace298b54a46960cb9f7c8bea2b267604326467/docs/golden-thread-check.yml) (golden-thread-check.yml) — automated checks and PR comments

- [Golden Thread Diagrams](https://github.com/CodingWizard-AI/golden-thread-framework/blob/aace298b54a46960cb9f7c8bea2b267604326467/docs/diagrams/golden-thread-diagrams.md) — architecture/traceability diagrams

- [Pull Request Template ](https://github.com/CodingWizard-AI/golden-thread-framework/blob/aace298b54a46960cb9f7c8bea2b267604326467/docs/templates/PULL_REQUEST_TEMPLATE.md) — required PR fields and traceability checklist

---
## Pre-requisite

### Duplicate and populate the CodingWizard.AI Golden Thread Notion Template (See golden-thread-framework.md for in-depth walk-thorugh)

1. **Access the Template**  
   Visit: [CodingWizard.AI Golden Thread Template](https://codingwizard-ai.notion.site/) 
   - https://codingwizard-ai.notion.site

2. **Duplicate to Your Workspace**  
   - Click "Duplicate" in the top-right corner
   - Select your team's Notion workspace
   - Rename to match your project: `[Project Name] - Golden Thread Matrix`

3. **Set Permissions**  
   - Share with your engineering team
   - Grant edit access to architects and tech leads
   - Grant view access to stakeholders

## golden-thread-framework Quick Start

```bash
# Install from source
pip install -e .

# Set Notion API token
export NOTION_API_TOKEN=your_token_here

# Validate a service
golden-thread validate --service path/to/service

# Detect orphans
golden-thread orphans
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              golden-thread (Python Package)                      │
│            pip install golden-thread-framework                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐               │
│  │ Go Parser │    │ Py Parser │    │ TS Parser │               │
│  │(tree-sitter)   │   (AST)   │    │(tree-sitter)              │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘               │
│        └────────────────┼────────────────┘                      │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           Traceability Manifest Engine                   │    │
│  │  - Loads .golden-thread.yaml per service                │    │
│  │  - Maps code symbols to BR/UR/FEAT/FR/TC/V/EA          │    │
│  │  - Validates coverage against AST                       │    │
│  │  - Queries Notion registries via API                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                         │                                        │
│        ┌────────────────┼────────────────┐                      │
│        ▼                ▼                ▼                      │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐                 │
│  │ CI Validate│   │  CLI Tool │   │Report Gen │                 │
│  │(pre-commit)│   │(golden-thread)│ (JSON)    │                 │
│  └───────────┘   └───────────┘   └───────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Concepts

### Traceability Chain

The framework validates end-to-end traceability across Notion registries:

```
BR (Business Requirement)
 ↓
UR (User Requirement)
 ↓
FEAT (Feature)
 ↓
CF (Call Flow)
 ↓
FR / NFR / TSR / TCR (Requirements)
 ↓
V (Verification)
 ↓
TC (Test Case)
 ↓
EA (Evidence Artifact)
```

**Critical Rule**: No V-ID can be marked "Verified" without at least one EA-ID

### 17 Notion Registries available for use

| Registry | ID Pattern | Purpose |
|----------|-----------|---------|
| Business Requirement | BR-XXX-001 | Business justification |
| User Requirement | UR-XXX-001 | User needs |
| Feature Registry | FEAT-XXX-001 | Features |
| Call Flow Registry | CF-XXX-001 | Interaction sequences |
| Functional Requirement | FR-XXX-001 | Functional specs |
| Non-Functional Requirement | NFR-XXX-001 | Performance, security |
| Technical & System Requirement | TSR-XXX-001 | Technical specs |
| Transitional & Compliance | TCR-XXX-001 | Compliance needs |
| Verification Matrix | V-XXX-001 | Verification methods |
| Test Case Registry | TC-XXX-001 | Test cases |
| Evidence Artifacts | EA-XXX-001 | Test evidence |
| Services Matrix | Service Name | Service catalog |
| Interface Registry | IF-XXX-001 | API interfaces |
| Events Registry | EVT-XXX-001 | Event definitions |
| REST Endpoints | REST-XXX-001 | REST endpoints |
| GraphQL Operations | GQL-XXX-001 | GraphQL ops |
| gRPC Methods | RPC-XXX-001 | gRPC methods |

## Development Setup

### Prerequisites

- Python 3.9+
- Notion API token
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/golden-thread-framework.git
cd golden-thread-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_manifest.py -v

# Generate HTML coverage report
pytest --cov=golden_thread --cov-report=html
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Run all checks
black src/ tests/ && ruff check src/ tests/ && mypy src/ && pytest
```

## Configuration

### Global Config (`.golden-thread.config.yaml`)

Place at repository root:

```yaml
notion:
  api_token: ${NOTION_API_TOKEN}
  databases:
    BR: "db-id-here"
    UR: "db-id-here"
    FEAT: "db-id-here"
    # ... all 17 registries

services:
  discovery:
    manifest_filename: ".golden-thread.yaml"
    root_directories: [services/, packages/]

validation:
  ignore_patterns:
    - "**/test_*.py"
    - "**/*.test.ts"
```

### Service Manifest (`.golden-thread.yaml`)

Place in each service directory:

```yaml
service: authentication-service
version: "1.0"

traceability:
  features:
    - id: FEAT-AUTH-001
      description: "OAuth2 authentication"
      business_requirements: [BR-AUTH-001]
      user_requirements: [UR-AUTH-001]

  symbols:
    - path: "auth/oauth.py::OAuthProvider"
      type: class
      ids: [FEAT-AUTH-001, FR-AUTH-001]

    - path: "auth/oauth.py::OAuthProvider.authenticate"
      type: method
      ids: [FR-AUTH-003, NFR-AUTH-001]

exclusions:
  patterns:
    - "**/__init__.py"
    - "**/migrations/*.py"
```

## CLI Commands

### Validate Traceability

```bash
# Single service
golden-thread validate --service services/auth

# Entire monorepo
golden-thread validate --all

# With JSON output for CI
golden-thread validate --all --output json

# Strict mode (fail on warnings)
golden-thread validate --all --strict
```

### Detect Orphans

```bash
# Find unmapped code and manifest entries
golden-thread orphans --service services/auth

# JSON output
golden-thread orphans --output json
```

## Validation Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `ORPHAN_CODE` | Code without manifest entry | Add to `.golden-thread.yaml` |
| `ORPHAN_MANIFEST` | Manifest without code | Fix path or remove entry |
| `MISSING_BR` | Feature missing BR | Link in Notion |
| `MISSING_UR` | Feature missing UR | Link in Notion |
| `MISSING_FR` | Feature missing FR | Create FR in Notion |
| `MISSING_V` | Requirement missing V | Create V in Notion |
| `MISSING_TC` | Verification missing TC | Create TC in Notion |
| `MISSING_EA` | Verified without EA | Create EA in Notion |
| `INVALID_ID` | ID not in Notion | Check registry |

## Project Structure

```
golden-thread-framework/
├── src/golden_thread/
│   ├── __init__.py              # Exceptions, constants
│   ├── cli.py                   # CLI commands
│   ├── config.py                # Config loader
│   ├── manifest.py              # Manifest parser
│   ├── parsers/
│   │   ├── base.py              # Abstract parser
│   │   ├── python_parser.py     # Python AST
│   │   ├── typescript_parser.py # TypeScript tree-sitter
│   │   └── go_parser.py         # Go tree-sitter
│   ├── notion/
│   │   ├── client.py            # REST API client
│   │   └── registry.py          # Registry interface
│   ├── validators/
│   │   ├── coverage.py          # Coverage validator
│   │   ├── consistency.py       # ID validator
│   │   └── orphans.py           # Orphan detector
│   └── reports/
│       └── json.py              # JSON reporter
├── tests/                       # Test suite
├── examples/                    # Example configs
└── docs/                        # Documentation
```

## Adding Support for New Languages

1. Create parser in `src/golden_thread/parsers/`:

```python
from .base import BaseParser, CodeSymbol

class RustParser(BaseParser):
    def get_file_extensions(self):
        return [".rs"]

    def parse_file(self, file_path: str):
        # Implementation
        pass
```

2. Add to config schema in `config.py`
3. Add tests in `tests/test_parsers/`
4. Update documentation

## CI/CD Integration

### GitHub Actions

```yaml
name: Golden Thread Validation
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install golden-thread-framework
      - env:
          NOTION_API_TOKEN: ${{ secrets.NOTION_API_TOKEN }}
        run: golden-thread validate --all --output json --strict
```

## API Usage

```python
from golden_thread.config import Config
from golden_thread.manifest import Manifest
from golden_thread.parsers.python_parser import PythonParser
from golden_thread.validators.coverage import CoverageValidator

# Load config
config = Config.load(".golden-thread.config.yaml")

# Parse manifest
manifest = Manifest.load("services/auth/.golden-thread.yaml")

# Parse codebase
parser = PythonParser("services/auth", config.validation.__dict__)
symbols = parser.parse()

# Validate coverage
validator = CoverageValidator(manifest, symbols)
result = validator.validate()

print(f"Coverage: {result.coverage_percentage:.1f}%")
print(f"Errors: {len(result.errors)}")
```

## Performance

- **Caching**: Notion API responses cached for 1 hour
- **Rate Limiting**: 3 requests/second (Notion limit)
- **Parsing**: ~1000 files/second (Python AST)
- **Memory**: Lazy-loaded parsers, streamed file processing

## Troubleshooting

### Common Issues

**Issue**: `NOTION_API_TOKEN not set`
```bash
export NOTION_API_TOKEN=your_token_here
```

**Issue**: Tree-sitter grammar not found
```bash
pip install --upgrade tree-sitter-go tree-sitter-typescript
```

**Issue**: Import errors
```bash
pip install -e .  # Install in editable mode
```

## Release Process

See [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) for complete release process.

```bash
# Update version in pyproject.toml and __init__.py
# Update CHANGELOG.md

# Build
python -m build

# Test
twine check dist/*

# Upload to TestPyPI (optional)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Documentation

- **User Guide**: [README.md](README.md) (this file)
- **Implementation Plan**: [.claude/implementation-plan.md](.claude/implementation-plan.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Release Checklist**: [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)

## License

Apache 2.0 - See [LICENSE](LICENSE)

## Support

- Issues: [GitHub Issues](https://github.com/yourusername/golden-thread-framework/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/golden-thread-framework/discussions)

---

**Current Version**: 0.1.0
**Status**: Production Ready
**Test Coverage**: 75%+
