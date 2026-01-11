"""Python code parser using built-in AST module."""

import ast
from pathlib import Path
from typing import List

from ..import ParserError
from .base import BaseParser, CodeSymbol


class PythonParser(BaseParser):
    """Parser for Python source files."""

    def get_file_extensions(self) -> List[str]:
        """Return Python file extensions."""
        return [".py"]

    def parse(self) -> List[CodeSymbol]:
        """Parse all Python files in root directory."""
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
        Parse a single Python file using AST.

        Args:
            file_path: Path to Python file

        Returns:
            List of code symbols found

        Raises:
            ParserError: If file has syntax errors
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            raise ParserError(f"Failed to read file {file_path}: {e}")

        try:
            tree = ast.parse(source, filename=file_path)
        except SyntaxError as e:
            raise ParserError(f"Syntax error in {file_path}:{e.lineno}: {e.msg}")

        symbols = []

        # Make file path relative to root directory
        try:
            rel_path = str(Path(file_path).relative_to(self.root_directory))
        except ValueError:
            rel_path = file_path

        # Walk the AST
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Extract class
                if self._should_extract_symbol("class"):
                    symbols.append(
                        CodeSymbol(
                            name=node.name,
                            type="class",
                            file_path=rel_path,
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                        )
                    )

                # Extract methods from class
                if self._should_extract_symbol("method"):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            symbols.append(
                                CodeSymbol(
                                    name=item.name,
                                    type="method",
                                    file_path=rel_path,
                                    line_start=item.lineno,
                                    line_end=getattr(item, "end_lineno", item.lineno),
                                    parent=node.name,
                                )
                            )

        # Extract top-level functions (not inside classes)
        if self._should_extract_symbol("function"):
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append(
                        CodeSymbol(
                            name=node.name,
                            type="function",
                            file_path=rel_path,
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                        )
                    )

        return symbols
