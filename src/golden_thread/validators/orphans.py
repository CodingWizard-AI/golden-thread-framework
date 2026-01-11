"""Orphan detection validator."""

from dataclasses import dataclass, field
from difflib import get_close_matches
from pathlib import Path
from typing import Dict, List

from ..manifest import Manifest
from ..parsers.base import CodeSymbol


@dataclass
class OrphanResult:
    """Results from orphan detection."""

    orphan_code: List[Dict] = field(default_factory=list)
    orphan_manifest: List[Dict] = field(default_factory=list)
    suggestions: List[Dict] = field(default_factory=list)


class OrphanValidator:
    """Detects orphaned code and manifest entries."""

    def __init__(self, manifest: Manifest, parsed_symbols: List[CodeSymbol]):
        """
        Initialize orphan validator.

        Args:
            manifest: Service manifest
            parsed_symbols: List of parsed code symbols
        """
        self.manifest = manifest
        self.parsed_symbols = parsed_symbols

    def detect_orphans(self) -> OrphanResult:
        """
        Detect all orphaned code and manifest entries.

        Returns:
            OrphanResult with orphan details and suggestions
        """
        orphan_code = []
        orphan_manifest = []
        suggestions = []

        # Build lookup maps
        manifest_paths = self.manifest.get_symbol_paths()
        symbol_paths = {s.qualified_path for s in self.parsed_symbols}

        # Find orphaned code
        for symbol in self.parsed_symbols:
            if symbol.qualified_path not in manifest_paths:
                if not self._is_excluded(symbol) and self._should_check_symbol(symbol):
                    orphan_code.append(
                        {
                            "path": symbol.qualified_path,
                            "type": symbol.type,
                            "file": symbol.file_path,
                            "line": symbol.line_start,
                        }
                    )

                    # Generate suggestion
                    suggestions.append(
                        {
                            "orphan": symbol.qualified_path,
                            "type": "code",
                            "suggestion": self._generate_manifest_snippet(symbol),
                        }
                    )

        # Find orphaned manifest entries
        for mapping in self.manifest.symbols:
            if mapping.path not in symbol_paths:
                orphan_manifest.append({"path": mapping.path, "ids": mapping.ids})

                # Suggest similar symbols
                similar = self._find_similar_symbols(mapping.path)
                if similar:
                    suggestions.append(
                        {
                            "orphan": mapping.path,
                            "type": "manifest",
                            "suggestion": f"Did you mean one of these?\n"
                            + "\n".join(f"  - {s}" for s in similar),
                        }
                    )
                else:
                    suggestions.append(
                        {
                            "orphan": mapping.path,
                            "type": "manifest",
                            "suggestion": "Symbol not found in codebase. "
                            "Consider removing from manifest or fixing the path.",
                        }
                    )

        return OrphanResult(
            orphan_code=orphan_code, orphan_manifest=orphan_manifest, suggestions=suggestions
        )

    def _should_check_symbol(self, symbol: CodeSymbol) -> bool:
        """Check if symbol should be validated."""
        if symbol.name.startswith("_"):
            return False
        if symbol.name in ["__init__", "__str__", "__repr__", "__eq__", "__hash__"]:
            return False
        if symbol.name.startswith("test_"):
            return False
        return True

    def _is_excluded(self, symbol: CodeSymbol) -> bool:
        """Check if symbol is excluded."""
        if self.manifest.is_excluded(symbol.qualified_path):
            return True

        for pattern in self.manifest.exclusions.patterns:
            # Use Path.match() which handles ** patterns correctly
            if Path(symbol.file_path).match(pattern):
                return True

        return False

    def _find_similar_symbols(self, path: str) -> List[str]:
        """
        Find similar symbol paths using fuzzy matching.

        Args:
            path: Symbol path to match

        Returns:
            List of similar paths
        """
        symbol_paths = [s.qualified_path for s in self.parsed_symbols]
        return get_close_matches(path, symbol_paths, n=3, cutoff=0.6)

    def _generate_manifest_snippet(self, symbol: CodeSymbol) -> str:
        """
        Generate YAML snippet for adding symbol to manifest.

        Args:
            symbol: Code symbol

        Returns:
            YAML snippet as string
        """
        return (
            f"Add to .golden-thread.yaml:\n\n"
            f"  - path: \"{symbol.qualified_path}\"\n"
            f"    type: {symbol.type}\n"
            f"    ids:\n"
            f"      - FEAT-XXX-001  # Replace with actual feature ID\n"
            f"      - FR-XXX-001    # Replace with actual requirement ID"
        )
