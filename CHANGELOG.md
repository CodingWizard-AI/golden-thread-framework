# Changelog

All notable changes to the Golden Thread Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-11

### Added

- Initial release of Golden Thread Framework
- **Core Parsers**: Python (AST), TypeScript (tree-sitter), Go (tree-sitter)
- **Notion Integration**: REST API client with caching and rate limiting
- **Validation Engine**:
  - Coverage validator for code-to-manifest traceability
  - Consistency validator for Notion ID validation
  - Orphan detector for unmapped code and manifest entries
- **CLI Commands**:
  - `golden-thread validate` - Validate single service or entire monorepo
  - `golden-thread orphans` - Detect orphaned code and manifests
- **Reporting**: JSON output for CI/CD integration
- **Configuration**: YAML-based config with environment variable substitution
- **Manifest System**: Per-service `.golden-thread.yaml` for traceability mappings

### Features

- Validates traceability chain: BR → UR → FEAT → CF → FR/NFR/TSR/TCR → V → TC → EA
- Queries 16 Notion registry databases
- File-based caching with configurable TTL
- Rate limiting (3 req/sec) with exponential backoff
- Actionable error messages with resolution suggestions
- Support for monorepo and single-service validation
- Exclusion patterns for test files and private symbols
- Coverage percentage calculation
- Fuzzy matching for orphan suggestions

### Documentation

- Comprehensive README with installation and usage guide
- Example configuration files
- CI/CD integration examples (GitHub Actions)
- Error resolution reference guide
- Implementation plan documentation

### Supported Languages

- Python (3.9+)
- TypeScript/JavaScript
- Go

### Traceability Model

Validates 16 Notion registry types:
- Business Requirements (BR)
- User Requirements (UR)
- Features (FEAT)
- Call Flows (CF)
- Functional Requirements (FR)
- Non-Functional Requirements (NFR)
- Technical & System Requirements (TSR)
- Transitional & Compliance Requirements (TCR)
- Verifications (V)
- Test Cases (TC)
- Evidence Artifacts (EA)
- Services Matrix (Service)
- Interfaces (IF)
- Events (EVT)
- GraphQL Operations (GQL)
- gRPC Methods (RPC)

### Known Limitations

- Tree-sitter parsers require language grammars to be installed
- Notion relation properties return page IDs (not actual requirement IDs)
- Large codebases may require increased cache TTL
- HTML report generation not yet implemented

## [Unreleased]

### Planned for v0.2.0

- HTML report generation with visualizations
- PR template generator from feature traceability
- Pre-commit hook support
- Watch mode for continuous validation
- Support for additional languages (Rust, Java, C#)
- Improved Notion relation property parsing
- Performance optimizations for large monorepos
- Interactive CLI mode for fixing orphans
- VS Code extension integration
