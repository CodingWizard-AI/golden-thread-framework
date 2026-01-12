# Contributing to Golden Thread Framework

Thank you for your interest in contributing to the Golden Thread Framework!

## For Users

If you want to use the Golden Thread Framework in your project:

```bash
pip install golden-thread-framework
```

See the [PyPI package](https://pypi.org/project/golden-thread-framework/) and [README](README.md) for usage documentation.

## For Contributors

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CodingWizard-AI/golden-thread-framework.git
   cd golden-thread-framework
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks** (when available):
   ```bash
   pre-commit install
   ```

## Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_manifest.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=golden_thread --cov-report=html
```

## Code Quality

We use several tools to maintain code quality:

```bash
# Format code with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type check with MyPy
mypy src/

# Run all checks
black src/ tests/ && ruff check src/ tests/ && mypy src/ && pytest
```

## Project Structure

```
golden-thread-framework/
├── src/golden_thread/       # Main package
│   ├── parsers/             # Language parsers
│   ├── notion/              # Notion API integration
│   ├── validators/          # Validation logic
│   └── reports/             # Report generators
├── tests/                   # Test suite
├── examples/                # Example configs
└── docs/                    # Documentation
```

## Adding a New Language Parser

1. Create a new parser in `src/golden_thread/parsers/`
2. Inherit from `BaseParser` class
3. Implement required methods:
   - `get_file_extensions()`
   - `parse()`
   - `parse_file()`
4. Add parser to configuration schema in `config.py`
5. Add tests in `tests/test_parsers/`
6. Update documentation

Example:
```python
# src/golden_thread/parsers/rust_parser.py
from .base import BaseParser, CodeSymbol

class RustParser(BaseParser):
    def get_file_extensions(self):
        return [".rs"]

    def parse_file(self, file_path: str):
        # Parser implementation
        pass
```

## Adding a New Validator

1. Create validator in `src/golden_thread/validators/`
2. Define result dataclass
3. Implement validation logic
4. Add tests
5. Integrate into CLI pipeline

## Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

Co-Authored-By: Your Name <email@example.com>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

Examples:
```
feat(parsers): Add Rust parser support

Implements tree-sitter-based parser for Rust language.
Extracts structs, traits, functions, and impl blocks.

Co-Authored-By: Your Name <email@example.com>
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear commits
3. Add tests for new functionality
4. Update documentation as needed
5. Ensure all tests pass
6. Submit PR with description of changes
7. Address review feedback

## Release Process (Maintainers)

1. Update version in `pyproject.toml` and `src/golden_thread/__init__.py`
2. Update `CHANGELOG.md`
3. Create release commit: `chore: Release v0.2.0`
4. Tag release: `git tag v0.2.0`
5. Push tags: `git push --tags`
6. Build distributions: `python -m build`
7. Upload to PyPI: `twine upload dist/*`

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- Questions about the framework

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.
