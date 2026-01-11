"""
Golden Thread Framework - End-to-end traceability validation.

This package validates that code implementations are traceable to business
requirements through a chain of Notion registries.
"""

__version__ = "0.1.0"

# Exception hierarchy
class GoldenThreadError(Exception):
    """Base exception for all Golden Thread Framework errors."""
    pass


class ManifestError(GoldenThreadError):
    """Raised when manifest parsing or validation fails."""
    pass


class ParserError(GoldenThreadError):
    """Raised when code parsing fails."""
    pass


class NotionError(GoldenThreadError):
    """Raised when Notion API operations fail."""
    pass


class ValidationError(GoldenThreadError):
    """Raised when traceability validation fails."""
    pass


class ConfigError(GoldenThreadError):
    """Raised when configuration is invalid."""
    pass


# ID Pattern constants (regex patterns for validation)
ID_PATTERNS = {
    'BR': r'^BR-[A-Z]+-\d{3}$',
    'UR': r'^UR-[A-Z]+-\d{3}$',
    'FEAT': r'^FEAT-[A-Z]+-\d{3}$',
    'CF': r'^CF-[A-Z]+-\d{3}$',
    'FR': r'^FR-[A-Z]+-\d{3}$',
    'NFR': r'^NFR-[A-Z]+-\d{3}$',
    'TSR': r'^TSR-[A-Z]+-\d{3}$',
    'TCR': r'^TCR-[A-Z]+-\d{3}$',
    'V': r'^V-[A-Z]+-\d{3}$',
    'TC': r'^TC-[A-Z]+-\d{3}$',
    'EA': r'^EA-[A-Z]+-\d{3}$',
    'IF': r'^IF-[A-Z]+-\d{3}$',
    'EVT': r'^EVT-[A-Z]+-\d{3}$',
    'GQL': r'^GQL-[A-Z]+-\d{3}$',
    'RPC': r'^RPC-[A-Z]+-\d{3}$',
}

# Validation error codes
ERROR_CODES = [
    'MISSING_BR',
    'MISSING_UR',
    'MISSING_FR',
    'MISSING_CF',
    'MISSING_V',
    'MISSING_TC',
    'MISSING_EA',
    'ORPHAN_CODE',
    'ORPHAN_MANIFEST',
    'INVALID_ID',
    'INVALID_FORMAT',
]

# Registry type mapping
REGISTRY_TYPES = [
    'BR',   # Business Requirement
    'UR',   # User Requirement
    'FEAT', # Feature Registry
    'CF',   # Call Flow Registry
    'FR',   # Functional Requirement
    'NFR',  # Non-Functional Requirement
    'TSR',  # Technical & System Requirement
    'TCR',  # Transitional & Compliance Requirement
    'V',    # Verification Matrix
    'TC',   # Test Case Registry
    'EA',   # Evidence Artifacts
    'IF',   # Interface Registry
    'EVT',  # Events Registry
    'GQL',  # GraphQL Operations
    'RPC',  # gRPC Methods
]

__all__ = [
    '__version__',
    'GoldenThreadError',
    'ManifestError',
    'ParserError',
    'NotionError',
    'ValidationError',
    'ConfigError',
    'ID_PATTERNS',
    'ERROR_CODES',
    'REGISTRY_TYPES',
]
