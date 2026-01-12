"""Command-line interface for Golden Thread Framework."""

import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import Config
from .manifest import Manifest
from .notion.client import NotionClient
from .notion.registry import NotionRegistry
from .parsers.python_parser import PythonParser
from .parsers.typescript_parser import TypeScriptParser
from .parsers.go_parser import GoParser
from .validators.coverage import CoverageValidator
from .validators.consistency import ConsistencyValidator
from .validators.orphans import OrphanValidator
from .reports.json import JSONReporter

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """Golden Thread Framework - Code Traceability Validation."""
    pass


@cli.command()
@click.option("--service", help="Service name to validate (path to service directory)")
@click.option("--all", "validate_all", is_flag=True, help="Validate entire monorepo")
@click.option(
    "--output",
    type=click.Choice(["console", "json"]),
    default="console",
    help="Output format",
)
@click.option("--strict", is_flag=True, help="Fail on warnings (exit code 1)")
@click.option(
    "--config",
    default=".golden-thread.config.yaml",
    help="Config file path",
)
def validate(
    service: Optional[str],
    validate_all: bool,
    output: str,
    strict: bool,
    config: str,
):
    """Validate traceability coverage for services."""
    try:
        # Load configuration
        cfg = Config.load(config)

        if validate_all:
            console.print("[yellow]Validating all services...[/yellow]")
            services = discover_services(cfg)
            if not services:
                console.print("[red]No services found with .golden-thread.yaml[/red]")
                sys.exit(1)
        elif service:
            services = [Path(service)]
        else:
            console.print("[red]Error: Specify --service or --all[/red]")
            sys.exit(1)

        # Validate each service
        all_results = []
        for service_path in services:
            result = validate_service(service_path, cfg)
            all_results.append(result)

        # Output results
        if output == "json":
            # Combine results if multiple services
            combined = combine_results(all_results)
            output_dir = Path(cfg.reports.output_directory)
            json_reporter = JSONReporter(output_dir / "report.json")
            json_reporter.generate(combined)
            console.print(f"[green]Report saved to {output_dir / 'report.json'}[/green]")
        else:
            # Console output
            for result in all_results:
                display_results(result, strict)

        # Exit code
        has_errors = any(not r["valid"] for r in all_results)
        has_warnings = any(r.get("warnings") for r in all_results)

        if has_errors or (strict and has_warnings):
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    type=click.Choice(["console", "json"]),
    default="console",
    help="Output format",
)
@click.option(
    "--config",
    default=".golden-thread.config.yaml",
    help="Config file path",
)
@click.option("--service", help="Service path to check for orphans")
def orphans(output: str, config: str, service: Optional[str]):
    """Detect orphaned code and manifest entries."""
    try:
        # Load configuration
        cfg = Config.load(config)

        # Determine service path
        if service:
            service_path = Path(service)
        else:
            # Use current directory
            service_path = Path.cwd()

        # Load manifest
        manifest_file = service_path / cfg.services.manifest_filename
        if not manifest_file.exists():
            console.print(f"[red]No manifest found at {manifest_file}[/red]")
            sys.exit(1)

        manifest = Manifest.load(str(manifest_file))

        # Parse codebase
        console.print("[yellow]Parsing codebase...[/yellow]")
        all_symbols = parse_codebase(service_path, cfg)

        # Detect orphans
        orphan_validator = OrphanValidator(manifest, all_symbols)
        orphan_result = orphan_validator.detect_orphans()

        # Output
        if output == "json":
            output_dir = Path(cfg.reports.output_directory)
            output_file = output_dir / "orphans.json"
            output_dir.mkdir(parents=True, exist_ok=True)

            import json

            with open(output_file, "w") as f:
                json.dump(
                    {
                        "orphan_code": orphan_result.orphan_code,
                        "orphan_manifest": orphan_result.orphan_manifest,
                        "suggestions": orphan_result.suggestions,
                    },
                    f,
                    indent=2,
                )
            console.print(f"[green]Report saved to {output_file}[/green]")
        else:
            display_orphans(orphan_result)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def discover_services(cfg: Config) -> List[Path]:
    """Discover services with manifests."""
    services = []
    manifest_filename = cfg.services.manifest_filename

    for root_dir in cfg.services.root_directories:
        root_path = Path(root_dir)
        if not root_path.exists():
            continue

        # Find all manifest files
        for manifest_file in root_path.rglob(manifest_filename):
            services.append(manifest_file.parent)

    return services


def validate_service(service_path: Path, cfg: Config) -> dict:
    """Validate a single service."""
    console.print(f"[cyan]Validating {service_path}...[/cyan]")

    # Load manifest
    manifest_file = service_path / cfg.services.manifest_filename
    manifest = Manifest.load(str(manifest_file))

    # Parse codebase
    all_symbols = parse_codebase(service_path, cfg)

    # Initialize Notion client
    notion_client = NotionClient(cfg.notion)
    registry = NotionRegistry(notion_client, cfg.notion.databases)

    # Run validators
    coverage_validator = CoverageValidator(manifest, all_symbols)
    coverage_result = coverage_validator.validate()

    consistency_validator = ConsistencyValidator(manifest, registry)
    consistency_result = consistency_validator.validate()

    # Combine results
    all_errors = coverage_result.errors + consistency_result.errors
    all_warnings = consistency_result.warnings

    return {
        "service": manifest.service,
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "coverage_percentage": coverage_result.coverage_percentage,
        "total_symbols": coverage_result.total_symbols,
        "mapped_symbols": coverage_result.mapped_symbols,
        "orphan_symbols": coverage_result.orphan_symbols,
        "invalid_mappings": coverage_result.invalid_mappings,
    }


def parse_codebase(service_path: Path, cfg: Config) -> list:
    """Parse codebase with all enabled parsers."""
    all_symbols = []

    # Python parser
    if cfg.parsers.python.enabled:
        python_parser = PythonParser(str(service_path), cfg.validation.__dict__)
        all_symbols.extend(python_parser.parse())

    # TypeScript parser
    if cfg.parsers.typescript.enabled:
        ts_parser = TypeScriptParser(str(service_path), cfg.validation.__dict__)
        all_symbols.extend(ts_parser.parse())

    # Go parser
    if cfg.parsers.go.enabled:
        go_parser = GoParser(str(service_path), cfg.validation.__dict__)
        all_symbols.extend(go_parser.parse())

    return all_symbols


def display_results(result: dict, strict: bool):
    """Display validation results to console."""
    service = result["service"]
    valid = result["valid"]
    errors = result["errors"]
    warnings = result["warnings"]
    coverage = result["coverage_percentage"]

    # Header
    if valid and (not strict or not warnings):
        console.print(f"\n[green]✓ {service}: PASS[/green]")
    else:
        console.print(f"\n[red]✗ {service}: FAIL[/red]")

    # Coverage
    console.print(f"Coverage: {coverage:.1f}%")

    # Errors
    if errors:
        console.print(f"\n[red]Errors ({len(errors)}):[/red]")
        for error in errors[:10]:  # Limit display
            console.print(f"  • {error['code']}: {error['message']}")

        if len(errors) > 10:
            console.print(f"  ... and {len(errors) - 10} more errors")

    # Warnings
    if warnings:
        console.print(f"\n[yellow]Warnings ({len(warnings)}):[/yellow]")
        for warning in warnings[:10]:  # Limit display
            console.print(f"  • {warning['code']}: {warning['message']}")

        if len(warnings) > 10:
            console.print(f"  ... and {len(warnings) - 10} more warnings")


def display_orphans(orphan_result):
    """Display orphan detection results."""
    console.print("\n[cyan]Orphan Detection Results[/cyan]")

    # Orphaned code
    if orphan_result.orphan_code:
        console.print(f"\n[red]Orphaned Code ({len(orphan_result.orphan_code)}):[/red]")
        console.print("Code symbols without manifest entries:\n")

        for orphan in orphan_result.orphan_code[:10]:
            console.print(f"  • {orphan['path']} ({orphan['type']}) at {orphan['file']}:{orphan['line']}")

        if len(orphan_result.orphan_code) > 10:
            console.print(f"  ... and {len(orphan_result.orphan_code) - 10} more")

    # Orphaned manifest
    if orphan_result.orphan_manifest:
        console.print(f"\n[yellow]Orphaned Manifest ({len(orphan_result.orphan_manifest)}):[/yellow]")
        console.print("Manifest entries without matching code:\n")

        for orphan in orphan_result.orphan_manifest[:10]:
            console.print(f"  • {orphan['path']}")

        if len(orphan_result.orphan_manifest) > 10:
            console.print(f"  ... and {len(orphan_result.orphan_manifest) - 10} more")

    # Suggestions
    if orphan_result.suggestions:
        console.print("\n[cyan]Suggestions:[/cyan]")
        for suggestion in orphan_result.suggestions[:5]:
            console.print(f"\n{suggestion['orphan']}:")
            console.print(f"{suggestion['suggestion']}")


def combine_results(results: List[dict]) -> dict:
    """Combine multiple service results."""
    combined = {
        "service": "all",
        "valid": all(r["valid"] for r in results),
        "errors": [],
        "warnings": [],
        "coverage_percentage": 0.0,
        "total_symbols": 0,
        "mapped_symbols": 0,
        "orphan_symbols": [],
        "invalid_mappings": [],
    }

    for result in results:
        combined["errors"].extend(result["errors"])
        combined["warnings"].extend(result["warnings"])
        combined["total_symbols"] += result["total_symbols"]
        combined["mapped_symbols"] += result["mapped_symbols"]
        combined["orphan_symbols"].extend(result["orphan_symbols"])
        combined["invalid_mappings"].extend(result["invalid_mappings"])

    # Calculate overall coverage
    if combined["total_symbols"] > 0:
        combined["coverage_percentage"] = (
            combined["mapped_symbols"] / combined["total_symbols"] * 100
        )

    return combined


if __name__ == "__main__":
    cli()
