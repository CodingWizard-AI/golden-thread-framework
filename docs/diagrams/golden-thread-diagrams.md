# Golden Thread Traceability - Visual Diagrams

## Complete Traceability Flow

```mermaid
graph TD
    A[Business Requirement<br/>BR-MON-001] -->|derives| B[User Requirement<br/>UR-MON-001]
    A -->|derives| C[User Requirement<br/>UR-MON-002]
    
    B -->|implements| D[Feature<br/>FEAT-ONBOARD-001]
    C -->|implements| D
    
    D -->|defines| E[Functional Requirement<br/>FR-AUTH-001]
    D -->|defines| F[Technical Requirement<br/>TSR-DB-001]
    D -->|defines| G[Non-Functional Req<br/>NFR-PERF-001]
    
    E -->|exposes via| H[Interface<br/>IF-API-001]
    F -->|implements via| H
    
    H -->|defines| I[GraphQL Operation<br/>GQL-MUT-001]
    H -->|defines| J[gRPC Method<br/>RPC-ACCT-001]
    H -->|defines| K[REST Endpoint<br/>REST-AUTH-001]
    
    I -->|implements| L[Code Files]
    J -->|implements| L
    K -->|implements| L
    
    B -->|validated by| M[Test Case<br/>TC-E2E-001]
    E -->|validated by| N[Test Case<br/>TC-INT-001]
    
    M -->|produces| O[Evidence Artifact<br/>EA-TEST-001]
    N -->|produces| O
    
    E -->|verified by| P[Verification<br/>V-AUTH-001]
    G -->|verified by| Q[Verification<br/>V-PERF-001]
    
    style A fill:#e1f5ff
    style B fill:#fff3cd
    style C fill:#fff3cd
    style D fill:#d4edda
    style E fill:#e7f3ff
    style F fill:#e7f3ff
    style G fill:#ffe7e7
    style H fill:#f0e7ff
    style I fill:#e2e3e5
    style J fill:#e2e3e5
    style K fill:#e2e3e5
    style L fill:#d1ecf1
    style M fill:#fff3cd
    style N fill:#fff3cd
    style O fill:#d4edda
    style P fill:#ffeaa7
    style Q fill:#ffeaa7
```

## Database Relations

```mermaid
erDiagram
    BUSINESS_REQUIREMENT ||--o{ USER_REQUIREMENT : "derives"
    USER_REQUIREMENT ||--o{ FEATURE : "implements"
    FEATURE ||--o{ FUNCTIONAL_REQUIREMENT : "defines"
    FEATURE ||--o{ TECHNICAL_REQUIREMENT : "defines"
    FEATURE ||--o{ NON_FUNCTIONAL_REQUIREMENT : "defines"
    FUNCTIONAL_REQUIREMENT ||--o{ INTERFACE : "exposes-via"
    TECHNICAL_REQUIREMENT ||--o{ INTERFACE : "implements-via"
    INTERFACE ||--o{ REST_ENDPOINT : "defines"
    INTERFACE ||--o{ GRAPHQL_OPERATION : "defines"
    INTERFACE ||--o{ GRPC_METHOD : "defines"
    FEATURE ||--o{ EVENT : "emits"
    USER_REQUIREMENT ||--o{ CALL_FLOW : "documented-by"
    USER_REQUIREMENT ||--o{ TEST_CASE : "validated-by"
    FUNCTIONAL_REQUIREMENT ||--o{ TEST_CASE : "validated-by"
    TEST_CASE ||--o{ EVIDENCE_ARTIFACT : "produces"
    FUNCTIONAL_REQUIREMENT ||--o{ VERIFICATION : "verified-by"
    NON_FUNCTIONAL_REQUIREMENT ||--o{ VERIFICATION : "verified-by"
    FEATURE ||--o{ SERVICE : "implemented-by"
    FEATURE ||--o{ TRANSITIONAL_COMPLIANCE : "must-comply"
    
    BUSINESS_REQUIREMENT {
        string br_id PK
        string title
        string description
        string priority
        string stakeholder
        string success_metrics
    }
    
    USER_REQUIREMENT {
        string ur_id PK
        string br_id FK
        string title
        string user_story
        string acceptance_criteria
    }
    
    FEATURE {
        string feat_id PK
        string ur_id FK
        string title
        string description
        string components
        string status
    }
    
    FUNCTIONAL_REQUIREMENT {
        string fr_id PK
        string feat_id FK
        string title
        string description
        string acceptance_criteria
        string priority
    }
    
    TECHNICAL_REQUIREMENT {
        string tsr_id PK
        string feat_id FK
        string title
        string description
        string rationale
    }
    
    NON_FUNCTIONAL_REQUIREMENT {
        string nfr_id PK
        string feat_id FK
        string type
        string title
        string description
        string measurement
    }
    
    INTERFACE {
        string if_id PK
        string fr_id FK
        string title
        string type
        string description
    }
    
    REST_ENDPOINT {
        string rest_id PK
        string if_id FK
        string method
        string path
        string request_schema
        string response_schema
    }
    
    GRAPHQL_OPERATION {
        string gql_id PK
        string if_id FK
        string operation_type
        string name
        string schema
    }
    
    GRPC_METHOD {
        string rpc_id PK
        string if_id FK
        string service_name
        string method_name
        string request_message
        string response_message
    }
    
    EVENT {
        string evt_id PK
        string feat_id FK
        string event_name
        string payload_schema
        string producer
        string consumers
    }
    
    CALL_FLOW {
        string cf_id PK
        string ur_id FK
        string title
        string actors
        string steps
    }
    
    TEST_CASE {
        string tc_id PK
        string ur_id FK
        string fr_id FK
        string title
        string type
        string test_steps
        string expected_result
        string status
    }
    
    EVIDENCE_ARTIFACT {
        string ea_id PK
        string tc_id FK
        string title
        string type
        string artifacts
        date date
    }
    
    VERIFICATION {
        string v_id PK
        string fr_id FK
        string nfr_id FK
        string method
        string criteria
        string status
    }
    
    SERVICE {
        string service_name PK
        string feat_id FK
        string type
        string technology
        string repository
    }
    
    TRANSITIONAL_COMPLIANCE {
        string tcr_id PK
        string feat_id FK
        string type
        string title
        string regulation
    }
```

## Developer Workflow

```mermaid
sequenceDiagram
    actor PM as Product Manager
    actor Dev as Developer
    actor QA as QA Engineer
    participant Notion
    participant Git
    participant CI/CD
    
    PM->>Notion: Create BR-MON-001
    PM->>Notion: Create UR-MON-001
    Note over PM,Notion: Use Notion AI to generate<br/>user stories
    
    Dev->>Notion: Create FEAT-ONBOARD-001
    Dev->>Notion: Link to UR-MON-001
    Dev->>Notion: Create FR-ONBOARD-001
    Dev->>Notion: Break into tasks
    
    Dev->>Notion: Update TASK status: In Progress
    Dev->>Git: Commit with TASK-ID
    Note over Dev,Git: git commit -m "FR-ONBOARD-001:<br/>Implement auth service"
    
    Git->>CI/CD: Trigger build & test
    
    QA->>Notion: Create TEST-E2E-001
    QA->>Notion: Link to UR-MON-001
    QA->>CI/CD: Run tests
    CI/CD->>Notion: Update TEST status
    
    Dev->>Notion: Update TASK status: Done
    Dev->>Notion: Update FEAT progress
    
    Dev->>Notion: Create V-PROD-001
    Dev->>Notion: Link FEAT-ONBOARD-001
    Dev->>CI/CD: Deploy to production
```

## Impact Analysis Example

```mermaid
graph LR
    A[Change Password<br/>Requirements] -->|impacts| B[UR-MON-001<br/>User Registration]
    
    B -->|traces to| C[FEAT-ONBOARD-001]
    
    C -->|affects| D[TASK-ONBOARD-001-03<br/>Account Service]
    C -->|affects| E[TASK-ONBOARD-001-05<br/>Frontend Validation]
    
    D -->|code in| F[auth_service.go]
    E -->|code in| G[RegisterForm.tsx]
    
    B -->|must update| H[TEST-E2E-001<br/>Registration Test]
    B -->|must update| I[TEST-UNIT-003<br/>Password Validation]
    
    style A fill:#ff6b6b
    style B fill:#fff3cd
    style C fill:#d4edda
    style D fill:#e2e3e5
    style E fill:#e2e3e5
    style F fill:#d1ecf1
    style G fill:#d1ecf1
    style H fill:#ffc107
    style I fill:#ffc107
```

## Traceability Query Paths

### Forward Tracing (Business → Code)

```mermaid
graph LR
    A["What code implements<br/>BR-MON-001?"] --> B[Find linked URs]
    B --> C[Find linked FEATs]
    C --> D[Find linked TASKs]
    D --> E[Get affected files<br/>from commits]
    
    style A fill:#e1f5ff
    style E fill:#d1ecf1
```

### Backward Tracing (Code → Business)

```mermaid
graph LR
    A["What business value<br/>does auth_service.go<br/>provide?"] --> B[Find TASK from<br/>commit message]
    B --> C[Find linked FEAT]
    C --> D[Find linked URs]
    D --> E[Find linked BRs]
    E --> F["Answer: Enables SaaS<br/>business model"]
    
    style A fill:#d1ecf1
    style F fill:#e1f5ff
```

### Completeness Check

```mermaid
graph TD
    A[Is UR-MON-001<br/>complete?] --> B{All Tasks Done?}
    B -->|Yes| C{All Tests Passing?}
    B -->|No| Z[Not Complete]
    
    C -->|Yes| D{Feature Deployed?}
    C -->|No| Z
    
    D -->|Yes| E[✓ Complete]
    D -->|No| Z
    
    style A fill:#fff3cd
    style E fill:#28a745,color:#fff
    style Z fill:#dc3545,color:#fff
```

## Legend

```mermaid
graph LR
    A[Business Requirements<br/>BR-XXX-NNN]
    B[User Requirements<br/>UR-XXX-NNN]
    C[Features<br/>FEAT-XXX-NNN]
    D[Functional Requirements<br/>FR-XXX-NNN]
    E[Technical Requirements<br/>TSR-XXX-NNN]
    F[Non-Functional Requirements<br/>NFR-XXX-NNN]
    G[Interfaces<br/>IF-XXX-NNN]
    H[API Endpoints<br/>REST/GQL/RPC-XXX-NNN]
    I[Test Cases<br/>TC-XXX-NNN]
    J[Evidence Artifacts<br/>EA-XXX-NNN]
    K[Verification<br/>V-XXX-NNN]
    
    style A fill:#e1f5ff
    style B fill:#fff3cd
    style C fill:#d4edda
    style D fill:#e7f3ff
    style E fill:#e7f3ff
    style F fill:#ffe7e7
    style G fill:#f0e7ff
    style H fill:#e2e3e5
    style I fill:#ffc107
    style J fill:#28a745,color:#fff
    style K fill:#ffeaa7
```

---

## How to Use These Diagrams

### In Documentation
Copy the Mermaid code blocks into any Markdown file. They render automatically in:
- GitHub
- GitLab
- Notion (with Mermaid support)
- VS Code (with Mermaid extension)
- Documentation sites (MkDocs, Docusaurus, etc.)

### In Presentations
1. Render diagram in a Mermaid viewer
2. Take screenshot
3. Add to slides

### In Notion
1. Create a code block
2. Set language to "Mermaid"
3. Paste diagram code

### Live Editing
Use online editors:
- https://mermaid.live/
- https://mermaid-js.github.io/mermaid-live-editor/

---

## Example: Real Traceability

Here's the actual traceability for FEAT-ONBOARD-001:

```mermaid
graph TD
    BR["BR-MON-001<br/>Multi-Tenant Account Management<br/><i>Enable SaaS business model</i>"] 
    
    UR1["UR-MON-001<br/>User Registration<br/><i>Create account with email/password</i>"]
    UR2["UR-MON-002<br/>User Login<br/><i>Authenticate with credentials</i>"]
    
    FEAT["FEAT-ONBOARD-001<br/>Web App Initial Load<br/>with Authentication"]
    
    FR1["FR-AUTH-001<br/>User Registration with Email Validation"]
    FR2["FR-AUTH-002<br/>User Login with Credentials"]
    
    TSR1["TSR-DB-001<br/>PostgreSQL for IAM"]
    TSR2["TSR-GRPC-001<br/>gRPC Communication"]
    
    NFR1["NFR-PERF-001<br/>Response Time < 2s"]
    NFR2["NFR-SEC-001<br/>Bcrypt Password Hashing"]
    
    IF1["IF-API-001<br/>Account Management API"]
    
    GQL1["GQL-MUT-001<br/>Register Mutation"]
    GQL2["GQL-MUT-002<br/>Login Mutation"]
    RPC1["RPC-ACCT-001<br/>Register RPC"]
    RPC2["RPC-ACCT-002<br/>Login RPC"]
    
    CF1["CF-LOGIN-001<br/>User Login Flow"]
    
    TC1["TC-E2E-001<br/>Registration E2E"]
    TC2["TC-E2E-002<br/>Login E2E"]
    TC3["TC-INT-001<br/>Service Integration"]
    TC4["TC-PERF-001<br/>Login Performance"]
    
    EA1["EA-TEST-001<br/>E2E Test Results"]
    V1["V-SEC-001<br/>Password Hash Verification"]
    V2["V-PERF-001<br/>Performance Verification"]
    
    BR -->|derives| UR1
    BR -->|derives| UR2
    
    UR1 -->|implements| FEAT
    UR2 -->|implements| FEAT
    
    FEAT -->|defines| FR1
    FEAT -->|defines| FR2
    FEAT -->|defines| TSR1
    FEAT -->|defines| TSR2
    FEAT -->|defines| NFR1
    FEAT -->|defines| NFR2
    
    FR1 -->|exposes via| IF1
    FR2 -->|exposes via| IF1
    
    IF1 -->|defines| GQL1
    IF1 -->|defines| GQL2
    IF1 -->|defines| RPC1
    IF1 -->|defines| RPC2
    
    UR2 -->|documented by| CF1
    
    UR1 -->|validated by| TC1
    UR2 -->|validated by| TC2
    FR1 -->|validated by| TC3
    NFR1 -->|validated by| TC4
    
    TC1 -->|produces| EA1
    TC2 -->|produces| EA1
    
    NFR2 -->|verified by| V1
    NFR1 -->|verified by| V2
    
    style BR fill:#e1f5ff
    style UR1 fill:#fff3cd
    style UR2 fill:#fff3cd
    style FEAT fill:#d4edda
    style FR1 fill:#e7f3ff
    style FR2 fill:#e7f3ff
    style TSR1 fill:#e7f3ff
    style TSR2 fill:#e7f3ff
    style NFR1 fill:#ffe7e7
    style NFR2 fill:#ffe7e7
    style IF1 fill:#f0e7ff
    style GQL1 fill:#e2e3e5
    style GQL2 fill:#e2e3e5
    style RPC1 fill:#e2e3e5
    style RPC2 fill:#e2e3e5
    style CF1 fill:#d4edda
    style TC1 fill:#ffc107
    style TC2 fill:#ffc107
    style TC3 fill:#ffc107
    style TC4 fill:#ffc107
    style EA1 fill:#28a745,color:#fff
    style V1 fill:#ffeaa7
    style V2 fill:#ffeaa7
```

---

**Pro Tip**: Keep these diagrams updated as your traceability model evolves. They're invaluable for onboarding and stakeholder communication!
