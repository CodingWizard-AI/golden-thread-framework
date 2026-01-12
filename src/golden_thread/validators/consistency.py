"""Consistency validator for Notion ID validation."""

from dataclasses import dataclass, field
from typing import Dict, List

from ..manifest import Manifest
from ..notion.registry import NotionRegistry


@dataclass
class ConsistencyResult:
    """Results from consistency validation."""

    valid: bool
    errors: List[Dict] = field(default_factory=list)
    warnings: List[Dict] = field(default_factory=list)


class ConsistencyValidator:
    """Validates consistency with Notion registries."""

    def __init__(self, manifest: Manifest, registry: NotionRegistry):
        """
        Initialize consistency validator.

        Args:
            manifest: Service manifest
            registry: Notion registry interface
        """
        self.manifest = manifest
        self.registry = registry

    def validate(self) -> ConsistencyResult:
        """
        Validate consistency with Notion.

        Returns:
            ConsistencyResult with validation details
        """
        errors = []
        warnings = []

        # Get all IDs from manifest
        all_ids = self.manifest.get_all_referenced_ids()

        # Validate each ID exists in Notion and has correct format
        for id_type, ids in all_ids.items():
            for id_str in ids:
                # Validate format
                if not self.registry.validate_id_format(id_str):
                    errors.append(
                        {
                            "code": "INVALID_FORMAT",
                            "message": f"Invalid ID format: {id_str}",
                            "id": id_str,
                        }
                    )
                    continue

                # Check exists in Notion
                try:
                    entry = self.registry.get_entry(id_str)
                    if not entry:
                        errors.append(
                            {
                                "code": "INVALID_ID",
                                "message": f"ID not found in Notion: {id_str}",
                                "id": id_str,
                                "id_type": id_type,
                            }
                        )
                except Exception as e:
                    errors.append(
                        {
                            "code": "INVALID_ID",
                            "message": f"Error checking ID {id_str}: {str(e)}",
                            "id": id_str,
                        }
                    )

        # Validate traceability chains for features
        for feature in self.manifest.features:
            feat_id = feature.id

            try:
                chain_result = self.registry.validate_traceability_chain(feat_id)

                # Add errors with feature context
                for error_msg in chain_result.get("errors", []):
                    # Parse error code from message (format: "CODE: message")
                    parts = error_msg.split(":", 1)
                    code = parts[0].strip() if len(parts) > 1 else "VALIDATION_ERROR"

                    errors.append(
                        {
                            "code": code,
                            "message": error_msg,
                            "feature": feat_id,
                        }
                    )

                # Add warnings with feature context
                for warning_msg in chain_result.get("warnings", []):
                    # Parse warning code from message
                    parts = warning_msg.split(":", 1)
                    code = parts[0].strip() if len(parts) > 1 else "VALIDATION_WARNING"

                    warnings.append(
                        {
                            "code": code,
                            "message": warning_msg,
                            "feature": feat_id,
                        }
                    )
            except Exception as e:
                errors.append(
                    {
                        "code": "VALIDATION_ERROR",
                        "message": f"Failed to validate traceability chain for {feat_id}: {str(e)}",
                        "feature": feat_id,
                    }
                )

        return ConsistencyResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
