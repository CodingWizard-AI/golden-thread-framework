# Release Checklist for Golden Thread Framework

This checklist ensures a smooth release process for the package.

## Pre-Release Checklist

### Code Quality
- [ ] All tests pass locally: `pytest`
- [ ] Code is formatted: `black src/ tests/`
- [ ] Linting passes: `ruff check src/ tests/`
- [ ] Type checking passes: `mypy src/`
- [ ] No pending TODOs or FIXMEs in production code
- [ ] All docstrings are complete and accurate

### Dependencies
- [ ] All dependencies in `pyproject.toml` have version constraints
- [ ] Tree-sitter language packages are specified correctly
- [ ] Development dependencies are in `[project.optional-dependencies]`
- [ ] No unused dependencies

### Documentation
- [ ] README.md is up to date
- [ ] CHANGELOG.md has entry for this version
- [ ] Example files are current and working
- [ ] API documentation is generated (if applicable)
- [ ] Error codes are documented

### Version Management
- [ ] Version updated in `pyproject.toml`
- [ ] Version updated in `src/golden_thread/__init__.py`
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)

### Testing
- [ ] Unit tests cover new features
- [ ] Integration tests pass
- [ ] Test coverage is ≥80%
- [ ] Manual testing completed:
  - [ ] `golden-thread validate --service` works
  - [ ] `golden-thread validate --all` works
  - [ ] `golden-thread orphans` works
  - [ ] JSON output is valid
  - [ ] Config loading works with env vars
  - [ ] Notion API integration works (if credentials available)

## Build Process

### Local Build Test
```bash
# Install build tools
pip install build twine

# Build distributions
python -m build

# Check distributions
twine check dist/*

# Test installation
pip install dist/*.whl
golden-thread --version
golden-thread --help
```

### Expected Outputs
- [ ] `dist/golden_thread_framework-X.Y.Z.tar.gz` (source)
- [ ] `dist/golden_thread_framework-X.Y.Z-py3-none-any.whl` (wheel)
- [ ] Both distributions pass `twine check`

## TestPyPI Release (Optional but Recommended)

### Upload to TestPyPI
```bash
twine upload --repository testpypi dist/*
```

### Test Installation from TestPyPI
```bash
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  golden-thread-framework
```

### Verify
- [ ] Package installs without errors
- [ ] CLI command works: `golden-thread --version`
- [ ] Dependencies are correctly resolved

## PyPI Release

### Final Checks
- [ ] Git working directory is clean
- [ ] On main branch
- [ ] All changes committed
- [ ] Version tag created: `git tag vX.Y.Z`

### Upload to PyPI
```bash
# Upload to production PyPI
twine upload dist/*
```

### Post-Upload Verification
- [ ] Package appears on PyPI: https://pypi.org/project/golden-thread-framework/
- [ ] Install from PyPI: `pip install golden-thread-framework`
- [ ] Version number is correct
- [ ] README renders correctly on PyPI

## Post-Release Tasks

### Git
- [ ] Push version tag: `git push --tags`
- [ ] Create GitHub Release with CHANGELOG excerpt
- [ ] Close milestone (if using milestones)

### Communication
- [ ] Announce release internally (if applicable)
- [ ] Update project documentation site (if exists)
- [ ] Post in relevant channels/forums

### Planning
- [ ] Create milestone for next version
- [ ] Move unreleased CHANGELOG items to new version
- [ ] Update project roadmap

## Rollback Procedure

If issues are discovered post-release:

1. **Yank the release** (makes it unavailable for new installs):
   ```bash
   # Cannot be done via twine, must use PyPI web interface
   # Go to: https://pypi.org/manage/project/golden-thread-framework/releases/
   ```

2. **Fix the issue** in a new patch version

3. **Release the fix** following this checklist

## Version Numbering Guide

- **MAJOR** (1.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.1.0): New features, backwards compatible
- **PATCH** (0.0.1): Bug fixes, backwards compatible

Examples:
- `0.1.0` → `0.2.0`: Added new parser support
- `0.1.0` → `0.1.1`: Fixed bug in manifest loading
- `0.9.0` → `1.0.0`: Stable release with breaking changes

## Common Issues

### Issue: `twine upload` fails with authentication error
**Solution**: Set PyPI token in `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

### Issue: Package dependencies not resolving
**Solution**: Check dependency version constraints in `pyproject.toml`

### Issue: CLI command not found after install
**Solution**: Verify `[project.scripts]` entry in `pyproject.toml`

## Automated Release (Future)

GitHub Actions workflow for automated releases:

```yaml
name: Publish to PyPI
on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Build
        run: |
          pip install build
          python -m build
      - name: Publish
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```
