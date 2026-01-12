# Golden Thread Framework - Quick Reference

## TL;DR

**Every feature must trace from Business Requirement → User Requirement → Feature → Requirements (FR/TSR/NFR) → Interfaces → Test Cases → Evidence**

Before writing code, create the trace in Notion. Reference IDs in commits and PRs.

---

## ID Naming Convention

| Registry | Format | Example | Purpose |
|----------|--------|---------|---------|
| Business Requirement | `BR-XXX-NNN` | `BR-MON-001` | Business justification |
| User Requirement | `UR-XXX-NNN` | `UR-MON-001` | User needs |
| Feature | `FEAT-XXX-NNN` | `FEAT-ONBOARD-001` | Features to implement |
| Functional Requirement | `FR-XXX-NNN` | `FR-AUTH-001` | Functional specifications |
| Non-Functional Requirement | `NFR-XXX-NNN` | `NFR-PERF-001` | Performance, security |
| Technical & System Requirement | `TSR-XXX-NNN` | `TSR-DB-001` | Technical specifications |
| Call Flow | `CF-XXX-NNN` | `CF-LOGIN-001` | Interaction sequences |
| Interface | `IF-XXX-NNN` | `IF-API-001` | API interfaces |
| REST Endpoint | `REST-XXX-NNN` | `REST-AUTH-001` | REST API endpoints |
| GraphQL Operation | `GQL-XXX-NNN` | `GQL-USER-001` | GraphQL queries/mutations |
| gRPC Method | `RPC-XXX-NNN` | `RPC-ACCT-001` | gRPC service methods |
| Event | `EVT-XXX-NNN` | `EVT-USER-001` | Event definitions |
| Test Case | `TC-XXX-NNN` | `TC-E2E-001` | Test cases |
| Evidence Artifact | `EA-XXX-NNN` | `EA-TEST-001` | Test evidence |
| Verification Method | `V-XXX-NNN` | `V-AUTH-001` | Verification methods |
| Service | `Service-Name` | `account-service` | Service catalog |
| Transitional & Compliance | `TCR-XXX-NNN` | `TCR-GDPR-001` | Compliance needs |

---

## 5-Minute Quick Start

1. **Duplicate Template**: [CodingWizard.AI Template](https://codingwizard-ai.notion.site/)
2. **Create BR**: What business value? (Use Notion AI to expand)
3. **Create UR**: What must users do? (Use Notion AI for user stories)
4. **Create FEAT**: What will we build? (Link to UR)
5. **Create FR/TSR**: Define functional and technical requirements (Link to FEAT)
6. **Create IF/REST/GQL/RPC**: Define interfaces (Link to requirements)
7. **Start coding**: Reference IDs in commits

---

## Essential Notion AI Prompts

```
# Expand business requirement
"Expand this into a business requirement with description, priority, stakeholders, and success metrics"

# Generate user stories
"Generate 5 user stories for this business requirement"

# Feature breakdown
"Break this into features with components and dependencies"

# Functional requirements
"Generate functional requirements from this feature with acceptance criteria"

# Technical requirements
"Generate technical and system requirements for this feature including infrastructure, security, and performance needs"

# Interface design
"Generate interface specifications for this feature including REST endpoints, GraphQL operations, or gRPC methods as needed"

# Call flow documentation
"Create a call flow diagram description for this user interaction"

# Test case generation
"Generate test cases covering these acceptance criteria with steps and expected results"
```

---

## Git Commit Template

```bash
git commit -m "FR-AUTH-001, IF-API-001: Add session validation middleware

Implements session cookie validation for GraphQL Gateway.
Relates to UR-MON-002 (user login) and FEAT-ONBOARD-001.
Tests: TC-INT-003, TC-E2E-002"
```

---

## Pull Request Checklist

```markdown
## Traceability
- [ ] Linked to Feature: FEAT-XXX-NNN
- [ ] Functional Requirements: FR-XXX-NNN
- [ ] Technical Requirements: TSR-XXX-NNN
- [ ] User Requirements addressed: UR-XXX-NNN
- [ ] Interfaces defined: IF/REST/GQL/RPC-XXX-NNN
- [ ] Tests created/updated: TC-XXX-NNN
- [ ] All Notion statuses updated

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Acceptance criteria met
```

---

## Required Relations in Notion

| Record Type | Must Link To |
|-------------|--------------|
| UR | BR (business requirement) |
| FEAT | UR (user requirement) |
| FR | FEAT (feature) |
| TSR | FEAT (feature) |
| NFR | FEAT (feature) |
| CF | UR (user requirement) or FEAT |
| IF | FR or TSR (requirements) |
| REST/GQL/RPC | IF (interface) |
| EVT | FEAT (feature) |
| TC | UR (user requirement) or FR |
| EA | TC (test case) |
| V | FR, TSR, or NFR |

---

## Common Queries

**"What business value does this code provide?"**
```
Code File → IF/REST/GQL/RPC → FR/TSR → FEAT → UR → BR
```

**"Is this requirement complete?"**
```
Check UR → All linked FRs defined
           All linked IFs implemented
           All linked TCs = Passing
           Evidence artifacts collected
```

**"What's impacted by changing this requirement?"**
```
UR → Find all linked FEATs
   → Find all linked FRs/TSRs
   → Find all linked IFs
   → Find affected REST/GQL/RPC endpoints
   → Find affected TCs
```

**"What interfaces does this feature expose?"**
```
FEAT → Linked IFs → REST/GQL/RPC endpoints
```

---

## Red Flags 🚩

- ❌ Feature with no User Requirement link
- ❌ Functional Requirement with no Feature link
- ❌ Interface with no Functional/Technical Requirement link
- ❌ Code commit without FR/IF reference
- ❌ User Requirement with no test cases
- ❌ Test Case without Evidence Artifact
- ❌ Interface without REST/GQL/RPC implementation

---

## Daily Developer Workflow

### Morning
1. Check Notion for assigned features/requirements
2. Verify requirements link to features
3. Read acceptance criteria from URs and FRs

### During Work
1. Reference FR/IF IDs in commits
2. Update implementation progress in Notion
3. Add technical notes to TSRs

### Before PR
1. Update all related requirement statuses
2. Link PR to FRs and IFs
3. Verify tests are passing
4. Update test case status in Notion

### After Merge
1. Mark requirements as "Implemented"
2. Update feature progress
3. Add evidence artifacts for completed tests

---

## Team Responsibilities

| Role | Primary Responsibility |
|------|------------------------|
| Product Manager | Create/maintain BRs and URs |
| Architect | Create/review Technical Requirements and FEATs |
| Developer | Complete TASKs, update status |
| QA Engineer | Create/update TESTs |
| DevOps | Manage DEPLOY records |

---

## Metrics to Track

- **Traceability Coverage**: FRs/TSRs linked to features (target: 100%)
- **Interface Coverage**: All FRs have corresponding IFs (target: 100%)
- **Test Coverage**: URs/FRs with passing TCs (target: 100%)
- **Evidence Collection**: TCs with EAs (target: 100%)
- **Completion Rate**: Verified URs / Total URs (target: track trend)

---

## Help & Resources

- **Full Guide**: [/docs/guides/golden-thread-framework.md](/docs/guides/golden-thread-framework.md)
- **Notion Template**: https://codingwizard-ai.notion.site/
- **Team Wiki**: https://wiki.yourcompany.com/golden-thread
- **Slack Channel**: #golden-thread

---

## Emergency: "I'm Stuck"

**Problem**: Don't know where to start  
**Solution**: Start with Business Requirement (BR). Ask: "What business problem am I solving?"

**Problem**: Can't find related records  
**Solution**: Use Notion search with keywords from your task. Check related views.

**Problem**: Too much overhead  
**Solution**: This saves time long-term. Start small: just link tasks to features.

**Problem**: Team isn't following it  
**Solution**: Enforce in PR reviews. Show value with impact analysis examples.

---

**Keep This Visible**: Bookmark this page or pin in Slack for quick reference!
