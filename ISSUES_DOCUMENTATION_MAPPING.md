# Open Issues — Documentation Support Mapping

**Date:** June 10, 2026  
**Status:** Documentation foundation complete for all 3 open issues

---

## Overview

This document maps the 3 open GitHub issues to the comprehensive function documentation we've created, showing how the documentation provides the foundation for implementing each issue.

---

## Issue #11: Implement Centralized Instructions Framework with Provider-Specific Export Support

**Status:** OPEN  
**Link:** https://github.com/sharmapuneet1510/awesome-prompts/issues/11

### What It Needs

- Unified instruction schema as source of truth
- Provider-specific templates (Claude, GPT, Gemini, etc.)
- Versioning and rollback capability
- Validation system for instruction completeness
- Standardized agent workspace directory structure
- Hierarchical instructions (global → provider → agent-specific)

### Documentation Support

**AGENTS_FUNCTIONS_VERIFIED.md**
- ✅ All 28 agent functions documented with clear inputs/outputs
- ✅ Guardrails establish constraints and preconditions
- ✅ Examples show expected behavior and outputs
- **Use:** Foundation for defining instruction schema (what each function expects)

**FUNCTION_AUDIT_SUMMARY.md**
- ✅ Documents quality standards: Purpose, Inputs, Outputs, Guardrails
- ✅ Template structure can become instruction schema
- **Use:** Template format for instruction metadata (priority, applicability, version, deprecation)

**docs/superpowers/specs + docs/superpowers/plans**
- ✅ Detailed specification and implementation guidance
- ✅ Shows how to structure complex multi-phase systems
- **Use:** Pattern for instruction framework architecture (similar to our 3-phase approach)

### Implementation Steps

1. **Create instruction_schema.yaml** based on our documentation template
   ```yaml
   function:
     name: string
     purpose: string
     inputs: {}
     outputs: {}
     guardrails: []
     examples: []
     error_handling: {}
     edge_cases: []
   ```

2. **Define provider-specific formatters**
   - Claude: XML-style tags (like system prompt)
   - GPT: System message compatible format
   - Gemini: JSON-based instruction format

3. **Build validation system** against the schema (verify instruction completeness)

4. **Implement versioning** with Git tags (rollback capability)

5. **Create instruction hierarchy**
   - Global instructions (apply to all agents)
   - Provider-specific overrides (Claude, GPT, Gemini)
   - Agent-specific instructions (orchestrator, architect, etc.)

### Key References

- `AGENTS_FUNCTIONS_VERIFIED.md` — Agent function specifications
- `FUNCTION_AUDIT_SUMMARY.md` — Quality standards and template
- `docs/superpowers/specs/` — System design patterns
- `tools/exporter.py` — Existing multi-platform export logic (can extend for instruction export)

---

## Issue #10: QA Test Automation Generator

**Status:** OPEN  
**Link:** https://github.com/sharmapuneet1510/awesome-prompts/issues/10

### What It Needs

- BDD framework test generation
- Automated test case creation from requirements
- Test automation for quality assurance
- Comprehensive test coverage

### Documentation Support

**quality:audit function** (in AGENTS_FUNCTIONS_VERIFIED.md)
- ✅ Purpose: "Perform comprehensive codebase audit (architecture, SOLID, tech debt)"
- ✅ Real-world examples: Full codebase analysis with issue identification
- **Use:** Reference for what quality checks should verify (patterns, coverage, compliance)

**quality:review function** (in AGENTS_FUNCTIONS_VERIFIED.md)
- ✅ Purpose: "Comprehensive PR validation (6-phase scoring + JIRA validation)"
- ✅ Examples: Code quality assessment, testing requirement verification
- **Use:** Reference for what test automation should validate (requirements met, coverage targets)

**test_skill** (in SKILLS_REFERENCE_VERIFIED.md)
- ✅ Purpose: "Generate 95%+ coverage test suite (JUnit5, pytest, Jest)"
- ✅ Scope: Unit tests, integration tests, E2E tests with BDD frameworks
- ✅ Examples: Real-world test case patterns for JUnit5, pytest, Jest
- **Use:** Direct reference for BDD test generation patterns

**code_review_generator.py** (in TOOLS_FUNCTIONS_VERIFIED.md)
- ✅ Generates detailed PR analysis with issue identification
- ✅ Pattern for requirement analysis and validation
- **Use:** Template for analyzing test requirements from specs

**token_optimizer/analyzer.py** (in TOOLS_FUNCTIONS_VERIFIED.md)
- ✅ Multi-dimensional query analysis and scoring
- **Use:** Can analyze test coverage metrics and recommend additional tests

### Implementation Steps

1. **Create BDD test generator** using `test_skill` as foundation
   - Learn BDD patterns from test_skill documentation
   - Implement generator for JUnit5, pytest, Jest frameworks

2. **Integrate with requirement_parser.py**
   - Parse test requirements from specifications
   - Extract acceptance criteria and test cases

3. **Use code_review_generator.py patterns** for test validation
   - Analyze generated tests for coverage gaps
   - Generate quality report for test suite

4. **Implement coverage analysis** using `quality:audit` patterns
   - Verify code coverage meets targets (95%+)
   - Identify untested code paths

5. **Connect to JIRA** for test case tracking
   - Link test cases to requirements
   - Update issue status based on test results

### Key References

- `SKILLS_REFERENCE_VERIFIED.md` → `test_skill` section
- `AGENTS_FUNCTIONS_VERIFIED.md` → `quality:audit` and `quality:review` sections
- `TOOLS_FUNCTIONS_VERIFIED.md` → `code_review_generator.py` and `token_optimizer/analyzer.py`
- `FUNCTION_EXAMPLES.md` → Test generation examples

---

## Issue #9: Autonomous Developer Agent Should Auto-Call Context Creation Post Execution

**Status:** OPEN  
**Link:** https://github.com/sharmapuneet1510/awesome-prompts/issues/9

### What It Needs

- Orchestrator:build runs full end-to-end generation
- After implementation, auto-call orchestrator:context to update docs
- Post-execution context creation should be automatic
- Context artifacts: architecture.md, tech-stack.md, design.html, context.json

### Documentation Support

**orchestrator:build function** (in AGENTS_FUNCTIONS_VERIFIED.md)
- ✅ Purpose: "Full-stack end-to-end generation (architect → implementer → quality)"
- ✅ Examples: E-Commerce MVP, Shopping Cart, Full React Dashboard
- **Use:** Shows current behavior and identifies where context hook should trigger

**orchestrator:context function** (in AGENTS_FUNCTIONS_VERIFIED.md)
- ✅ Purpose: "Build project context (architecture.md, tech-stack.md, design.html)"
- ✅ Inputs: project directory, optional project name
- ✅ Outputs: Complete context artifacts in docs/context/
- **Use:** Perfect candidate for post-execution hook (ready to invoke)

**orchestrator:full function** (in AGENTS_FUNCTIONS_VERIFIED.md)
- ✅ Bundles build + test + doc in one context window
- ✅ Shows pattern for chaining related functions
- **Use:** Template for bundling build + context (could create orchestrator:build-with-context)

**FUNCTION_AUDIT_SUMMARY.md**
- ✅ Documents data flow and integration points
- ✅ Shows how functions interact and chain
- **Use:** Reference for designing automation hooks and function sequencing

### Implementation Steps

1. **Modify orchestrator:build** to return status signal
   - Include completion flag and generated code directory
   - Return artifact locations and summary

2. **Add post-execution hook** in orchestrator:pr
   - After code merge confirmation
   - Before final PR completion

3. **Automatically invoke orchestrator:context**
   - Pass generated code directory as input
   - Wait for context generation to complete

4. **Update context artifacts**
   - architecture.md (updated system design)
   - tech-stack.md (verified tech choices)
   - design.html (interactive visualization)
   - context.json (machine-readable metadata)

5. **Commit updated context** as separate commit
   - Commit message: "docs: auto-generated context post-implementation"
   - Reference original build commit
   - Include in same PR for atomic merge

### Key References

- `AGENTS_FUNCTIONS_VERIFIED.md` → `orchestrator:build`, `orchestrator:context`, `orchestrator:full` sections
- `FUNCTION_AUDIT_SUMMARY.md` → Data flow and integration points
- `docs/architecture-reference.html` → Architecture tab shows system topology and integration points
- `tools/github_sync.py` → PR creation logic (where hook would be added)

---

## Summary: Documentation Enabling Implementation

| Issue | Core Function | Documented | Pattern | Status |
|-------|---|---|---|---|
| #11 | Instruction Schema | All 28 agents | Template-based structure | ✅ Ready |
| #10 | Test Automation | test_skill, quality:audit, quality:review | BDD patterns, validation patterns | ✅ Ready |
| #9 | Context Auto-Creation | orchestrator:build, orchestrator:context, orchestrator:full | Function chaining patterns | ✅ Ready |

### Key Insights

1. **Issue #11** — Documentation template structure becomes the instruction schema
   - Each function's {Purpose, Inputs, Outputs, Guardrails, Examples} is the schema
   - Provider-specific formatters just transform the structure

2. **Issue #10** — Quality functions and test_skill provide the validation blueprint
   - test_skill shows what good tests look like
   - quality:review shows validation criteria
   - Can automate test generation by analyzing these patterns

3. **Issue #9** — Function documentation enables clear chaining logic
   - orchestrator:build → orchestrator:context is documented as a natural flow
   - Inputs/outputs align for seamless integration
   - Could create composite function or auto-hook

---

## Next Phase: Implementation

With the documentation foundation in place, each issue can now be implemented by:

1. **Reading** the relevant function documentation
2. **Understanding** the patterns and examples
3. **Building** based on the documented behavior
4. **Testing** against the examples to verify correctness

All 3 issues have clear implementation roadmaps based on our comprehensive function documentation.

---

**Last Updated:** June 10, 2026  
**Created by:** Comprehensive Function Documentation Project  
**Related Files:**
- AGENTS_FUNCTIONS_VERIFIED.md
- TOOLS_FUNCTIONS_VERIFIED.md
- SKILLS_REFERENCE_VERIFIED.md
- FUNCTION_AUDIT_SUMMARY.md
- docs/architecture-reference.html
