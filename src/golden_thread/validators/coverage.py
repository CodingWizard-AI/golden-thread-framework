"""Coverage validator for code-to-manifest traceability."""

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Set

from ..manifest import Manifest
from ..parsers.base import CodeSymbol


@dataclass
class CoverageResult:
    """Results from coverage validation."""

    total_symbols: int
    mapped_symbols: int
    orphan_symbols: List[str] = field(default_factory=list)
    invalid_mappings: List[str] = field(default_factory=list)
    coverage_percentage: float = 0.0
    errors: List[Dict] = field(default_factory=list)


class CoverageValidator:
    """Validates traceability coverage between code and manifest."""

    def __init__(self, manifest: Manifest, parsed_symbols: List[CodeSymbol]):
        """
        Initialize coverage validator.

        Args:
            manifest: Service manifest
            parsed_symbols: List of parsed code symbols
        """
        self.manifest = manifest
        self.parsed_symbols = parsed_symbols
        self.symbol_map = {s.qualified_path: s for s in parsed_symbols}

    def validate(self) -> CoverageResult:
        """
        Validate traceability coverage.

        Returns:
            CoverageResult with validation details
        """
        errors = []
        orphan_symbols = []
        invalid_mappings = []
        mapped_symbols = set()

        # Check manifest entries have code matches
        for mapping in self.manifest.symbols:
            if mapping.path not in self.symbol_map:
                errors.append(
                    {
                        "code": "ORPHAN_MANIFEST",
                        "message": f"Manifest entry '{mapping.path}' has no matching code",
                        "path": mapping.path,
                        "ids": mapping.ids,
                    }
                )
                invalid_mappings.append(mapping.path)
            else:
                mapped_symbols.add(mapping.path)

        # Check code symbols have manifest entries
        manifest_paths = self.manifest.get_symbol_paths()

        for symbol in self.parsed_symbols:
            if self._should_check_symbol(symbol):
                if symbol.qualified_path not in manifest_paths:
                    # Check if excluded
                    if not self._is_excluded(symbol):
                        errors.append(
                            {
                                "code": "ORPHAN_CODE",
                                "message": f"Code symbol '{symbol.qualified_path}' not in manifest",
                                "path": symbol.qualified_path,
                                "file": symbol.file_path,
                                "line": symbol.line_start,
                                "type": symbol.type,
                            }
                        )
                        orphan_symbols.append(symbol.qualified_path)

        # Calculate coverage
        checkable_symbols = [s for s in self.parsed_symbols if self._should_check_symbol(s)]
        total = len(checkable_symbols)
        mapped = len(mapped_symbols)

        coverage = (mapped / total * 100) if total > 0 else 0.0

        return CoverageResult(
            total_symbols=total,
            mapped_symbols=mapped,
            orphan_symbols=orphan_symbols,
            invalid_mappings=invalid_mappings,
            coverage_percentage=coverage,
            errors=errors,
        )

    def _should_check_symbol(self, symbol: CodeSymbol) -> bool:
        """
        Determine if symbol should be checked for traceability.

        Args:
            symbol: Code symbol

        Returns:
            True if symbol should be validated
        """
        # Skip private methods and attributes
        if symbol.name.startswith("_"):
            return False

        # Skip special methods
        if symbol.name in ["__init__", "__str__", "__repr__", "__eq__", "__hash__"]:
            return False

        # Skip test functions
        if symbol.name.startswith("test_"):
            return False

        # Skip setup/teardown methods
        if symbol.name in ["setUp", "tearDown", "setUpClass", "tearDownClass"]:
            return False

        return True

    def _is_excluded(self, symbol: CodeSymbol) -> bool:
        """
        Check if symbol matches exclusion patterns.

        Args:
            symbol: Code symbol

        Returns:
            True if symbol is excluded
        """
        # Check explicit exclusions
        if self.manifest.is_excluded(symbol.qualified_path):
            return True

        # Check pattern exclusions
        for pattern in self.manifest.exclusions.patterns:
            if fnmatch.fnmatch(symbol.file_path, pattern):
                return True

        return False
