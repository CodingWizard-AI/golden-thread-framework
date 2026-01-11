"""Base parser interface for all language parsers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CodeSymbol:
    """Represents a parsed code symbol (class, function, method, etc.)."""

    name: str
    type: str  # class, function, method, interface, struct, etc.
    file_path: str
    line_start: int
    line_end: int
    parent: Optional[str] = None  # For methods: parent class/struct name

    @property
    def qualified_path(self) -> str:
        """
        Return symbol path in manifest format.

        Examples:
            - "auth/oauth.py::OAuthProvider" (class)
            - "auth/oauth.py::OAuthProvider.authenticate" (method)
            - "utils/helpers.py::format_date" (function)
        """
        if self.parent:
            return f"{self.file_path}::{self.parent}.{self.name}"
        return f"{self.file_path}::{self.name}"


class BaseParser(ABC):
    """Abstract base class for all language parsers."""

    def __init__(self, root_directory: str, config: Dict):
        """
        Initialize parser.

        Args:
            root_directory: Root directory to parse
            config: Parser configuration dictionary
        """
        self.root_directory = Path(root_directory)
        self.config = config
        self.ignore_patterns = config.get("ignore_patterns", [])

    @abstractmethod
    def parse(self) -> List[CodeSymbol]:
        """
        Parse all files in root directory.

        Returns:
            List of discovered code symbols
        """
        pass

    @abstractmethod
    def parse_file(self, file_path: str) -> List[CodeSymbol]:
        """
        Parse a single file.

        Args:
            file_path: Path to file

        Returns:
            List of symbols found in file
        """
        pass

    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """
        Return file extensions this parser handles.

        Returns:
            List of extensions (e.g., ['.py', '.pyx'])
        """
        pass

    def discover_files(self) -> List[Path]:
        """
        Find all files this parser should process.

        Returns:
            List of file paths
        """
        extensions = self.get_file_extensions()
        files = []

        for ext in extensions:
            # Use rglob for recursive glob
            pattern = f"*{ext}"
            files.extend(self.root_directory.rglob(pattern))

        # Apply ignore patterns
        return [f for f in files if not self._should_ignore(f)]

    def _should_ignore(self, file_path: Path) -> bool:
        """
        Check if file matches ignore patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file should be ignored
        """
        # Convert to relative path for pattern matching
        try:
            rel_path = file_path.relative_to(self.root_directory)
        except ValueError:
            # File is not relative to root directory
            return True

        for pattern in self.ignore_patterns:
            # Use Path.match() which handles ** patterns correctly
            if rel_path.match(pattern):
                return True
            # For patterns starting with **, also check without the **/ prefix
            # to match files at the root level
            if pattern.startswith("**/"):
                simple_pattern = pattern[3:]  # Remove "**/""
                if rel_path.match(simple_pattern):
                    return True

        return False

    def _should_extract_symbol(self, symbol_type: str) -> bool:
        """
        Check if symbol type should be extracted based on config.

        Args:
            symbol_type: Type of symbol (class, function, etc.)

        Returns:
            True if symbol should be extracted
        """
        extract_types = self.config.get("extract", [])
        if not extract_types:
            # If no extract config, extract everything
            return True

        # Map plural forms to singular
        type_map = {
            "classes": "class",
            "functions": "function",
            "methods": "method",
            "interfaces": "interface",
            "types": "type",
            "structs": "struct",
        }

        # Check both singular and plural forms
        return (
            symbol_type in extract_types
            or symbol_type + "s" in extract_types
            or type_map.get(symbol_type) in extract_types
        )
