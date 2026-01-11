"""Manifest parsing and validation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from . import ManifestError


@dataclass
class SymbolMapping:
    """Maps a code symbol to requirement IDs."""

    path: str  # Format: "module.py::ClassName.method_name"
    type: str  # class, function, method, interface, struct, endpoint, etc.
    ids: List[str]  # List of requirement IDs (BR-XXX-001, FR-XXX-002, etc.)

    @property
    def file_path(self) -> str:
        """Extract file path from symbol path."""
        return self.path.split("::")[0] if "::" in self.path else self.path

    @property
    def symbol_name(self) -> str:
        """Extract symbol name from symbol path."""
        return self.path.split("::", 1)[1] if "::" in self.path else ""

    @property
    def qualified_path(self) -> str:
        """Return the full qualified path."""
        return self.path


@dataclass
class FeatureMapping:
    """Feature-level traceability mapping."""

    id: str
    description: str
    business_requirements: List[str] = field(default_factory=list)
    user_requirements: List[str] = field(default_factory=list)
    call_flows: List[str] = field(default_factory=list)


@dataclass
class InterfaceMapping:
    """Interface/API mapping."""

    id: str
    type: str  # rest_api, graphql, grpc
    endpoint: Optional[str] = None
    operation: Optional[str] = None
    service: Optional[str] = None
    method: Optional[str] = None
    requirements: List[str] = field(default_factory=list)


@dataclass
class TestMapping:
    """Test case mapping."""

    path: str
    test_cases: List[str] = field(default_factory=list)
    verifications: List[str] = field(default_factory=list)


@dataclass
class Exclusions:
    """Patterns and symbols to exclude from validation."""

    patterns: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)


@dataclass
class Manifest:
    """Service traceability manifest."""

    service: str
    version: str
    metadata: Dict[str, Any]
    symbols: List[SymbolMapping]
    features: List[FeatureMapping] = field(default_factory=list)
    interfaces: List[InterfaceMapping] = field(default_factory=list)
    tests: List[TestMapping] = field(default_factory=list)
    exclusions: Exclusions = field(default_factory=Exclusions)

    @classmethod
    def load(cls, path: str) -> "Manifest":
        """
        Load manifest from YAML file.

        Args:
            path: Path to .golden-thread.yaml file

        Returns:
            Manifest object

        Raises:
            ManifestError: If manifest file is invalid or missing
        """
        manifest_file = Path(path)

        if not manifest_file.exists():
            raise ManifestError(
                f"Manifest file not found: {path}\n"
                f"Please create a .golden-thread.yaml file for this service."
            )

        try:
            with open(manifest_file) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ManifestError(f"Failed to parse manifest file: {e}")

        if not data:
            raise ManifestError("Manifest file is empty")

        try:
            return cls.from_dict(data)
        except Exception as e:
            raise ManifestError(f"Invalid manifest format: {e}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Manifest":
        """Construct Manifest from dictionary."""
        # Validate required fields
        if "service" not in data:
            raise ManifestError("Missing required field: service")
        if "version" not in data:
            raise ManifestError("Missing required field: version")

        service = data["service"]
        version = data["version"]
        metadata = data.get("metadata", {})

        # Parse traceability section
        traceability = data.get("traceability", {})

        # Parse features
        features_data = traceability.get("features", [])
        features = []
        for feat_data in features_data:
            features.append(FeatureMapping(
                id=feat_data["id"],
                description=feat_data.get("description", ""),
                business_requirements=feat_data.get("business_requirements", []),
                user_requirements=feat_data.get("user_requirements", []),
                call_flows=feat_data.get("call_flows", []),
            ))

        # Parse symbols
        symbols_data = traceability.get("symbols", [])
        symbols = []
        for sym_data in symbols_data:
            if "path" not in sym_data:
                raise ManifestError("Symbol mapping missing required field: path")
            if "type" not in sym_data:
                raise ManifestError(f"Symbol mapping '{sym_data['path']}' missing required field: type")
            if "ids" not in sym_data:
                raise ManifestError(f"Symbol mapping '{sym_data['path']}' missing required field: ids")

            symbols.append(SymbolMapping(
                path=sym_data["path"],
                type=sym_data["type"],
                ids=sym_data["ids"],
            ))

        # Parse interfaces
        interfaces_data = traceability.get("interfaces", [])
        interfaces = []
        for iface_data in interfaces_data:
            interfaces.append(InterfaceMapping(
                id=iface_data["id"],
                type=iface_data["type"],
                endpoint=iface_data.get("endpoint"),
                operation=iface_data.get("operation"),
                service=iface_data.get("service"),
                method=iface_data.get("method"),
                requirements=iface_data.get("requirements", []),
            ))

        # Parse tests
        tests_data = traceability.get("tests", [])
        tests = []
        for test_data in tests_data:
            tests.append(TestMapping(
                path=test_data["path"],
                test_cases=test_data.get("test_cases", []),
                verifications=test_data.get("verifications", []),
            ))

        # Parse exclusions
        exclusions_data = data.get("exclusions", {})
        exclusions = Exclusions(
            patterns=exclusions_data.get("patterns", []),
            symbols=exclusions_data.get("symbols", []),
        )

        return cls(
            service=service,
            version=version,
            metadata=metadata,
            symbols=symbols,
            features=features,
            interfaces=interfaces,
            tests=tests,
            exclusions=exclusions,
        )

    def get_ids_for_symbol(self, symbol_path: str) -> Set[str]:
        """
        Get all IDs mapped to a code symbol.

        Args:
            symbol_path: Qualified symbol path (e.g., "auth/oauth.py::OAuthProvider.authenticate")

        Returns:
            Set of requirement IDs
        """
        for mapping in self.symbols:
            if mapping.path == symbol_path:
                return set(mapping.ids)
        return set()

    def get_all_referenced_ids(self) -> Dict[str, Set[str]]:
        """
        Get all IDs referenced in manifest, grouped by type.

        Returns:
            Dictionary mapping ID type (BR, UR, FEAT, etc.) to set of IDs
        """
        ids_by_type: Dict[str, Set[str]] = {}

        # IDs from symbol mappings
        for symbol in self.symbols:
            for id_str in symbol.ids:
                id_type = id_str.split("-")[0]
                ids_by_type.setdefault(id_type, set()).add(id_str)

        # IDs from feature mappings
        for feature in self.features:
            # Feature ID itself
            id_type = feature.id.split("-")[0]
            ids_by_type.setdefault(id_type, set()).add(feature.id)

            # Linked requirements
            for br_id in feature.business_requirements:
                ids_by_type.setdefault("BR", set()).add(br_id)
            for ur_id in feature.user_requirements:
                ids_by_type.setdefault("UR", set()).add(ur_id)
            for cf_id in feature.call_flows:
                ids_by_type.setdefault("CF", set()).add(cf_id)

        # IDs from interface mappings
        for iface in self.interfaces:
            id_type = iface.id.split("-")[0]
            ids_by_type.setdefault(id_type, set()).add(iface.id)

            for req_id in iface.requirements:
                req_type = req_id.split("-")[0]
                ids_by_type.setdefault(req_type, set()).add(req_id)

        # IDs from test mappings
        for test in self.tests:
            for tc_id in test.test_cases:
                ids_by_type.setdefault("TC", set()).add(tc_id)
            for v_id in test.verifications:
                ids_by_type.setdefault("V", set()).add(v_id)

        return ids_by_type

    def get_symbol_paths(self) -> Set[str]:
        """Get all symbol paths defined in manifest."""
        return {symbol.path for symbol in self.symbols}

    def is_excluded(self, symbol_path: str) -> bool:
        """
        Check if a symbol is explicitly excluded.

        Args:
            symbol_path: Qualified symbol path

        Returns:
            True if symbol is in exclusion list
        """
        return symbol_path in self.exclusions.symbols
