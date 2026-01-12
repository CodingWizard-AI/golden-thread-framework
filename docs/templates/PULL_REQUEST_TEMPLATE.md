## Description
<!-- Brief summary of changes -->


## 🧵 Traceability (Required)

**Feature**: <!-- FEAT-XXX-NNN -->
**Functional Requirements**: <!-- FR-XXX-NNN, FR-XXX-NNN -->
**Technical Requirements**: <!-- TSR-XXX-NNN (if applicable) -->
**User Requirements**: <!-- UR-XXX-NNN -->
**Business Requirements**: <!-- BR-XXX-NNN (if known) -->

**Interfaces** (if applicable):
- Interface: <!-- IF-XXX-NNN -->
- REST Endpoints: <!-- REST-XXX-NNN -->
- GraphQL Operations: <!-- GQL-XXX-NNN -->
- gRPC Methods: <!-- RPC-XXX-NNN -->
- Events: <!-- EVT-XXX-NNN -->

**Notion Links**:
- Feature: [FEAT-XXX-NNN](https://notion.so/link-to-feature)
- Functional Req: [FR-XXX-NNN](https://notion.so/link-to-fr)

### Acceptance Criteria
<!-- Copy from Functional Requirement in Notion -->

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## 🧪 Testing

**Test Coverage**:
- [ ] Unit tests added/updated: `TC-UNIT-XXX`
- [ ] Integration tests added/updated: `TC-INT-XXX`
- [ ] E2E tests added/updated: `TC-E2E-XXX`
- [ ] Evidence artifacts collected: `EA-XXX-NNN`

**Test Commands**:
```bash
# How to run tests locally
make test-unit
make test-integration
```

**Test Results**:
- [ ] All tests passing locally
- [ ] All tests passing in CI

## 📝 Changes

### Files Changed
<!-- List significant files and why they changed -->

- `path/to/file1.go` - 
- `path/to/file2.tsx` - 

### Database Migrations
<!-- If applicable -->

- [ ] No database changes
- [ ] Migration added: `databases/xxx/migrations/NNNNNN_description.up.sql`
- [ ] Migration tested locally
- [ ] Rollback migration tested: `NNNNNN_description.down.sql`

### API Changes
<!-- If applicable -->

- [ ] No API changes
- [ ] GraphQL schema updated (GQL-XXX-NNN)
- [ ] Protocol buffers updated (RPC-XXX-NNN) - regenerate with `make proto-gen`
- [ ] REST endpoints added/modified (REST-XXX-NNN)
- [ ] Events added/modified (EVT-XXX-NNN)
- [ ] Interface registry updated (IF-XXX-NNN)
- [ ] API documentation updated

## 🚀 Deployment

**Deployment Notes**:
<!-- Any special considerations for deployment -->

- [ ] No special deployment steps
- [ ] Requires environment variables: <!-- List them -->
- [ ] Requires database migration
- [ ] Requires service restart
- [ ] Breaking changes (requires coordination)

**Rollback Plan**:
<!-- How to rollback if issues occur -->


## ✅ Checklist

### Code Quality
- [ ] Code follows project style guide
- [ ] No linting errors
- [ ] No compiler warnings
- [ ] Code reviewed by myself first
- [ ] Complex logic has comments
- [ ] No debug code or console.logs

### Traceability
- [ ] All commits reference FR/IF/TSR IDs
- [ ] Requirements status updated in Notion
- [ ] Feature progress updated in Notion
- [ ] Test cases created/updated in Notion (TC-XXX-NNN)
- [ ] Evidence artifacts documented (EA-XXX-NNN)
- [ ] Interface registry updated (if applicable)

### Documentation
- [ ] Code is self-documenting
- [ ] Complex algorithms explained in comments
- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] Architecture docs updated (if needed)

### Testing
- [ ] New code has unit tests
- [ ] Integration points tested
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] All tests pass

### Security
- [ ] No secrets in code
- [ ] Input validation added
- [ ] Authentication/authorization considered
- [ ] Dependencies reviewed for vulnerabilities
- [ ] SQL injection prevention (if applicable)
- [ ] XSS prevention (if applicable)

## 📸 Screenshots
<!-- For UI changes, add before/after screenshots -->


## 🔗 Related PRs
<!-- Link to related/dependent PRs -->


## ⚠️ Breaking Changes
<!-- Describe any breaking changes and migration steps -->


## 📚 Additional Context
<!-- Add any other context about the PR here -->


---

## For Reviewers

### What to Check
1. **Traceability**: Verify links to Notion are valid and complete
2. **Acceptance Criteria**: Ensure all criteria from UR are met
3. **Tests**: Check test coverage is adequate
4. **Code Quality**: Review for readability and maintainability
5. **Architecture**: Ensure changes align with service boundaries

### Review Checklist
- [ ] Traceability links verified in Notion
- [ ] Code changes align with task description
- [ ] Tests are comprehensive
- [ ] No obvious bugs or security issues
- [ ] Documentation is clear
- [ ] Deployment plan is sound

### Questions for Author
<!-- Reviewers: Add your questions here -->


---

**Reminder**: Update Notion task status to "In Review" when PR is ready!
