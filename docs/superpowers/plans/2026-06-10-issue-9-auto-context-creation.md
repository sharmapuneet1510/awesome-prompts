# Issue #9: Auto Context Creation Post-Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement automatic context generation after orchestrator:build completes, so users get fully documented projects without manual steps.

**Architecture:** Backend auto-chaining detects when orchestrator:build finishes successfully, automatically invokes orchestrator:context with the generated project directory, commits both code and context in separate commits, and chains to orchestrator:pr for a complete workflow. User experience unchanged: call orchestrator:build once.

**Tech Stack:** Python (orchestrator agents), Git (commit handling), Configuration (YAML), Testing (pytest for unit tests, integration tests for full chain)

---

## File Structure

**Modified Files:**
- `agents/orchestrator_agent.md` (existing agent definition) — Add auto-chain behavior
- `agents/orchestrator/` (check if exists) — May need to add configuration
- `config.yaml` or `.claude/config` (existing) — Add auto_generate_context option

**New Files:**
- `src/orchestrator/git_handler.py` (NEW) — Handle dual commit creation with linking
- `tests/orchestrator/test_auto_chain_context.py` (NEW) — Test auto-chain invocation
- `tests/orchestrator/test_dual_commits.py` (NEW) — Test dual commit creation
- `tests/orchestrator/test_error_handling.py` (NEW) — Test failure scenarios

**Implementation Locations:**
- Auto-chain detection: orchestrator agent (modify existing or add new method)
- Dual commit handling: new git_handler.py module
- PR enhancement: existing orchestrator:pr function (minor enhancement)
- Configuration: existing config system (add new options)

---

# PHASE 1: Setup & Discovery (Task 1-2)

## Task 1: Discover Current Orchestrator Implementation

**Files:**
- Read: `agents/orchestrator_agent.md`
- Read: `agents/orchestrator/` directory structure (if exists)
- Read: Existing orchestrator function definitions

- [ ] **Step 1: Locate orchestrator agent definition**

Check if orchestrator is implemented as:
```bash
ls -la /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/agents/
ls -la /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/agents/orchestrator/
```

Expected: Find orchestrator_agent.md or orchestrator/ directory with implementation files

- [ ] **Step 2: Review orchestrator:build current implementation**

Read the orchestrator agent file to understand:
- How orchestrator:build currently works
- How it returns results (success/failure status)
- Where to hook in auto-chain logic
- Current commit strategy

- [ ] **Step 3: Review orchestrator:context current implementation**

Read the orchestrator agent to understand:
- How orchestrator:context is invoked
- What inputs it requires (path, depth, etc.)
- What outputs it produces
- Error handling behavior

- [ ] **Step 4: Review orchestrator:pr current implementation**

Read to understand:
- How PR is currently created
- Whether it can handle multiple commits
- How PR description is built
- Error scenarios

- [ ] **Step 5: Document findings**

Create notes on:
- Location of orchestrator implementation
- Current invocation patterns
- Where auto-chain trigger should be added
- Commit patterns (how does orchestrator currently commit?)

---

## Task 2: Discover Git & Configuration System

**Files:**
- Read: Existing config files (config.yaml, settings.json, etc.)
- Check: How commits are currently made in orchestrator agents

- [ ] **Step 1: Find configuration system**

```bash
find /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts -name "config.*" -o -name "settings.*" | head -10
```

Expected: Find existing configuration files

- [ ] **Step 2: Review configuration structure**

Read the config file to understand:
- Format (YAML, JSON, TOML)
- Existing agent configuration
- Where to add orchestrator options

- [ ] **Step 3: Check git commit handling**

Search for how orchestrator currently makes commits:
```bash
grep -r "git commit\|git add" /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/agents/ | head -10
```

Expected: Find existing commit patterns to follow

- [ ] **Step 4: Document git patterns**

Note:
- How commits are currently made (CLI, library, wrapper functions)
- Error handling for commit failures
- Commit message format

---

# PHASE 2: Unit Tests (Task 3-5)

## Task 3: Write Test for Auto-Chain Context Invocation

**Files:**
- Create: `tests/orchestrator/test_auto_chain_context.py`

- [ ] **Step 1: Write failing test for auto-chain detection**

```python
import pytest
from unittest.mock import Mock, patch, call

class TestAutoChainContext:
    """Test auto-chaining of orchestrator:context after build completes."""
    
    def test_build_success_triggers_context_auto_chain(self):
        """When orchestrator:build completes successfully, 
           orchestrator:context should be auto-invoked."""
        
        # Mock the orchestrator build result
        build_result = {
            "status": "success",
            "project_dir": "/tmp/generated_project",
            "artifacts": ["code", "tests", "docs"]
        }
        
        # Mock the context invocation
        with patch('orchestrator.invoke_context') as mock_context:
            mock_context.return_value = {
                "status": "success",
                "artifacts": ["architecture.md", "tech-stack.md"]
            }
            
            # Simulate build completion
            from orchestrator import auto_chain_context
            result = auto_chain_context(build_result)
            
            # Assert context was called with correct arguments
            mock_context.assert_called_once_with(
                path="/tmp/generated_project",
                depth="comprehensive"
            )
            
            assert result["status"] == "success"
            assert "context_artifacts" in result
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python -m pytest tests/orchestrator/test_auto_chain_context.py::TestAutoChainContext::test_build_success_triggers_context_auto_chain -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'orchestrator'" or "function not found"

---

## Task 4: Write Test for Dual Commit Creation

**Files:**
- Create: `tests/orchestrator/test_dual_commits.py`

- [ ] **Step 1: Write failing test for dual commit creation**

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

class TestDualCommits:
    """Test creating two separate commits (code + context) with linking."""
    
    def test_dual_commits_created_with_linking(self):
        """Two commits should be created:
           1. Code artifacts
           2. Context artifacts (referencing first commit)"""
        
        code_artifacts = ["src/", "tests/", "README.md"]
        context_artifacts = ["docs/context/architecture.md", "docs/context/tech-stack.md"]
        
        with patch('git_handler.commit') as mock_commit:
            # Setup mock to return commit SHAs
            mock_commit.side_effect = [
                "abc1234567890",  # First commit SHA
                "def1234567890"   # Second commit SHA
            ]
            
            from git_handler import commit_with_chain
            
            commit_shas = commit_with_chain(
                code_artifacts=code_artifacts,
                context_artifacts=context_artifacts,
                code_message="feat: auto-generated implementation",
                context_message="docs: auto-generated project context"
            )
            
            # Verify two commits were made
            assert mock_commit.call_count == 2
            
            # Verify first commit has code artifacts and message
            first_call = mock_commit.call_args_list[0]
            assert code_artifacts == first_call[0][0] or code_artifacts == first_call[1]['files']
            
            # Verify second commit has context artifacts
            # and references first commit
            second_call = mock_commit.call_args_list[1]
            assert context_artifacts == second_call[0][0] or context_artifacts == second_call[1]['files']
            assert "abc1234567890" in str(second_call)  # References first commit
            
            # Verify return value
            assert commit_shas == ["abc1234567890", "def1234567890"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/orchestrator/test_dual_commits.py::TestDualCommits::test_dual_commits_created_with_linking -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'git_handler'"

---

## Task 5: Write Test for Error Handling

**Files:**
- Create: `tests/orchestrator/test_error_handling.py`

- [ ] **Step 1: Write tests for failure scenarios**

```python
import pytest
from unittest.mock import Mock, patch

class TestErrorHandling:
    """Test error handling when build, context, or commits fail."""
    
    def test_context_failure_returns_partial_success(self):
        """When context generation fails, system should:
           - Keep code commit (already made)
           - Skip context commit
           - Mark as 'partial_success'"""
        
        build_result = {"status": "success", "project_dir": "/tmp/project"}
        
        with patch('orchestrator.invoke_context') as mock_context:
            mock_context.return_value = {
                "status": "failed",
                "error": "Architecture analysis failed"
            }
            
            from orchestrator import auto_chain_context
            result = auto_chain_context(build_result)
            
            assert result["status"] == "partial_success"
            assert result["build_status"] == "success"
            assert result["context_status"] == "failed"
            assert "error" in result
    
    def test_commit_failure_stops_chain(self):
        """When git commit fails, system should:
           - Return error to user
           - Not proceed to orchestrator:pr
           - Provide diagnostic info"""
        
        with patch('git_handler.commit') as mock_commit:
            mock_commit.side_effect = Exception("Permission denied: cannot commit")
            
            from git_handler import commit_with_chain
            
            with pytest.raises(Exception) as exc_info:
                commit_with_chain(
                    code_artifacts=["src/"],
                    context_artifacts=["docs/"],
                    code_message="feat: code",
                    context_message="docs: context"
                )
            
            assert "Permission denied" in str(exc_info.value)
    
    def test_build_failure_skips_auto_chain(self):
        """When build fails, auto-chain should not be triggered."""
        
        build_result = {
            "status": "failed",
            "error": "Implementation failed"
        }
        
        with patch('orchestrator.invoke_context') as mock_context:
            from orchestrator import auto_chain_context
            result = auto_chain_context(build_result)
            
            # Context should not be called on build failure
            mock_context.assert_not_called()
            assert result["status"] == "failed"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/orchestrator/test_error_handling.py -v
```

Expected: FAIL (tests for unimplemented error handling logic)

---

# PHASE 3: Implementation (Task 6-10)

## Task 6: Create git_handler.py Module

**Files:**
- Create: `src/orchestrator/git_handler.py` (or appropriate location)

- [ ] **Step 1: Create git_handler.py file**

```python
"""Git handler for orchestrator agent.

Handles committing generated artifacts with proper linking
and error handling.
"""

import subprocess
from typing import List, Tuple


def commit(files: List[str], message: str, parent_commit: str = None) -> str:
    """Create a git commit with the given files and message.
    
    Args:
        files: List of file paths to commit
        message: Commit message
        parent_commit: Optional SHA of parent commit (for reference in message)
    
    Returns:
        Commit SHA (hash)
    
    Raises:
        subprocess.CalledProcessError: If git commit fails
    """
    if not files:
        raise ValueError("No files to commit")
    
    # Stage files
    subprocess.run(["git", "add"] + files, check=True)
    
    # Add parent reference if provided
    full_message = message
    if parent_commit:
        full_message = f"{message}\n\nAutomated context for {parent_commit}"
    
    # Create commit
    result = subprocess.run(
        ["git", "commit", "-m", full_message],
        capture_output=True,
        text=True,
        check=True
    )
    
    # Extract SHA from output (first 7 chars)
    # Output format: [main abc1234] commit message
    commit_sha = result.stdout.split()[1].rstrip("]")
    return commit_sha


def commit_with_chain(
    code_artifacts: List[str],
    context_artifacts: List[str],
    code_message: str,
    context_message: str
) -> Tuple[str, str]:
    """Create two linked commits: code + context.
    
    Args:
        code_artifacts: List of files for code commit
        context_artifacts: List of files for context commit
        code_message: Message for code commit
        context_message: Message for context commit
    
    Returns:
        Tuple of (code_commit_sha, context_commit_sha)
    
    Raises:
        subprocess.CalledProcessError: If either commit fails
    """
    # Commit 1: Code artifacts
    code_sha = commit(code_artifacts, code_message)
    
    # Commit 2: Context (references code commit)
    context_sha = commit(context_artifacts, context_message, parent_commit=code_sha)
    
    return (code_sha, context_sha)
```

- [ ] **Step 2: Run Step 1 test to verify it passes**

```bash
python -m pytest tests/orchestrator/test_dual_commits.py::TestDualCommits::test_dual_commits_created_with_linking -v
```

Expected: PASS (git_handler module now exists with correct interface)

- [ ] **Step 3: Run Step 5 test to verify error handling**

```bash
python -m pytest tests/orchestrator/test_error_handling.py::TestErrorHandling::test_commit_failure_stops_chain -v
```

Expected: PASS (commit failure raises exception as expected)

- [ ] **Step 4: Commit**

```bash
git add src/orchestrator/git_handler.py tests/orchestrator/test_dual_commits.py tests/orchestrator/test_error_handling.py
git commit -m "feat: add git_handler module for dual commit creation

Implements commit_with_chain() to create two linked commits:
1. Code artifacts with main message
2. Context artifacts referencing first commit

Error handling: raises exception on commit failure (stops chain)

Tests pass for dual commit creation and error scenarios."
```

---

## Task 7: Implement Auto-Chain Logic in Orchestrator

**Files:**
- Modify: Orchestrator agent implementation (location TBD by Task 1)
- Test: tests/orchestrator/test_auto_chain_context.py

- [ ] **Step 1: Add _auto_chain_context method to orchestrator agent**

```python
def _auto_chain_context(self, build_result: dict) -> dict:
    """Auto-invoke orchestrator:context after successful build.
    
    Args:
        build_result: Result from orchestrator:build
        
    Returns:
        Combined result with both build and context outcomes
    """
    # Only auto-chain if build succeeded
    if build_result.get("status") != "success":
        return build_result
    
    # Get generated project directory
    project_dir = build_result.get("project_dir")
    if not project_dir:
        return {
            **build_result,
            "warning": "No project directory in build result"
        }
    
    # Check if auto-chaining is enabled (default: true)
    config = self.get_config()
    if not config.get("orchestrator", {}).get("build", {}).get("auto_generate_context", True):
        return build_result
    
    # Invoke orchestrator:context
    try:
        context_depth = config.get("orchestrator", {}).get("build", {}).get("context_depth", "comprehensive")
        
        context_result = self.invoke_context(
            path=project_dir,
            depth=context_depth
        )
        
        return {
            "status": "success",
            "build_result": build_result,
            "context_result": context_result,
            "build_status": "success",
            "context_status": context_result.get("status")
        }
    
    except Exception as e:
        # Context failed - mark as partial success
        return {
            "status": "partial_success",
            "build_result": build_result,
            "build_status": "success",
            "context_status": "failed",
            "context_error": str(e),
            "warning": f"Context generation failed: {str(e)}"
        }
```

- [ ] **Step 2: Hook auto-chain into orchestrator:build completion**

In the orchestrator:build function, after build completes:

```python
# In orchestrator:build, after all phases complete successfully:
final_result = {
    "status": "success",
    "project_dir": generated_path,
    "artifacts": [code, tests, docs, ci_cd, docker, iac]
}

# Auto-chain context generation
auto_chain_result = self._auto_chain_context(final_result)

return auto_chain_result
```

- [ ] **Step 3: Run test to verify auto-chain is called**

```bash
python -m pytest tests/orchestrator/test_auto_chain_context.py::TestAutoChainContext::test_build_success_triggers_context_auto_chain -v
```

Expected: PASS (auto-chain detection works)

- [ ] **Step 4: Run error handling test**

```bash
python -m pytest tests/orchestrator/test_error_handling.py::TestErrorHandling::test_context_failure_returns_partial_success -v
```

Expected: PASS (partial success on context failure)

- [ ] **Step 5: Commit**

```bash
git add [orchestrator implementation file] tests/orchestrator/test_auto_chain_context.py
git commit -m "feat: add auto-chain context to orchestrator:build

After orchestrator:build completes successfully, automatically invoke
orchestrator:context with depth=comprehensive.

Auto-chaining behavior:
- Enabled by default (configurable via orchestrator.build.auto_generate_context)
- Returns partial_success if context fails (keeps code commit)
- Skipped if build fails (no context generation needed)

Tests pass for auto-chain invocation and error scenarios."
```

---

## Task 8: Implement Dual Commit Handling

**Files:**
- Modify: Orchestrator agent or new orchestrator_bridge.py
- Use: git_handler.py module

- [ ] **Step 1: Create orchestrator_bridge.py if needed**

Check if orchestrator_bridge exists:
```bash
find /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts -name "orchestrator_bridge.py"
```

If not, create it:

```python
"""Bridge between orchestrator functions and git/PR handling."""

from typing import List, Dict, Any
from git_handler import commit_with_chain


def invoke_build_and_context_chain(
    orchestrator,
    requirements_path: str,
    context: str = None,
    tech_stack: str = None
) -> Dict[str, Any]:
    """Execute full build + context + PR chain.
    
    Args:
        orchestrator: Orchestrator agent instance
        requirements_path: Path to requirements.md
        context: Optional business context
        tech_stack: Optional tech stack preference
    
    Returns:
        Result with PR URL, commit SHAs, and status
    """
    # Phase 1: Build (which auto-chains context)
    build_and_context_result = orchestrator.build(
        requirements_path=requirements_path,
        context=context,
        tech_stack=tech_stack
    )
    
    if build_and_context_result.get("status") not in ["success", "partial_success"]:
        return build_and_context_result
    
    # Extract artifacts for commit
    build_result = build_and_context_result.get("build_result", {})
    context_result = build_and_context_result.get("context_result", {})
    
    code_artifacts = build_result.get("artifacts", [])
    context_artifacts = context_result.get("artifacts", []) if context_result else []
    
    # Phase 2: Create commits
    try:
        if code_artifacts and context_artifacts:
            # Both succeeded - create dual commits
            code_sha, context_sha = commit_with_chain(
                code_artifacts=code_artifacts,
                context_artifacts=context_artifacts,
                code_message="feat: auto-generated implementation",
                context_message="docs: auto-generated project context"
            )
            commits = [code_sha, context_sha]
        elif code_artifacts:
            # Only code succeeded
            from git_handler import commit
            code_sha = commit(
                files=code_artifacts,
                message="feat: auto-generated implementation"
            )
            commits = [code_sha]
        else:
            return {
                "status": "error",
                "error": "No artifacts to commit"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "error": f"Commit failed: {str(e)}",
            "note": "Generated artifacts are in memory, please commit manually"
        }
    
    # Phase 3: Create PR
    try:
        pr_result = orchestrator.pr(commits=commits)
        
        return {
            "status": "success",
            "build_status": build_and_context_result.get("build_status"),
            "context_status": build_and_context_result.get("context_status"),
            "commits": commits,
            "pr_url": pr_result.get("pr_url"),
            "pr_number": pr_result.get("pr_number")
        }
    
    except Exception as e:
        return {
            "status": "pr_creation_failed",
            "commits": commits,
            "error": f"PR creation failed: {str(e)}",
            "note": f"Commits are on branch, create PR manually at GitHub"
        }
```

- [ ] **Step 2: Update orchestrator:pr to handle multiple commits**

Modify orchestrator:pr to detect and handle multiple commits:

```python
def pr(self, commits: List[str] = None) -> Dict[str, Any]:
    """Create GitHub PR with generated artifacts.
    
    Args:
        commits: Optional list of commit SHAs to include in PR description
    
    Returns:
        PR creation result (URL, number, status)
    """
    # ... existing PR creation logic ...
    
    # Enhanced: Handle multiple commits
    if commits and len(commits) > 1:
        # Build description highlighting both commits
        description = f"""
## Auto-Generated Implementation

This PR includes:
- **Code & Tests**: {commits[0]} - Implementation with full test suite
- **Project Context**: {commits[1]} - Architecture documentation, tech stack, design visualization

Both commits are ready for review.
"""
    else:
        # Single commit or existing logic
        description = "Auto-generated implementation"
    
    # ... rest of PR creation ...
```

- [ ] **Step 3: Test dual commit scenario**

```bash
python -m pytest tests/orchestrator/test_dual_commits.py -v
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/orchestrator/orchestrator_bridge.py [orchestrator pr modifications]
git commit -m "feat: implement dual commit handling and PR creation

- orchestrator_bridge.py: Coordinate build → context → pr chain
- git_handler.commit_with_chain(): Create linked code + context commits
- orchestrator:pr enhancement: Detect and describe multiple commits in PR

Error handling:
- Build fails: Stop chain
- Context fails: Create code commit only (partial_success)
- Commit fails: Return to user (branch ready for manual PR)
- PR creation fails: Commits already made (user can create PR manually)

Tests pass for dual commit creation."
```

---

# PHASE 4: Configuration (Task 9)

## Task 9: Add Configuration Options

**Files:**
- Modify: config.yaml or configuration system

- [ ] **Step 1: Add auto-chain configuration options**

Find config file (from Task 2):
```bash
cat [config file location]
```

Add or update orchestrator configuration:

```yaml
orchestrator:
  build:
    auto_generate_context: true
    context_depth: "comprehensive"  # quick, standard, comprehensive
    separate_context_commit: true
    skip_on_context_failure: false  # Continue to PR even if context fails
```

- [ ] **Step 2: Update orchestrator code to read config**

In orchestrator agent, add:

```python
def get_config(self) -> dict:
    """Load configuration for orchestrator."""
    import yaml
    
    try:
        with open('.claude/config.yaml', 'r') as f:
            config = yaml.safe_load(f) or {}
        return config
    except FileNotFoundError:
        return {}  # Default config (auto_generate_context: true)
```

- [ ] **Step 3: Test configuration loading**

```bash
# Create test config
cat > /tmp/test_config.yaml << 'EOF'
orchestrator:
  build:
    auto_generate_context: true
    context_depth: "comprehensive"
EOF

# Verify it loads
python -c "import yaml; f=open('/tmp/test_config.yaml'); print(yaml.safe_load(f))"
```

Expected: Config loads correctly

- [ ] **Step 4: Commit**

```bash
git add .claude/config.yaml
git commit -m "config: add orchestrator auto-chain configuration options

Add settings for Issue #9 auto-context-creation:
- auto_generate_context: true (default, can be disabled)
- context_depth: comprehensive (quick, standard, comprehensive)
- separate_context_commit: true (context in separate commit)
- skip_on_context_failure: false (include code even if context fails)

Configuration read from .claude/config.yaml (YAML format)."
```

---

# PHASE 5: Integration Testing (Task 10)

## Task 10: Write & Run Integration Tests

**Files:**
- Create: `tests/orchestrator/test_integration_build_context_pr.py`

- [ ] **Step 1: Write end-to-end integration test**

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

class TestIntegrationBuildContextPR:
    """Integration test for full orchestrator:build → context → pr chain."""
    
    def test_full_chain_build_context_pr(self):
        """Complete workflow: build → auto-chain context → dual commits → PR."""
        
        # Setup mocks for all phases
        with patch('orchestrator.architect_design') as mock_architect, \
             patch('orchestrator.implementer_build') as mock_impl, \
             patch('orchestrator.quality_review') as mock_quality, \
             patch('orchestrator.invoke_context') as mock_context, \
             patch('git_handler.commit_with_chain') as mock_commits, \
             patch('orchestrator.pr') as mock_pr:
            
            # Phase 1: Build phases produce artifacts
            mock_architect.return_value = {"status": "success", "design": "..."}
            mock_impl.return_value = {
                "status": "success",
                "artifacts": ["src/", "tests/", "README.md"]
            }
            mock_quality.return_value = {"status": "success", "score": 95}
            
            # Phase 2: Context generation
            mock_context.return_value = {
                "status": "success",
                "artifacts": ["docs/context/architecture.md", "docs/context/tech-stack.md"]
            }
            
            # Phase 3: Dual commits
            mock_commits.return_value = ("abc1234", "def5678")
            
            # Phase 4: PR creation
            mock_pr.return_value = {
                "status": "success",
                "pr_url": "https://github.com/user/repo/pull/42",
                "pr_number": 42
            }
            
            # Execute build (which auto-chains context)
            from orchestrator import build_and_context_chain
            
            result = build_and_context_chain(
                requirements_path="requirements.md",
                context="Generate e-commerce MVP",
                tech_stack="Python FastAPI + React"
            )
            
            # Verify all phases executed
            assert mock_architect.called, "Architect should be called"
            assert mock_impl.called, "Implementer should be called"
            assert mock_quality.called, "Quality should be called"
            assert mock_context.called, "Context should be auto-called"
            assert mock_commits.called, "Commits should be made"
            assert mock_pr.called, "PR should be created"
            
            # Verify result
            assert result["status"] == "success"
            assert result["pr_number"] == 42
            assert result["commits"] == ["abc1234", "def5678"]
```

- [ ] **Step 2: Run integration test**

```bash
python -m pytest tests/orchestrator/test_integration_build_context_pr.py::TestIntegrationBuildContextPR::test_full_chain_build_context_pr -v
```

Expected: PASS (full chain works end-to-end)

- [ ] **Step 3: Run all tests to verify nothing broke**

```bash
python -m pytest tests/orchestrator/ -v
```

Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/orchestrator/test_integration_build_context_pr.py
git commit -m "test: add integration test for full build → context → pr chain

End-to-end test verifying:
- orchestrator:build completes (architect → implementer → quality)
- orchestrator:context auto-invoked with correct path
- Dual commits created (code + context) with linking
- orchestrator:pr creates PR with both commits
- Result returns PR URL and commit SHAs

All phases execute in correct order with proper data flow."
```

---

# PHASE 6: Documentation & Finalization (Task 11)

## Task 11: Update Agent Documentation

**Files:**
- Modify: `AGENTS_FUNCTIONS_VERIFIED.md` (orchestrator:build section)

- [ ] **Step 1: Update orchestrator:build documentation to mention auto-chaining**

Find orchestrator:build section and add note about auto-chaining:

```markdown
### orchestrator:build

**Purpose:** Execute full-stack generation end-to-end. Orchestrates downstream agents (architect → implementer → quality) in sequence to produce a complete, tested system. **Automatically generates project context after completion.**

[... existing documentation ...]

**Auto-Chaining Behavior:**
When orchestrator:build completes successfully:
1. Automatically invokes orchestrator:context with generated project
2. Generates architecture documentation (architecture.md, tech-stack.md, design.html, context.json)
3. Creates two commits: code artifacts + context artifacts (separately for clear review)
4. Proceeds to orchestrator:pr to create PR with both commits

This behavior can be disabled via configuration (`orchestrator.build.auto_generate_context: false`)
if you prefer to manage context generation manually.

**Output includes:**
- Complete system with code, tests, docs, CI/CD, Docker, IaC
- Project context: architecture documentation and tech stack reference
- Two commits: code + context (linked for traceability)
- GitHub PR ready for review
```

- [ ] **Step 2: Verify documentation is clear and complete**

Re-read the updated section to ensure:
- Auto-chaining behavior is clearly explained
- Configuration option is documented
- Output expectations are clear
- No placeholders or TBDs remain

- [ ] **Step 3: Commit**

```bash
git add AGENTS_FUNCTIONS_VERIFIED.md
git commit -m "docs: update orchestrator:build documentation for Issue #9 auto-chaining

Document auto-context-generation behavior:
- orchestrator:build auto-invokes orchestrator:context after completion
- Generates project context artifacts (architecture, tech-stack, design)
- Creates two linked commits (code + context)
- Proceeds to orchestrator:pr with both commits
- Can be disabled via config if needed

Users now understand that orchestrator:build produces fully documented projects."
```

---

# Summary of Implementation

**What Gets Built:**

1. ✅ **git_handler.py** — Module for creating linked dual commits
2. ✅ **Auto-chain Logic** — Orchestrator:build triggers context after completion
3. ✅ **Dual Commits** — Code and context in separate commits for review clarity
4. ✅ **Enhanced orchestrator:pr** — Handles multiple commits in PR description
5. ✅ **Configuration** — Enable/disable auto-chaining via config
6. ✅ **Tests** — Unit + integration tests covering all scenarios
7. ✅ **Documentation** — Updated orchestrator:build docs explaining auto-chain

**User Experience:**

- Call `orchestrator:build` once
- System auto-generates context documentation
- Two commits created (code + context) and included in PR
- No manual steps needed
- Can be disabled via config if preferred

**Error Handling:**

- Build fails → Skip auto-chain
- Context fails → Create code commit only (partial_success)
- Commit fails → Return error to user
- PR fails → Commits already made, user can create PR manually

---

Plan complete and saved to `docs/superpowers/plans/2026-06-10-issue-9-auto-context-creation.md`.

## Execution Options

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach would you like?
