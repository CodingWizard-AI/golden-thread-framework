"""Go parser using tree-sitter."""

from pathlib import Path
from typing import List

from ..import ParserError
from .base import BaseParser, CodeSymbol


class GoParser(BaseParser):
    """Parser for Go source files."""

    def __init__(self, root_directory: str, config: dict):
        """Initialize Go parser."""
        super().__init__(root_directory, config)
        self.parser = None
        self.language = None
        self._initialize_tree_sitter()

    def _initialize_tree_sitter(self):
        """Initialize tree-sitter parser for Go."""
        try:
            import tree_sitter_go as tsgo
            from tree_sitter import Language, Parser

            # Get the Go language
            GO_LANGUAGE = Language(tsgo.language())

            self.parser = Parser(GO_LANGUAGE)
            self.language = GO_LANGUAGE
        except ImportError:
            # tree-sitter not available, parser will be disabled
            pass
        except Exception as e:
            raise ParserError(f"Failed to initialize Go parser: {e}")

    def get_file_extensions(self) -> List[str]:
        """Return Go file extensions."""
        return [".go"]

    def parse(self) -> List[CodeSymbol]:
        """Parse all Go files in root directory."""
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
        Parse a single Go file using tree-sitter.

        Args:
            file_path: Path to Go file

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
        symbols.extend(self._extract_structs(tree.root_node, source, rel_path))
        symbols.extend(self._extract_interfaces(tree.root_node, source, rel_path))
        symbols.extend(self._extract_functions(tree.root_node, source, rel_path))
        symbols.extend(self._extract_methods(tree.root_node, source, rel_path))

        return symbols

    def _extract_structs(self, root_node, source: bytes, file_path: str) -> List[CodeSymbol]:
        """Extract struct declarations."""
        if not self._should_extract_symbol("struct"):
            return []

        symbols = []
        query = self.language.query(
            "(type_declaration (type_spec name: (type_identifier) @struct.name type: (struct_type)))"
        )

        captures = query.captures(root_node)
        for node, _ in captures:
            name = source[node.start_byte : node.end_byte].decode("utf-8")
            symbols.append(
                CodeSymbol(
                    name=name,
                    type="struct",
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
        query = self.language.query(
            "(type_declaration (type_spec name: (type_identifier) @interface.name type: (interface_type)))"
        )

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

    def _extract_functions(self, root_node, source: bytes, file_path: str) -> List[CodeSymbol]:
        """Extract top-level function declarations."""
        if not self._should_extract_symbol("function"):
            return []

        symbols = []
        query = self.language.query("(function_declaration name: (identifier) @function.name)")

        captures = query.captures(root_node)
        for node, _ in captures:
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

    def _extract_methods(self, root_node, source: bytes, file_path: str) -> List[CodeSymbol]:
        """Extract method declarations (functions with receivers)."""
        if not self._should_extract_symbol("method"):
            return []

        symbols = []
        query = self.language.query(
            """
            (method_declaration
                receiver: (parameter_list
                    (parameter_declaration
                        type: [(type_identifier) (pointer_type (type_identifier))] @receiver.type))
                name: (field_identifier) @method.name)
            """
        )

        captures = query.captures(root_node)

        # Group captures by method
        method_info = {}
        for node, capture_type in captures:
            node_id = (node.start_point[0], node.end_point[0])

            if capture_type == "method.name":
                method_name = source[node.start_byte : node.end_byte].decode("utf-8")
                if node_id not in method_info:
                    method_info[node_id] = {"name": method_name, "receiver": None}
                else:
                    method_info[node_id]["name"] = method_name

            elif capture_type == "receiver.type":
                receiver_type = source[node.start_byte : node.end_byte].decode("utf-8")
                # Clean up pointer syntax
                receiver_type = receiver_type.lstrip("*")

                if node_id not in method_info:
                    method_info[node_id] = {"name": None, "receiver": receiver_type}
                else:
                    method_info[node_id]["receiver"] = receiver_type

        # Create CodeSymbol for each method
        for (line_start, line_end), info in method_info.items():
            if info["name"]:
                symbols.append(
                    CodeSymbol(
                        name=info["name"],
                        type="method",
                        file_path=file_path,
                        line_start=line_start + 1,
                        line_end=line_end + 1,
                        parent=info.get("receiver"),
                    )
                )

        return symbols
