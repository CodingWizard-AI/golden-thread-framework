"""TypeScript/JavaScript parser using tree-sitter."""

from pathlib import Path
from typing import List, Optional

from ..import ParserError
from .base import BaseParser, CodeSymbol


class TypeScriptParser(BaseParser):
    """Parser for TypeScript and JavaScript source files."""

    def __init__(self, root_directory: str, config: dict):
        """Initialize TypeScript parser."""
        super().__init__(root_directory, config)
        self.parser = None
        self.language = None
        self._initialize_tree_sitter()

    def _initialize_tree_sitter(self):
        """Initialize tree-sitter parser for TypeScript."""
        try:
            import tree_sitter_typescript as tstypescript
            from tree_sitter import Language, Parser

            # Get the TypeScript language
            TS_LANGUAGE = Language(tstypescript.language_typescript())

            self.parser = Parser(TS_LANGUAGE)
            self.language = TS_LANGUAGE
        except ImportError:
            # tree-sitter not available, parser will be disabled
            pass
        except Exception as e:
            raise ParserError(f"Failed to initialize TypeScript parser: {e}")

    def get_file_extensions(self) -> List[str]:
        """Return TypeScript/JavaScript file extensions."""
        return [".ts", ".tsx", ".js", ".jsx"]

    def parse(self) -> List[CodeSymbol]:
        """Parse all TypeScript/JavaScript files in root directory."""
        if not self.parser:
            # Parser not available
            return []

        symbols = []
        files = self.discover_files()

        for file_path in files:
            try:
                symbols.extend(self.parse_file(str(file_path)))
            except ParserError:
                # Skip files with syntax errors but continue parsing
                continue

        return symbols

    def parse_file(self, file_path: str) -> List[CodeSymbol]:
        """
        Parse a single TypeScript/JavaScript file using tree-sitter.

        Args:
            file_path: Path to file

        Returns:
            List of code symbols found

        Raises:
            ParserError: If parsing fails
        """
        if not self.parser:
            return []

        try:
            with open(file_path, "rb") as f:
                source = f.read()
        except Exception as e:
            raise ParserError(f"Failed to read file {file_path}: {e}")

        try:
            tree = self.parser.parse(source)
        except Exception as e:
            raise ParserError(f"Failed to parse {file_path}: {e}")

        symbols = []

        # Make file path relative to root directory
        try:
            rel_path = str(Path(file_path).relative_to(self.root_directory))
        except ValueError:
            rel_path = file_path

        # Query for symbols
        symbols.extend(self._extract_classes(tree.root_node, source, rel_path))
        symbols.extend(self._extract_functions(tree.root_node, source, rel_path))
        symbols.extend(self._extract_interfaces(tree.root_node, source, rel_path))
        symbols.extend(self._extract_types(tree.root_node, source, rel_path))

        return symbols

    def _extract_classes(self, root_node, source: bytes, file_path: str) -> List[CodeSymbol]:
        """Extract class declarations."""
        if not self._should_extract_symbol("class"):
            return []

        symbols = []
        query = self.language.query("(class_declaration name: (type_identifier) @class.name)")

        captures = query.captures(root_node)
        for node, _ in captures:
            name = source[node.start_byte : node.end_byte].decode("utf-8")
            symbols.append(
                CodeSymbol(
                    name=name,
                    type="class",
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                )
            )

        return symbols

    def _extract_functions(self, root_node, source: bytes, file_path: str) -> List[CodeSymbol]:
        """Extract function declarations."""
        if not self._should_extract_symbol("function"):
            return []

        symbols = []
        query = self.language.query(
            """
            (function_declaration name: (identifier) @function.name)
            (arrow_function) @arrow.function
            """
        )

        captures = query.captures(root_node)
        for node, capture_type in captures:
            if capture_type == "function.name":
                name = source[node.start_byte : node.end_byte].decode("utf-8")
                symbols.append(
                    CodeSymbol(
                        name=name,
                        type="function",
                        file_path=file_path,
                        line_start=node.start_point[0] + 1,
                        line_end=node.end_point[0] + 1,
                    )
                )

        return symbols

    def _extract_interfaces(self, root_node, source: bytes, file_path: str) -> List[CodeSymbol]:
        """Extract interface declarations."""
        if not self._should_extract_symbol("interface"):
            return []

        symbols = []
        query = self.language.query("(interface_declaration name: (type_identifier) @interface.name)")

        captures = query.captures(root_node)
        for node, _ in captures:
            name = source[node.start_byte : node.end_byte].decode("utf-8")
            symbols.append(
                CodeSymbol(
                    name=name,
                    type="interface",
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                )
            )

        return symbols

    def _extract_types(self, root_node, source: bytes, file_path: str) -> List[CodeSymbol]:
        """Extract type alias declarations."""
        if not self._should_extract_symbol("type"):
            return []

        symbols = []
        query = self.language.query("(type_alias_declaration name: (type_identifier) @type.name)")

        captures = query.captures(root_node)
        for node, _ in captures:
            name = source[node.start_byte : node.end_byte].decode("utf-8")
            symbols.append(
                CodeSymbol(
                    name=name,
                    type="type",
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                )
            )

        return symbols
