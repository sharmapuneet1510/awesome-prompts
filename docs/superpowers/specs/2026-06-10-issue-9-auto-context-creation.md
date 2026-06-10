# Issue #9: Auto Context Creation Post-Execution — Design Specification

**Date:** June 10, 2026  
**Status:** Approved Design  
**Version:** 1.0  
**Related Issue:** #9 — Autonomous developer Agent Should automatically call Context Creation Updation post Execution

---

## Executive Summary

Implement automatic context generation after `orchestrator:build` completes. Users call `orchestrator:build` once, and the system automatically:
1. Generates code, tests, docs, CI/CD, and deployment config
2. Automatically generates project context (architecture.md, tech-stack.md, design.html, context.json)
3. Commits both in separate commits (code + context) for clear review
4. Creates PR with comprehensive description linking both commits

User experience is seamless: call `orchestrator:build`, get fully documented project with context.

---

## Problem Statement

**Current State:**
- User calls `orchestrator:build` → generates code, tests, docs, CI/CD
- User must separately call `orchestrator:context` to generate architecture documentation
- Context is not automatically included in the generated project
- Two-step process is error-prone and easy to forget

**Desired State:**
- User calls `orchestrator:build` once
- System automatically generates context documentation
- PR includes both code and context artifacts
- Complete, documented project is ready for review

---

## Solution: Backend Auto-Chaining

**Approach:** Implement automatic invocation of `orchestrator:context` after `orchestrator:build` completes, transparent to the user.

**Key Decisions:**
1. ✅ Keep user API unchanged (call `orchestrator:build`, get everything)
2. ✅ Auto-chaining happens in backend (internal implementation detail)
3. ✅ Two separate commits (code + context) for review clarity
4. ✅ Both commits included in single PR
5. ✅ Backward compatible (orchestrator:build works standalone)

---

## Architecture

### Components

**1. orchestrator:build** (existing, no user-facing changes)
- Generates: code, tests, docs, CI/CD, deployment config
- Returns: `{status: "success", project_dir: "<path>", artifacts: {...}}`
- New: Emits completion signal to orchestrator system

**2. Auto-Chaining Logic** (new, internal)
- Detects `orchestrator:build` completion
- Extracts `project_dir` from build output
- Invokes `orchestrator:context(path=project_dir, depth="comprehensive")`
- Waits for context generation to complete

**3. orchestrator:context** (existing, no changes)
- Takes generated project directory
- Produces: architecture.md, tech-stack.md, design.html, context.json
- Returns: `{status: "success", artifacts: [...], output_dir: "docs/context/"}`

**4. Git Commit Handler** (new, internal)
- Commits generated code as: `"feat: auto-generated implementation"`
- Commits context artifacts as: `"docs: auto-generated project context"`
- Links commits for traceability (second commit references first)
- Handles commit failures gracefully

**5. orchestrator:pr** (existing, enhanced)
- Detects multi-commit scenario (code + context)
- Creates PR with comprehensive description
- References both commits in PR description
- Returns: `{status: "success", pr_url: "...", pr_number: ...}`

### Data Flow

```
User Input:
  orchestrator:build(requirements.md, context, tech_stack)

Build Phase:
  ├─ Architect → Design system topology, API, database schema
  ├─ Implementer → Generate code, tests, docs, CI/CD, Docker, IaC
  └─ Quality → Validate and review all artifacts
         ↓ (on success)

Auto-Chain Triggered:
  orchestrator:context(path=<generated_project>, depth=comprehensive)
         ↓

Context Phase:
  ├─ Analyze generated project structure
  ├─ Generate architecture.md (C4 diagrams, data flows, topology)
  ├─ Generate tech-stack.md (technology reference)
  ├─ Generate design.html (interactive visualization)
  └─ Generate context.json (machine-readable metadata)
         ↓ (on success)

Git Commits:
  ├─ Commit 1: "feat: auto-generated implementation"
  │   Files: src/, tests/, README.md, .github/workflows/, Dockerfile, terraform/
  │
  └─ Commit 2: "docs: auto-generated project context"
      Files: docs/context/architecture.md, docs/context/tech-stack.md, etc.
         ↓ (on success)

PR Creation:
  orchestrator:pr(commits=[commit1, commit2])
         ↓

Output:
  {
    status: "success",
    pr_url: "https://github.com/user/repo/pull/123",
    pr_number: 123,
    commits: ["abc1234", "def5678"],
    description: "Complete project with auto-generated context"
  }
```

---

## Implementation Details

### File Changes

**1. orchestrator.py** (existing agent, add auto-chaining)
```python
# After orchestrator:build completes successfully:
if build_result.status == "success":
    project_dir = build_result.project_dir
    context_result = self._auto_chain_context(project_dir)
    # Continue to git commit handler
```

**2. git_handler.py** (new, handle dual commits)
```python
def commit_with_chain(self, code_artifacts, context_artifacts, 
                      code_message, context_message):
    # Commit 1: Code artifacts
    commit1_sha = self.commit(code_artifacts, code_message)
    
    # Commit 2: Context (references Commit 1)
    extended_message = f"{context_message}\n\nAutomated context for {commit1_sha}"
    commit2_sha = self.commit(context_artifacts, extended_message)
    
    return [commit1_sha, commit2_sha]
```

**3. orchestrator_bridge.py** (existing, coordinate chaining)
```python
def invoke_build_and_context_chain(self, requirements_path, context, tech_stack):
    # Execute orchestrator:build
    build_result = self.orchestrator.build(requirements_path, context, tech_stack)
    
    if build_result.status != "success":
        return build_result
    
    # Auto-invoke orchestrator:context
    context_result = self.orchestrator.context(
        path=build_result.project_dir,
        depth="comprehensive"
    )
    
    if context_result.status != "success":
        # Handle partial failure (code generated, context failed)
        return {
            "status": "partial_success",
            "build_status": "success",
            "context_status": "failed",
            "error": context_result.error
        }
    
    # Both succeeded, commit and create PR
    return {
        "status": "success",
        "build_result": build_result,
        "context_result": context_result
    }
```

### Configuration

**New config option** (in settings or .claude/config):
```yaml
orchestrator:
  build:
    auto_generate_context: true  # Default: true
    context_depth: "comprehensive"  # quick, standard, comprehensive
    separate_context_commit: true  # Separate commit for docs
    skip_on_context_failure: false  # Continue to PR even if context fails
```

---

## Error Handling

### Scenario 1: Build succeeds, context fails
**Action:**
- Keep code commit
- Skip context commit
- Mark output as `"status": "partial_success"`
- Continue to `orchestrator:pr` with code only
- PR description includes warning: `⚠️ Context generation failed`

### Scenario 2: Build succeeds, context succeeds, git commit fails
**Action:**
- Return error with diagnostic info
- Don't proceed to `orchestrator:pr`
- User can manually commit or retry
- Generated artifacts are in memory (not lost)

### Scenario 3: PR creation fails
**Action:**
- Both commits already in branch
- Return branch URL to user
- User can create PR manually via GitHub
- Return PR-ready state info

---

## Testing Strategy

### Unit Tests
- `test_auto_chain_context_invocation()` — Verify context is called with correct args
- `test_dual_commit_creation()` — Verify both commits are created with proper messages
- `test_commit_linking()` — Verify second commit references first
- `test_error_handling_build_fails()` — Build error stops chain
- `test_error_handling_context_fails()` — Context failure handled gracefully

### Integration Tests
- `test_full_chain_build_context_pr()` — End-to-end orchestrator:build → context → pr
- `test_generated_project_has_context()` — Verify docs/context/ exists in generated code
- `test_pr_description_mentions_both_commits()` — PR description links both commits
- `test_backward_compatibility_build_standalone()` — orchestrator:build works without auto-chain

### Edge Cases
- Large projects (100K+ LOC) → context generation completes in reasonable time
- Projects with existing docs/context/ → context artifacts are overwritten correctly
- Projects with git errors → failures are handled gracefully
- Network failures → retry logic or user notification

---

## Success Criteria

✅ User calls `orchestrator:build` once, receives fully documented project  
✅ Context artifacts are automatically generated without user action  
✅ Two commits created (code + context) for clear review separation  
✅ PR includes both commits with comprehensive description  
✅ Backward compatible (orchestrator:build still works standalone)  
✅ Auto-chaining can be disabled via config if user prefers manual control  
✅ Clear error messages if any step fails  
✅ Performance is acceptable (context generation doesn't add excessive delay)  

---

## Backwards Compatibility

**No breaking changes:**
- `orchestrator:build` API remains identical
- Existing code calling `orchestrator:build` works unchanged
- New behavior is additive (adds context generation)
- Can be disabled via `auto_generate_context: false` in config

**Opt-out option:**
- Users who prefer manual control can disable auto-chaining
- Users can call `orchestrator:build` standalone as before
- Users can call functions separately in custom order

---

## Future Enhancements

**Phase 2 ideas (out of scope for Issue #9):**
1. Post-build hooks system (security scan, performance test, etc.)
2. Custom context templates (allow user-defined context structure)
3. Context versioning (track context changes over time)
4. Selective auto-chaining (only certain phases)
5. Parallel execution (run context generation in parallel with build validation)

---

## Assumptions

- `orchestrator:context` implementation is stable and production-ready
- Git commits can be created in sequence without conflicts
- Generated projects have consistent structure (docs/context/ location)
- Context generation completes in <5 minutes for typical projects
- orchestrator:pr can handle PR creation with multiple commits

---

## Out of Scope

- Modifying `orchestrator:build` implementation (only adding auto-chain trigger)
- Creating new skill or agent (reusing existing functions)
- UI changes (purely backend implementation)
- Documentation for users (handled in function documentation update)
- Performance optimization (future phase)

---

## Related Documentation

- `AGENTS_FUNCTIONS_VERIFIED.md` → orchestrator:build, orchestrator:context, orchestrator:pr
- `ISSUES_DOCUMENTATION_MAPPING.md` → How documentation supports Issue #9
- Issue #9 GitHub issue → Original requirement and discussion

---

**Design Status: APPROVED ✅**  
Ready to proceed to implementation planning phase.
