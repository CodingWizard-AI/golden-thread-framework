"""Tests for Python parser."""

import tempfile
from pathlib import Path

import pytest

from golden_thread.parsers.python_parser import PythonParser


class TestPythonParser:
    """Test Python AST parser."""

    def test_parse_classes(self, tmp_path):
        """Test parsing Python classes."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
class OAuthProvider:
    '''OAuth provider class.'''
    pass

class UserSession:
    '''User session class.'''
    def __init__(self):
        pass
"""
        )

        parser = PythonParser(str(tmp_path), {"ignore_patterns": []})
        symbols = parser.parse()

        classes = [s for s in symbols if s.type == "class"]
        assert len(classes) == 2
        assert "OAuthProvider" in [c.name for c in classes]
        assert "UserSession" in [c.name for c in classes]

    def test_parse_functions(self, tmp_path):
        """Test parsing top-level functions."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def authenticate(username, password):
    '''Authenticate user.'''
    pass

async def fetch_user(user_id):
    '''Fetch user asynchronously.'''
    pass
"""
        )

        parser = PythonParser(str(tmp_path), {"ignore_patterns": []})
        symbols = parser.parse()

        functions = [s for s in symbols if s.type == "function"]
        assert len(functions) == 2
        assert "authenticate" in [f.name for f in functions]
        assert "fetch_user" in [f.name for f in functions]

    def test_parse_methods(self, tmp_path):
        """Test parsing methods within classes."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
class AuthService:
    def login(self, username, password):
        pass

    async def logout(self):
        pass
"""
        )

        parser = PythonParser(str(tmp_path), {"ignore_patterns": []})
        symbols = parser.parse()

        methods = [s for s in symbols if s.type == "method"]
        assert len(methods) == 2
        assert all(m.parent == "AuthService" for m in methods)
        assert "login" in [m.name for m in methods]
        assert "logout" in [m.name for m in methods]

    def test_qualified_path_generation(self, tmp_path):
        """Test qualified path generation for symbols."""
        test_file = tmp_path / "auth" / "oauth.py"
        test_file.parent.mkdir()
        test_file.write_text(
            """
class OAuthProvider:
    def authenticate(self):
        pass
"""
        )

        parser = PythonParser(str(tmp_path), {"ignore_patterns": []})
        symbols = parser.parse()

        class_symbol = [s for s in symbols if s.type == "class"][0]
        method_symbol = [s for s in symbols if s.type == "method"][0]

        assert class_symbol.qualified_path == "auth/oauth.py::OAuthProvider"
        assert method_symbol.qualified_path == "auth/oauth.py::OAuthProvider.authenticate"

    def test_ignore_patterns(self, tmp_path):
        """Test file ignore patterns."""
        # Create test file
        test_file = tmp_path / "test_auth.py"
        test_file.write_text(
            """
class TestClass:
    pass
"""
        )

        # Create normal file
        normal_file = tmp_path / "auth.py"
        normal_file.write_text(
            """
class AuthClass:
    pass
"""
        )

        parser = PythonParser(str(tmp_path), {"ignore_patterns": ["**/test_*.py"]})
        symbols = parser.parse()

        # Should only parse auth.py, not test_auth.py
        assert len(symbols) == 1
        assert symbols[0].name == "AuthClass"

    def test_parse_syntax_error(self, tmp_path):
        """Test handling files with syntax errors."""
        test_file = tmp_path / "bad.py"
        test_file.write_text("def bad_function(\n  # Missing closing paren")

        parser = PythonParser(str(tmp_path), {"ignore_patterns": []})

        # Should not raise, just skip the file
        symbols = parser.parse()
        assert len(symbols) == 0

    def test_get_file_extensions(self):
        """Test file extensions returned by parser."""
        parser = PythonParser("/tmp", {})
        extensions = parser.get_file_extensions()

        assert ".py" in extensions
        assert len(extensions) == 1

    def test_parse_empty_directory(self, tmp_path):
        """Test parsing an empty directory."""
        parser = PythonParser(str(tmp_path), {"ignore_patterns": []})
        symbols = parser.parse()

        assert len(symbols) == 0

    def test_line_numbers(self, tmp_path):
        """Test that line numbers are correctly captured."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
class TestClass:
    def method(self):
        pass
"""
        )

        parser = PythonParser(str(tmp_path), {"ignore_patterns": []})
        symbols = parser.parse()

        class_symbol = [s for s in symbols if s.type == "class"][0]
        assert class_symbol.line_start == 2
        assert class_symbol.line_end >= 2

        method_symbol = [s for s in symbols if s.type == "method"][0]
        assert method_symbol.line_start == 3
