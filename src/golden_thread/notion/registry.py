"""High-level interface to Notion registries."""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .. import NotionError, ID_PATTERNS
from .client import NotionClient


@dataclass
class RegistryEntry:
    """Represents an entry in a Notion registry."""

    id: str
    title: str
    status: str
    properties: Dict[str, Any]
    related_ids: Dict[str, List[str]] = field(default_factory=dict)


class NotionRegistry:
    """High-level interface to Notion registries."""

    # Mapping of ID type to expected property names for relations
    RELATION_PROPERTIES = {
        "FEAT": ["BR", "UR", "FR", "NFR", "TSR", "TCR", "CF"],
        "FR": ["V", "FEAT"],
        "NFR": ["V", "FEAT"],
        "TSR": ["V", "FEAT"],
        "TCR": ["V", "FEAT"],
        "V": ["TC", "FR", "NFR", "TSR", "TCR"],
        "TC": ["EA", "V"],
    }

    def __init__(self, client: NotionClient, database_ids: Dict[str, str]):
        """
        Initialize registry interface.

        Args:
            client: Notion API client
            database_ids: Mapping of ID type to database ID
        """
        self.client = client
        self.database_ids = database_ids

    def get_entry(self, id_str: str) -> Optional[RegistryEntry]:
        """
        Get a single registry entry by ID.

        Args:
            id_str: ID string (e.g., "FEAT-AUTH-001")

        Returns:
            RegistryEntry or None if not found

        Raises:
            NotionError: If ID type is unknown or API error
        """
        id_type = self._extract_id_type(id_str)
        if not id_type:
            raise NotionError(f"Invalid ID format: {id_str}")

        db_id = self.database_ids.get(id_type)
        if not db_id:
            raise NotionError(
                f"Unknown ID type: {id_type}\n"
                f"Please add {id_type} database ID to configuration."
            )

        # Query database for this ID
        # Note: Notion property names may vary, try common patterns
        filter_params = {"property": "ID", "title": {"equals": id_str}}

        try:
            results = self.client.search_database(db_id, filter_params)
        except NotionError:
            # Try alternative property name
            filter_params = {"property": "Name", "title": {"contains": id_str}}
            results = self.client.search_database(db_id, filter_params)

        if not results:
            return None

        return self._parse_entry(results[0], id_type)

    def get_entries_by_type(self, id_type: str) -> List[RegistryEntry]:
        """
        Get all entries for a registry type.

        Args:
            id_type: Registry type (BR, UR, FEAT, etc.)

        Returns:
            List of registry entries

        Raises:
            NotionError: If ID type is unknown or API error
        """
        db_id = self.database_ids.get(id_type)
        if not db_id:
            raise NotionError(f"Unknown ID type: {id_type}")

        results = self.client.search_database(db_id)
        return [self._parse_entry(r, id_type) for r in results]

    def validate_traceability_chain(self, feat_id: str) -> Dict[str, Any]:
        """
        Validate complete traceability chain for a feature.

        Args:
            feat_id: Feature ID (e.g., "FEAT-AUTH-001")

        Returns:
            Dictionary with validation results:
                - valid: bool
                - errors: List of error messages
                - warnings: List of warning messages
        """
        errors = []
        warnings = []

        # Get feature
        feat = self.get_entry(feat_id)
        if not feat:
            errors.append(f"INVALID_ID: {feat_id} not found in Feature Registry")
            return {"valid": False, "errors": errors, "warnings": warnings}

        # Check BR linkage
        if not feat.related_ids.get("BR"):
            errors.append(f"MISSING_BR: {feat_id} has no Business Requirement")

        # Check UR linkage
        if not feat.related_ids.get("UR"):
            errors.append(f"MISSING_UR: {feat_id} has no User Requirement")

        # Check FR linkage (at least one type of requirement)
        has_requirements = any(
            feat.related_ids.get(req_type) for req_type in ["FR", "NFR", "TSR", "TCR"]
        )
        if not has_requirements:
            errors.append(f"MISSING_FR: {feat_id} has no Functional Requirements")

        # Check CF linkage (warning only)
        if not feat.related_ids.get("CF"):
            warnings.append(f"MISSING_CF: {feat_id} has no Call Flow")

        # Validate each requirement has V-IDs
        for req_type in ["FR", "NFR", "TSR", "TCR"]:
            for req_id in feat.related_ids.get(req_type, []):
                req = self.get_entry(req_id)
                if not req:
                    errors.append(f"INVALID_ID: {req_id} not found")
                    continue

                if not req.related_ids.get("V"):
                    errors.append(f"MISSING_V: {req_id} has no Verification")
                    continue

                # Check each V has TC
                for v_id in req.related_ids.get("V", []):
                    v = self.get_entry(v_id)
                    if not v:
                        errors.append(f"INVALID_ID: {v_id} not found")
                        continue

                    if not v.related_ids.get("TC"):
                        errors.append(f"MISSING_TC: {v_id} has no Test Case")

                    # Critical rule: Verified V-IDs must have EA
                    if v.status and v.status.lower() == "verified":
                        if not v.related_ids.get("EA"):
                            errors.append(
                                f"MISSING_EA: {v_id} is Verified but has no Evidence Artifact"
                            )

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def validate_id_format(self, id_str: str) -> bool:
        """
        Validate ID format using regex patterns.

        Args:
            id_str: ID string to validate

        Returns:
            True if format is valid
        """
        id_type = self._extract_id_type(id_str)
        if not id_type:
            return False

        pattern = ID_PATTERNS.get(id_type)
        if not pattern:
            return False

        return bool(re.match(pattern, id_str))

    def _extract_id_type(self, id_str: str) -> Optional[str]:
        """Extract ID type from ID string."""
        parts = id_str.split("-")
        if len(parts) < 2:
            return None
        return parts[0]

    def _parse_entry(self, page: Dict, id_type: str) -> RegistryEntry:
        """
        Parse Notion page into RegistryEntry.

        Args:
            page: Notion page object
            id_type: Registry type

        Returns:
            RegistryEntry object
        """
        props = page.get("properties", {})

        # Extract ID (try different property names)
        id_value = (
            self._extract_property(props.get("ID"), "title")
            or self._extract_property(props.get("Name"), "title")
            or ""
        )

        # Extract title (try different property names)
        title = (
            self._extract_property(props.get("Title"), "rich_text")
            or self._extract_property(props.get("Description"), "rich_text")
            or self._extract_property(props.get("Name"), "rich_text")
            or ""
        )

        # Extract status
        status = (
            self._extract_property(props.get("Status"), "select")
            or self._extract_property(props.get("State"), "select")
            or ""
        )

        # Extract related IDs
        related_ids = self._extract_related_ids(props, id_type)

        return RegistryEntry(
            id=id_value, title=title, status=status, properties=props, related_ids=related_ids
        )

    def _extract_property(self, prop: Optional[Dict], prop_type: str) -> Any:
        """
        Extract value from Notion property structure.

        Args:
            prop: Property object
            prop_type: Property type (title, rich_text, select, etc.)

        Returns:
            Extracted value or empty string
        """
        if not prop:
            return ""

        try:
            if prop_type == "title":
                items = prop.get("title", [])
                return items[0].get("plain_text", "") if items else ""

            elif prop_type == "rich_text":
                items = prop.get("rich_text", [])
                return items[0].get("plain_text", "") if items else ""

            elif prop_type == "select":
                select_obj = prop.get("select")
                return select_obj.get("name", "") if select_obj else ""

            elif prop_type == "multi_select":
                return [item.get("name", "") for item in prop.get("multi_select", [])]

            elif prop_type == "relation":
                return [item.get("id", "") for item in prop.get("relation", [])]

        except (KeyError, AttributeError, IndexError):
            pass

        return ""

    def _extract_related_ids(self, props: Dict, id_type: str) -> Dict[str, List[str]]:
        """
        Extract related IDs from properties based on registry type.

        Args:
            props: Page properties
            id_type: Registry type

        Returns:
            Dictionary mapping relation type to list of IDs
        """
        related = {}

        # Get expected relation properties for this ID type
        relation_types = self.RELATION_PROPERTIES.get(id_type, [])

        for rel_type in relation_types:
            # Try different property name patterns
            for prop_name in [f"{rel_type}-IDs", f"{rel_type} IDs", rel_type]:
                if prop_name in props:
                    rel_ids = self._extract_property(props[prop_name], "relation")
                    if rel_ids:
                        # For relation properties, we get page IDs not actual IDs
                        # We would need to fetch each page to get the actual ID
                        # For now, store the relation page IDs
                        related[rel_type] = rel_ids
                        break

        return related
