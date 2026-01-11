# golden-thread-framework


┌─────────────────────────────────────────────────────────────────┐
│              golden-thread (Python Package)                      │
│            pip install golden-thread-framework                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐               │
│  │ Go Parser │    │ Py Parser │    │ TS Parser │               │
│  │(tree-sitter)   │   (AST)   │    │(tree-sitter)              │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘               │
│        └────────────────┼────────────────┘                      │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           Traceability Manifest Engine                   │    │
│  │  - Loads .golden-thread.yaml per service                │    │
│  │  - Maps code symbols to BR/UR/FEAT/FR/TC/V/EA          │    │
│  │  - Validates coverage against AST                       │    │
│  │  - Queries Notion registries via API                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                         │                                        │
│        ┌────────────────┼────────────────┐                      │
│        ▼                ▼                ▼                      │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐                 │
│  │ CI Validate│   │  CLI Tool │   │Report Gen │                 │
│  │(pre-commit)│   │(golden-thread)│ (HTML/JSON)│                 │
│  └───────────┘   └───────────┘   └───────────┘                 │
└─────────────────────────────────────────────────────────────────┘


# Package Structure
golden-thread-framework/
├── pyproject.toml
├── [README.md](http://README.md)
├── src/
│   └── golden_thread/
│       ├── __init__.py
│       ├── [cli.py](http://cli.py)                    # CLI entrypoint
│       ├── [config.py](http://config.py)                 # Configuration loading
│       ├── [manifest.py](http://manifest.py)               # YAML manifest parser
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── [base.py](http://base.py)               # Base parser interface
│       │   ├── go_[parser.py](http://parser.py)          # tree-sitter Go AST
│       │   ├── python_[parser.py](http://parser.py)      # Python AST module
│       │   └── typescript_[parser.py](http://parser.py)  # tree-sitter TS AST
│       ├── notion/
│       │   ├── __init__.py
│       │   ├── [client.py](http://client.py)             # Notion API client
│       │   └── [registry.py](http://registry.py)           # Registry query helpers
│       ├── validators/
│       │   ├── __init__.py
│       │   ├── [coverage.py](http://coverage.py)           # Traceability coverage
│       │   ├── [orphans.py](http://orphans.py)            # Orphan detection
│       │   └── [consistency.py](http://consistency.py)        # ID consistency checks
│       └── reports/
│           ├── __init__.py
│           ├── [html.py](http://html.py)               # HTML report generator
│           ├── [json.py](http://json.py)               # JSON export
│           └── pr_[template.py](http://template.py)        # PR description generator
└── tests/
    ├── test_[manifest.py](http://manifest.py)
    ├── test_[parsers.py](http://parsers.py)
    └── test_[validators.py](http://validators.py)


## Golden Thread Traceability Model

```
BR (Business Requirement)
 ↓
UR (User Requirement)
 ↓
FEAT (Feature)
 ↓
CF (Call Flow)
 ↓
FR / NFR / TSR / TCR (Functional / Non-Functional / Technical Requirements)
 ↓
V (Verification)
 ↓
TC (Test Case)
 ↓
EA (Evidence Artifact)
```

**Rule:** No V-ID can be marked "Verified" without at least one EA-ID

## Claude Code Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE CODE: "Implement FEAT-CV-001"                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. QUERY NOTION: Load FEAT-CV-001 from Feature Registry        │
│     → Extract BR-IDs, UR-IDs, FR-IDs, CF-IDs, NFR-IDs           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. UNDERSTAND THE WHY:                                         │
│     BR-CV-001 → "Why does the business need this?"              │
│     UR-CV-001 → "What user problem does this solve?"            │
│     FR-CV-001 → "What must the system do?"                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. IMPLEMENT WITH CLEAN CODE:                                  │
│     → Write focused, well-structured code                       │
│     → No annotation pollution                                   │
│     → Update .golden-thread.yaml with symbol mappings           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. VALIDATE BEFORE PR:                                         │
│     → Run: golden-thread validate --strict                      │
│     → Run: golden-thread orphans                                │
│     → Generate: golden-thread pr-template --feat FEAT-CV-001    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Intentionality Checklist

Before writing code, Claude Code must be able to answer:

- [ ]  **BR-ID** — Why does the business care about this?
- [ ]  **UR-ID** — What user problem am I solving?
- [ ]  **FR-ID / NFR-ID / TSR-ID / TCR-ID** — What are the requirements?
- [ ]  **CF-ID** — What is the call flow sequence?
- [ ]  **V-ID** — How will this be verified?
- [ ]  **TC-ID** — What tests must pass?
- [ ]  **EA-ID** — What evidence will be produced?

If any cannot be answered, query Notion registries first.

## Registry Database Mapping

<aside>
📊

Each registry below maps to a Notion database that `golden-thread` queries via API.

BR➡️UR➡️FEAT➡️CallFlows➡️FR➡️NFR/TSR/TCR➡️Verifications➡️TestCases➡️EvidenceArtifacts


</aside>

### Core Traceability Registries

| Registry | Primary Key |
| --- | --- |
| Business Requirement | BR-ID |
| User Requirement | UR-ID |
| Feature Registry | FEAT-ID |
| Call Flow Registry | CF-ID |
| Functional Requirement | FR-ID |
| Non-Functional Requirement | NFR-ID |
| Technical & System Requirement | TSR-ID |
| Transitional & Compliance Requirement | TCR-ID |
| Verification Matrix | V-ID |
| Test Case Registry | TC-ID |
| Evidence Artifacts | EA-ID |

### Service & Interface Registries

| Registry | Primary Key |
| --- | --- |
| Services Matrix | Service Name |
| Interface Registry | IF-ID |
| Events Registry | EVT-ID |
| GraphQL Operations | GQL-ID |
| gRPC Methods | RPC-ID |
---

## Validation Error Codes

| Code | Meaning | Resolution |
| --- | --- | --- |
| MISSING_BR | Feature has no Business Requirement | Add BR-ID to Feature Registry |
| MISSING_UR | Feature has no User Requirement | Add UR-ID to Feature Registry |
| MISSING_FR | Feature has no Functional Requirement | Create FR and link to FEAT |
| MISSING_CF | Feature has no Call Flow | Create CF-ID in Call Flow Registry |
| MISSING_V | Requirement has no Verification | Create V-ID in Verification Matrix |
| MISSING_TC | Verification has no Test Case | Create TC-ID in Test Case Registry |
| MISSING_EA | Verified V-ID has no Evidence | Create EA-ID in Evidence Registry |
| ORPHAN_CODE | Code symbol not in manifest | Add mapping to .golden-thread.yaml |
| ORPHAN_MANIFEST | Manifest entry has no code match | Remove or fix symbol path |
| INVALID_ID | ID not found in Notion registry | Create entry in Notion or fix typo |

## CLI Commands

# Core commands for v1
golden-thread validate --service <name>   # Validate single service
golden-thread validate --all              # Validate entire monorepo
golden-thread orphans                     # Detect unmapped code/manifest entries
```
Plus:

- JSON output for CI parsing (`--output json`)
- Basic console summary with pass/fail counts
- Exit codes for CI (0 = pass, 1 = fail)

## Next Steps

1. **Create repo:** `golden-thread-framework` in separate repository
2. **Implement parsers:** Go, Python, TypeScript via tree-sitter
3. **Build Notion client:** Query registries, cache responses
-- I added the credentials to access my documentation datatables in notion with notion api as an MCP server in claude code mcp servers for you to reference (note its a rest api not mcp). 
    https://api.notion.com/v1/
    (See token in your MCP Servers config titled "notion")
4. **Add validators:** Coverage, orphans, consistency
5. **Publish package:** PyPI for easy installation
6. **Integrate CI:** GitHub Actions workflow in monorepo