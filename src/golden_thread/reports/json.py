"""JSON reporter for CI/CD integration."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .. import __version__


class JSONReporter:
    """Generates JSON reports for CI/CD parsing."""

    def __init__(self, output_path: str):
        """
        Initialize JSON reporter.

        Args:
            output_path: Path to output file
        """
        self.output_path = Path(output_path)

    def generate(self, validation_results: Dict[str, Any]) -> str:
        """
        Generate JSON report.

        Args:
            validation_results: Validation results dictionary

        Returns:
            JSON string
        """
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "1.0",
                "framework_version": __version__,
                "service": validation_results.get("service", "unknown"),
            },
            "summary": {
                "valid": validation_results.get("valid", False),
                "total_errors": len(validation_results.get("errors", [])),
                "total_warnings": len(validation_results.get("warnings", [])),
                "coverage_percentage": validation_results.get("coverage_percentage", 0.0),
            },
            "errors": validation_results.get("errors", []),
            "warnings": validation_results.get("warnings", []),
            "coverage": {
                "total_symbols": validation_results.get("total_symbols", 0),
                "mapped_symbols": validation_results.get("mapped_symbols", 0),
                "orphan_symbols": validation_results.get("orphan_symbols", []),
                "invalid_mappings": validation_results.get("invalid_mappings", []),
            },
        }

        # Write to file
        with open(self.output_path, "w") as f:
            json.dump(report, f, indent=2)

        return json.dumps(report, indent=2)
