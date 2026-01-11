"""Tests for validators."""

import pytest

from golden_thread.manifest import Manifest, SymbolMapping, Exclusions
from golden_thread.parsers.base import CodeSymbol
from golden_thread.validators.coverage import CoverageValidator
from golden_thread.validators.orphans import OrphanValidator


class TestCoverageValidator:
    """Test coverage validation."""

    def test_validate_full_coverage(self):
        """Test validation with 100% coverage."""
        manifest = Manifest(
            service="test-service",
            version="1.0",
            metadata={},
            symbols=[
                SymbolMapping(path="test.py::TestClass", type="class", ids=["FEAT-001"]),
                SymbolMapping(path="test.py::test_function", type="function", ids=["FR-001"]),
            ],
            exclusions=Exclusions(),
        )

        parsed_symbols = [
            CodeSymbol(name="TestClass", type="class", file_path="test.py", line_start=1, line_end=5),
            CodeSymbol(name="test_function", type="function", file_path="test.py", line_start=7, line_end=10),
        ]

        validator = CoverageValidator(manifest, parsed_symbols)
        result = validator.validate()

        assert result.coverage_percentage == 100.0
        assert result.total_symbols == 2
        assert result.mapped_symbols == 2
        assert len(result.orphan_symbols) == 0
        assert len(result.invalid_mappings) == 0
        assert len(result.errors) == 0

    def test_validate_orphan_code(self):
        """Test detection of orphaned code."""
        manifest = Manifest(
            service="test-service",
            version="1.0",
            metadata={},
            symbols=[SymbolMapping(path="test.py::TestClass", type="class", ids=["FEAT-001"])],
            exclusions=Exclusions(),
        )

        parsed_symbols = [
            CodeSymbol(name="TestClass", type="class", file_path="test.py", line_start=1, line_end=5),
            CodeSymbol(name="OrphanClass", type="class", file_path="test.py", line_start=7, line_end=10),
        ]

        validator = CoverageValidator(manifest, parsed_symbols)
        result = validator.validate()

        assert len(result.orphan_symbols) == 1
        assert "test.py::OrphanClass" in result.orphan_symbols
        assert result.coverage_percentage == 50.0

        # Check error details
        orphan_error = [e for e in result.errors if e["code"] == "ORPHAN_CODE"][0]
        assert orphan_error["path"] == "test.py::OrphanClass"

    def test_validate_orphan_manifest(self):
        """Test detection of orphaned manifest entries."""
        manifest = Manifest(
            service="test-service",
            version="1.0",
            metadata={},
            symbols=[
                SymbolMapping(path="test.py::TestClass", type="class", ids=["FEAT-001"]),
                SymbolMapping(path="test.py::MissingClass", type="class", ids=["FEAT-002"]),
            ],
            exclusions=Exclusions(),
        )

        parsed_symbols = [
            CodeSymbol(name="TestClass", type="class", file_path="test.py", line_start=1, line_end=5),
        ]

        validator = CoverageValidator(manifest, parsed_symbols)
        result = validator.validate()

        assert len(result.invalid_mappings) == 1
        assert "test.py::MissingClass" in result.invalid_mappings

        # Check error details
        orphan_error = [e for e in result.errors if e["code"] == "ORPHAN_MANIFEST"][0]
        assert orphan_error["path"] == "test.py::MissingClass"

    def test_skip_private_symbols(self):
        """Test that private symbols are skipped."""
        manifest = Manifest(
            service="test-service", version="1.0", metadata={}, symbols=[], exclusions=Exclusions()
        )

        parsed_symbols = [
            CodeSymbol(name="_private", type="function", file_path="test.py", line_start=1, line_end=2),
            CodeSymbol(name="__init__", type="method", file_path="test.py", line_start=3, line_end=4, parent="TestClass"),
            CodeSymbol(name="test_something", type="function", file_path="test.py", line_start=5, line_end=6),
        ]

        validator = CoverageValidator(manifest, parsed_symbols)
        result = validator.validate()

        # Private symbols and __init__ should not be counted
        # test_ functions should also be skipped
        assert result.total_symbols == 0

    def test_exclusion_patterns(self):
        """Test that exclusion patterns work."""
        manifest = Manifest(
            service="test-service",
            version="1.0",
            metadata={},
            symbols=[],
            exclusions=Exclusions(patterns=["**/__init__.py"], symbols=["test.py::DeprecatedClass"]),
        )

        parsed_symbols = [
            CodeSymbol(name="InitClass", type="class", file_path="__init__.py", line_start=1, line_end=2),
            CodeSymbol(name="DeprecatedClass", type="class", file_path="test.py", line_start=1, line_end=2),
            CodeSymbol(name="RegularClass", type="class", file_path="test.py", line_start=3, line_end=4),
        ]

        validator = CoverageValidator(manifest, parsed_symbols)
        result = validator.validate()

        # Only RegularClass should trigger orphan error
        assert len(result.orphan_symbols) == 1
        assert "test.py::RegularClass" in result.orphan_symbols


class TestOrphanValidator:
    """Test orphan detection."""

    def test_detect_orphan_code(self):
        """Test detecting orphaned code."""
        manifest = Manifest(
            service="test-service",
            version="1.0",
            metadata={},
            symbols=[SymbolMapping(path="test.py::MappedClass", type="class", ids=["FEAT-001"])],
            exclusions=Exclusions(),
        )

        parsed_symbols = [
            CodeSymbol(name="MappedClass", type="class", file_path="test.py", line_start=1, line_end=2),
            CodeSymbol(name="OrphanClass", type="class", file_path="test.py", line_start=3, line_end=4),
        ]

        validator = OrphanValidator(manifest, parsed_symbols)
        result = validator.detect_orphans()

        assert len(result.orphan_code) == 1
        assert result.orphan_code[0]["path"] == "test.py::OrphanClass"
        assert result.orphan_code[0]["type"] == "class"

    def test_detect_orphan_manifest(self):
        """Test detecting orphaned manifest entries."""
        manifest = Manifest(
            service="test-service",
            version="1.0",
            metadata={},
            symbols=[
                SymbolMapping(path="test.py::ExistingClass", type="class", ids=["FEAT-001"]),
                SymbolMapping(path="test.py::MissingClass", type="class", ids=["FEAT-002"]),
            ],
            exclusions=Exclusions(),
        )

        parsed_symbols = [
            CodeSymbol(name="ExistingClass", type="class", file_path="test.py", line_start=1, line_end=2),
        ]

        validator = OrphanValidator(manifest, parsed_symbols)
        result = validator.detect_orphans()

        assert len(result.orphan_manifest) == 1
        assert result.orphan_manifest[0]["path"] == "test.py::MissingClass"

    def test_generate_suggestions(self):
        """Test suggestion generation for orphans."""
        manifest = Manifest(
            service="test-service", version="1.0", metadata={}, symbols=[], exclusions=Exclusions()
        )

        parsed_symbols = [
            CodeSymbol(name="OrphanClass", type="class", file_path="test.py", line_start=1, line_end=2),
        ]

        validator = OrphanValidator(manifest, parsed_symbols)
        result = validator.detect_orphans()

        assert len(result.suggestions) == 1
        suggestion = result.suggestions[0]
        assert suggestion["orphan"] == "test.py::OrphanClass"
        assert suggestion["type"] == "code"
        assert ".golden-thread.yaml" in suggestion["suggestion"]
        assert "FEAT-XXX-001" in suggestion["suggestion"]

    def test_fuzzy_matching_suggestions(self):
        """Test fuzzy matching for orphaned manifest entries."""
        manifest = Manifest(
            service="test-service",
            version="1.0",
            metadata={},
            symbols=[SymbolMapping(path="test.py::OAthProvider", type="class", ids=["FEAT-001"])],  # Typo
            exclusions=Exclusions(),
        )

        parsed_symbols = [
            CodeSymbol(name="OAuthProvider", type="class", file_path="test.py", line_start=1, line_end=2),
        ]

        validator = OrphanValidator(manifest, parsed_symbols)
        result = validator.detect_orphans()

        # Should suggest the similar symbol
        manifest_suggestions = [s for s in result.suggestions if s["type"] == "manifest"]
        assert len(manifest_suggestions) == 1
        assert "Did you mean" in manifest_suggestions[0]["suggestion"]
        assert "OAuthProvider" in manifest_suggestions[0]["suggestion"]
