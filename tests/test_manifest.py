"""Tests for manifest parsing."""

import pytest
import yaml

from golden_thread import ManifestError
from golden_thread.manifest import Manifest, SymbolMapping


class TestManifest:
    """Test manifest loading and validation."""

    def test_load_valid_manifest(self, tmp_path):
        """Test loading a valid manifest file."""
        manifest_file = tmp_path / ".golden-thread.yaml"
        manifest_data = {
            "service": "test-service",
            "version": "1.0",
            "metadata": {"owner": "test-team"},
            "traceability": {
                "features": [
                    {
                        "id": "FEAT-TEST-001",
                        "description": "Test feature",
                        "business_requirements": ["BR-TEST-001"],
                        "user_requirements": ["UR-TEST-001"],
                    }
                ],
                "symbols": [
                    {
                        "path": "auth/oauth.py::OAuthProvider",
                        "type": "class",
                        "ids": ["FEAT-TEST-001", "FR-TEST-001"],
                    }
                ],
            },
        }

        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        manifest = Manifest.load(str(manifest_file))

        assert manifest.service == "test-service"
        assert manifest.version == "1.0"
        assert len(manifest.features) == 1
        assert len(manifest.symbols) == 1
        assert manifest.features[0].id == "FEAT-TEST-001"
        assert manifest.symbols[0].path == "auth/oauth.py::OAuthProvider"

    def test_load_manifest_missing_service(self, tmp_path):
        """Test error when service field is missing."""
        manifest_file = tmp_path / ".golden-thread.yaml"
        manifest_data = {"version": "1.0"}

        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        with pytest.raises(ManifestError, match="service"):
            Manifest.load(str(manifest_file))

    def test_load_manifest_missing_version(self, tmp_path):
        """Test error when version field is missing."""
        manifest_file = tmp_path / ".golden-thread.yaml"
        manifest_data = {"service": "test-service"}

        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        with pytest.raises(ManifestError, match="version"):
            Manifest.load(str(manifest_file))

    def test_load_manifest_file_not_found(self):
        """Test error when manifest file doesn't exist."""
        with pytest.raises(ManifestError, match="not found"):
            Manifest.load("nonexistent.yaml")

    def test_load_manifest_empty_file(self, tmp_path):
        """Test error when manifest file is empty."""
        manifest_file = tmp_path / ".golden-thread.yaml"
        manifest_file.touch()

        with pytest.raises(ManifestError, match="empty"):
            Manifest.load(str(manifest_file))

    def test_symbol_mapping_qualified_path(self):
        """Test qualified path generation for symbols."""
        # Class
        symbol = SymbolMapping(
            path="auth/oauth.py::OAuthProvider", type="class", ids=["FEAT-TEST-001"]
        )
        assert symbol.qualified_path == "auth/oauth.py::OAuthProvider"
        assert symbol.file_path == "auth/oauth.py"
        assert symbol.symbol_name == "OAuthProvider"

        # Method
        symbol = SymbolMapping(
            path="auth/oauth.py::OAuthProvider.authenticate", type="method", ids=["FR-TEST-001"]
        )
        assert symbol.qualified_path == "auth/oauth.py::OAuthProvider.authenticate"

    def test_get_ids_for_symbol(self, tmp_path):
        """Test getting IDs for a specific symbol."""
        manifest_file = tmp_path / ".golden-thread.yaml"
        manifest_data = {
            "service": "test-service",
            "version": "1.0",
            "traceability": {
                "symbols": [
                    {
                        "path": "auth/oauth.py::OAuthProvider",
                        "type": "class",
                        "ids": ["FEAT-TEST-001", "FR-TEST-001"],
                    }
                ]
            },
        }

        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        manifest = Manifest.load(str(manifest_file))

        ids = manifest.get_ids_for_symbol("auth/oauth.py::OAuthProvider")
        assert "FEAT-TEST-001" in ids
        assert "FR-TEST-001" in ids
        assert len(ids) == 2

        # Non-existent symbol
        ids = manifest.get_ids_for_symbol("nonexistent")
        assert len(ids) == 0

    def test_get_all_referenced_ids(self, tmp_path):
        """Test getting all referenced IDs grouped by type."""
        manifest_file = tmp_path / ".golden-thread.yaml"
        manifest_data = {
            "service": "test-service",
            "version": "1.0",
            "traceability": {
                "features": [
                    {
                        "id": "FEAT-TEST-001",
                        "description": "Test",
                        "business_requirements": ["BR-TEST-001"],
                        "user_requirements": ["UR-TEST-001", "UR-TEST-002"],
                    }
                ],
                "symbols": [
                    {"path": "test.py::TestClass", "type": "class", "ids": ["FR-TEST-001"]}
                ],
                "tests": [
                    {
                        "path": "tests/test_auth.py::test_login",
                        "test_cases": ["TC-TEST-001"],
                        "verifications": ["V-TEST-001"],
                    }
                ],
            },
        }

        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        manifest = Manifest.load(str(manifest_file))

        ids_by_type = manifest.get_all_referenced_ids()

        assert "FEAT-TEST-001" in ids_by_type["FEAT"]
        assert "BR-TEST-001" in ids_by_type["BR"]
        assert len(ids_by_type["UR"]) == 2
        assert "FR-TEST-001" in ids_by_type["FR"]
        assert "TC-TEST-001" in ids_by_type["TC"]
        assert "V-TEST-001" in ids_by_type["V"]

    def test_get_symbol_paths(self, tmp_path):
        """Test getting all symbol paths."""
        manifest_file = tmp_path / ".golden-thread.yaml"
        manifest_data = {
            "service": "test-service",
            "version": "1.0",
            "traceability": {
                "symbols": [
                    {"path": "auth/oauth.py::OAuthProvider", "type": "class", "ids": ["FEAT-001"]},
                    {
                        "path": "auth/oauth.py::OAuthProvider.login",
                        "type": "method",
                        "ids": ["FR-001"],
                    },
                ]
            },
        }

        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        manifest = Manifest.load(str(manifest_file))

        paths = manifest.get_symbol_paths()
        assert "auth/oauth.py::OAuthProvider" in paths
        assert "auth/oauth.py::OAuthProvider.login" in paths
        assert len(paths) == 2

    def test_is_excluded(self, tmp_path):
        """Test checking if symbol is excluded."""
        manifest_file = tmp_path / ".golden-thread.yaml"
        manifest_data = {
            "service": "test-service",
            "version": "1.0",
            "exclusions": {"symbols": ["auth/legacy.py::OldAuth", "utils/deprecated.py::old_func"]},
        }

        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        manifest = Manifest.load(str(manifest_file))

        assert manifest.is_excluded("auth/legacy.py::OldAuth") is True
        assert manifest.is_excluded("auth/oauth.py::OAuthProvider") is False

    def test_manifest_missing_symbol_fields(self, tmp_path):
        """Test error when symbol mapping is missing required fields."""
        manifest_file = tmp_path / ".golden-thread.yaml"

        # Missing path
        manifest_data = {
            "service": "test-service",
            "version": "1.0",
            "traceability": {"symbols": [{"type": "class", "ids": ["FEAT-001"]}]},
        }

        with open(manifest_file, "w") as f:
            yaml.dump(manifest_data, f)

        with pytest.raises(ManifestError, match="path"):
            Manifest.load(str(manifest_file))
