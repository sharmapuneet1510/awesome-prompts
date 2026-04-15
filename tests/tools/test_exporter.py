"""Tests for tools/exporter.py"""
from pathlib import Path
import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────

def write_skill(tmp_path: Path, filename: str, content: str) -> Path:
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


def write_agent(tmp_path: Path, role: str, filename: str, content: str) -> Path:
    d = tmp_path / role
    d.mkdir(parents=True, exist_ok=True)
    p = d / filename
    p.write_text(content, encoding="utf-8")
    return p


# ── Test fixtures ─────────────────────────────────────────────────────────────

SKILL_MD = """\
---
name: Java Advanced Coding Skill
version: 2.0
description: >
  A reusable skill for Java coding.
applies_to: [java, spring-boot, maven]
tags: [java, spring, patterns]
---

# Java Advanced Skill

Some content here.
"""

SKILL_INLINE_LIST = """\
---
name: Test Skill
version: 1.0
description: Short description
applies_to:
  - python
  - fastapi
tags:
  - python
  - api
---

Body content.
"""

SKILL_NO_FRONTMATTER = "# Just a heading\n\nNo frontmatter here."

AGENT_MD = """\
---
name: Java Senior Engineering Agent
version: 2.0
description: >
  Advanced Java coding agent for Spring Boot projects.
skills: [java_advanced_skill]
instruction_set: instructions/master_instruction_set.md
intake_form: instructions/java_project_intake.md
---

# Java Senior Engineering Agent

You are Jarvis.
"""

AGENT_MULTI_SKILLS = """\
---
name: Code Health Inspector Agent
version: 1.0
description: Step-by-step code scanning agent.
skills:
  - code_health_skill
  - java_advanced_skill
instruction_set: instructions/master_instruction_set.md
intake_form: instructions/java_project_intake.md
---

Inspector body.
"""


# ── SkillFile tests ───────────────────────────────────────────────────────────

def test_skill_file_parses_name(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert skill.name == "Java Advanced Coding Skill"


def test_skill_file_parses_version(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert skill.version == "2.0"


def test_skill_file_parses_block_scalar_description(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert "reusable skill for Java" in skill.description


def test_skill_file_parses_inline_applies_to(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert skill.applies_to == ["java", "spring-boot", "maven"]


def test_skill_file_parses_block_list_applies_to(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "test_skill.md", SKILL_INLINE_LIST)
    skill = SkillFile.from_path(path)
    assert skill.applies_to == ["python", "fastapi"]


def test_skill_file_parses_inline_tags(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert skill.tags == ["java", "spring", "patterns"]


def test_skill_file_slug_is_stem(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert skill.slug == "java_advanced_skill"


def test_skill_file_content_strips_frontmatter(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert "# Java Advanced Skill" in skill.content
    assert "applies_to:" not in skill.content


def test_skill_file_raises_on_missing_frontmatter(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "bad.md", SKILL_NO_FRONTMATTER)
    with pytest.raises(ValueError, match="missing YAML frontmatter"):
        SkillFile.from_path(path)


# ── AgentFile tests ───────────────────────────────────────────────────────────

def test_agent_file_parses_name(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.name == "Java Senior Engineering Agent"


def test_agent_file_parses_version(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.version == "2.0"


def test_agent_file_parses_block_scalar_description(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert "Spring Boot" in agent.description


def test_agent_file_parses_inline_skills(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.skills == ["java_advanced_skill"]


def test_agent_file_parses_block_list_skills(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "reviewer", "code_health_inspector_agent.md", AGENT_MULTI_SKILLS)
    agent = AgentFile.from_path(path)
    assert agent.skills == ["code_health_skill", "java_advanced_skill"]


def test_agent_file_parses_instruction_set(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.instruction_set == "instructions/master_instruction_set.md"


def test_agent_file_role_derived_from_parent_dir(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "reviewer", "code_review_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.role == "reviewer"


def test_agent_file_slug_is_stem(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.slug == "java_advanced_agent"


def test_agent_file_content_strips_frontmatter(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert "You are Jarvis" in agent.content
    assert "instruction_set:" not in agent.content


def test_agent_file_raises_on_missing_frontmatter(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "bad_agent.md", "# No frontmatter here")
    with pytest.raises(ValueError, match="missing YAML frontmatter"):
        AgentFile.from_path(path)


# ── PlatformExporter base ─────────────────────────────────────────────────────

def make_skill(tmp_path: Path) -> "SkillFile":
    from tools.exporter import SkillFile
    p = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    return SkillFile.from_path(p)


def make_agent(tmp_path: Path, role: str = "developer") -> "AgentFile":
    from tools.exporter import AgentFile
    p = write_agent(tmp_path, role, "java_advanced_agent.md", AGENT_MD)
    return AgentFile.from_path(p)


def test_export_result_stores_fields(tmp_path):
    from tools.exporter import ExportResult
    result = ExportResult(
        target="claude",
        skill_files=[tmp_path / "skill.md"],
        agent_files=[tmp_path / "agent.md"],
        dry_run=False,
    )
    assert result.target == "claude"
    assert len(result.skill_files) == 1
    assert len(result.agent_files) == 1
    assert result.dry_run is False


def test_platform_exporter_export_writes_skill_file(tmp_path):
    from tools.exporter import ClaudeExporter
    skill = make_skill(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    exporter.export(skills=[skill], agents=[], dry_run=False)
    out = tmp_path / ".claude" / "skills" / "java_advanced_skill.md"
    assert out.exists()
    assert "Java Advanced" in out.read_text()


def test_platform_exporter_export_writes_agent_file(tmp_path):
    from tools.exporter import ClaudeExporter
    agent = make_agent(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    exporter.export(skills=[], agents=[agent], dry_run=False)
    out = tmp_path / ".claude" / "agents" / "java_advanced_agent.md"
    assert out.exists()


def test_platform_exporter_dry_run_does_not_write(tmp_path):
    from tools.exporter import ClaudeExporter
    skill = make_skill(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    result = exporter.export(skills=[skill], agents=[], dry_run=True)
    out = tmp_path / ".claude" / "skills" / "java_advanced_skill.md"
    assert not out.exists()
    assert result.dry_run is True


def test_platform_exporter_returns_correct_file_paths(tmp_path):
    from tools.exporter import ClaudeExporter
    skill = make_skill(tmp_path)
    agent = make_agent(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    result = exporter.export(skills=[skill], agents=[agent], dry_run=True)
    assert any("java_advanced_skill" in str(p) for p in result.skill_files)
    assert any("java_advanced_agent" in str(p) for p in result.agent_files)


# ── CopilotExporter ───────────────────────────────────────────────────────────

def test_copilot_skill_filename_has_instructions_suffix(tmp_path):
    from tools.exporter import CopilotExporter
    skill = make_skill(tmp_path)
    assert CopilotExporter(repo_root=tmp_path).skill_filename(skill) == "java_advanced_skill.instructions.md"


def test_copilot_skill_format_has_apply_to_frontmatter(tmp_path):
    from tools.exporter import CopilotExporter
    output = CopilotExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "applyTo: '**'" in output


def test_copilot_skill_output_dir(tmp_path):
    from tools.exporter import CopilotExporter
    assert CopilotExporter(repo_root=tmp_path).skill_output_dir() == tmp_path / ".github" / "instructions"


def test_copilot_agent_output_dir(tmp_path):
    from tools.exporter import CopilotExporter
    assert CopilotExporter(repo_root=tmp_path).agent_output_dir() == tmp_path / ".github" / "copilot" / "agents"


def test_copilot_agent_format_has_name_in_frontmatter(tmp_path):
    from tools.exporter import CopilotExporter
    output = CopilotExporter(repo_root=tmp_path).format_agent(make_agent(tmp_path))
    assert "name:" in output
    assert "description:" in output


# ── ClaudeExporter ────────────────────────────────────────────────────────────

def test_claude_skill_output_dir(tmp_path):
    from tools.exporter import ClaudeExporter
    assert ClaudeExporter(repo_root=tmp_path).skill_output_dir() == tmp_path / ".claude" / "skills"


def test_claude_agent_output_dir(tmp_path):
    from tools.exporter import ClaudeExporter
    assert ClaudeExporter(repo_root=tmp_path).agent_output_dir() == tmp_path / ".claude" / "agents"


def test_claude_skill_format_has_generated_comment(tmp_path):
    from tools.exporter import ClaudeExporter
    output = ClaudeExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "Generated by tools/exporter.py" in output


def test_claude_skill_format_preserves_content(tmp_path):
    from tools.exporter import ClaudeExporter
    output = ClaudeExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "# Java Advanced Skill" in output


def test_claude_agent_format_has_generated_comment(tmp_path):
    from tools.exporter import ClaudeExporter
    output = ClaudeExporter(repo_root=tmp_path).format_agent(make_agent(tmp_path))
    assert "Generated by tools/exporter.py" in output


# ── CursorExporter ────────────────────────────────────────────────────────────

def test_cursor_skill_filename_has_mdc_extension(tmp_path):
    from tools.exporter import CursorExporter
    assert CursorExporter(repo_root=tmp_path).skill_filename(make_skill(tmp_path)) == "java_advanced_skill.mdc"


def test_cursor_agent_filename_has_mdc_extension(tmp_path):
    from tools.exporter import CursorExporter
    assert CursorExporter(repo_root=tmp_path).agent_filename(make_agent(tmp_path)) == "java_advanced_agent.mdc"


def test_cursor_skill_output_dir(tmp_path):
    from tools.exporter import CursorExporter
    assert CursorExporter(repo_root=tmp_path).skill_output_dir() == tmp_path / ".cursor" / "rules"


def test_cursor_agent_output_dir(tmp_path):
    from tools.exporter import CursorExporter
    assert CursorExporter(repo_root=tmp_path).agent_output_dir() == tmp_path / ".cursor" / "rules" / "agents"


def test_cursor_skill_format_has_required_frontmatter(tmp_path):
    from tools.exporter import CursorExporter
    output = CursorExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "description:" in output
    assert "globs:" in output
    assert "alwaysApply:" in output


def test_cursor_agent_format_has_role_in_body(tmp_path):
    from tools.exporter import CursorExporter
    output = CursorExporter(repo_root=tmp_path).format_agent(make_agent(tmp_path, role="developer"))
    assert "developer" in output


# ── WindsurfExporter ──────────────────────────────────────────────────────────

def test_windsurf_skill_output_dir(tmp_path):
    from tools.exporter import WindsurfExporter
    assert WindsurfExporter(repo_root=tmp_path).skill_output_dir() == tmp_path / ".windsurf" / "rules"


def test_windsurf_agent_output_dir(tmp_path):
    from tools.exporter import WindsurfExporter
    assert WindsurfExporter(repo_root=tmp_path).agent_output_dir() == tmp_path / ".windsurf" / "rules" / "agents"


def test_windsurf_skill_format_has_generated_comment(tmp_path):
    from tools.exporter import WindsurfExporter
    output = WindsurfExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "Generated by tools/exporter.py" in output


def test_windsurf_agent_format_preserves_content(tmp_path):
    from tools.exporter import WindsurfExporter
    output = WindsurfExporter(repo_root=tmp_path).format_agent(make_agent(tmp_path))
    assert "You are Jarvis" in output


# ── GeminiExporter ────────────────────────────────────────────────────────────

def test_gemini_skill_output_dir(tmp_path):
    from tools.exporter import GeminiExporter
    assert GeminiExporter(repo_root=tmp_path).skill_output_dir() == tmp_path / ".gemini" / "skills"


def test_gemini_agent_output_dir(tmp_path):
    from tools.exporter import GeminiExporter
    assert GeminiExporter(repo_root=tmp_path).agent_output_dir() == tmp_path / ".gemini" / "agents"


def test_gemini_skill_format_has_generated_comment(tmp_path):
    from tools.exporter import GeminiExporter
    output = GeminiExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "Generated by tools/exporter.py" in output


def test_gemini_agent_format_preserves_content(tmp_path):
    from tools.exporter import GeminiExporter
    output = GeminiExporter(repo_root=tmp_path).format_agent(make_agent(tmp_path))
    assert "You are Jarvis" in output


# ── ContinueExporter ──────────────────────────────────────────────────────────

def test_continue_skill_filename_has_prompt_extension(tmp_path):
    from tools.exporter import ContinueExporter
    assert ContinueExporter(repo_root=tmp_path).skill_filename(make_skill(tmp_path)) == "java_advanced_skill.prompt"


def test_continue_agent_filename_has_prompt_extension(tmp_path):
    from tools.exporter import ContinueExporter
    assert ContinueExporter(repo_root=tmp_path).agent_filename(make_agent(tmp_path)) == "java_advanced_agent.prompt"


def test_continue_skill_output_dir(tmp_path):
    from tools.exporter import ContinueExporter
    assert ContinueExporter(repo_root=tmp_path).skill_output_dir() == tmp_path / ".continue" / "prompts"


def test_continue_agent_output_dir(tmp_path):
    from tools.exporter import ContinueExporter
    assert ContinueExporter(repo_root=tmp_path).agent_output_dir() == tmp_path / ".continue" / "prompts" / "agents"


def test_continue_skill_format_has_name_and_description_frontmatter(tmp_path):
    from tools.exporter import ContinueExporter
    output = ContinueExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "name:" in output
    assert "description:" in output


def test_continue_agent_format_has_frontmatter(tmp_path):
    from tools.exporter import ContinueExporter
    output = ContinueExporter(repo_root=tmp_path).format_agent(make_agent(tmp_path))
    assert "name:" in output
    assert "description:" in output


# ── OpenAIExporter ────────────────────────────────────────────────────────────

def test_openai_skill_filename_has_txt_extension(tmp_path):
    from tools.exporter import OpenAIExporter
    assert OpenAIExporter(repo_root=tmp_path).skill_filename(make_skill(tmp_path)) == "java_advanced_skill.txt"


def test_openai_agent_filename_has_txt_extension(tmp_path):
    from tools.exporter import OpenAIExporter
    assert OpenAIExporter(repo_root=tmp_path).agent_filename(make_agent(tmp_path)) == "java_advanced_agent.txt"


def test_openai_skill_output_dir(tmp_path):
    from tools.exporter import OpenAIExporter
    assert OpenAIExporter(repo_root=tmp_path).skill_output_dir() == tmp_path / "tools" / "output" / "openai" / "skills"


def test_openai_agent_output_dir(tmp_path):
    from tools.exporter import OpenAIExporter
    assert OpenAIExporter(repo_root=tmp_path).agent_output_dir() == tmp_path / "tools" / "output" / "openai" / "agents"


def test_openai_skill_format_is_plain_text_with_header(tmp_path):
    from tools.exporter import OpenAIExporter
    output = OpenAIExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "SKILL:" in output
    assert "APPLIES TO:" in output


def test_openai_skill_format_strips_markdown_headings(tmp_path):
    from tools.exporter import OpenAIExporter
    output = OpenAIExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "## " not in output
    assert "# " not in output


def test_openai_agent_format_is_plain_text_with_header(tmp_path):
    from tools.exporter import OpenAIExporter
    output = OpenAIExporter(repo_root=tmp_path).format_agent(make_agent(tmp_path))
    assert "AGENT:" in output
    assert "ROLE:" in output


# ── AiderExporter ─────────────────────────────────────────────────────────────

def test_aider_skill_output_dir(tmp_path):
    from tools.exporter import AiderExporter
    assert AiderExporter(repo_root=tmp_path).skill_output_dir() == tmp_path / ".aider" / "skills"


def test_aider_agent_output_dir(tmp_path):
    from tools.exporter import AiderExporter
    assert AiderExporter(repo_root=tmp_path).agent_output_dir() == tmp_path / ".aider" / "agents"


def test_aider_skill_format_has_generated_comment(tmp_path):
    from tools.exporter import AiderExporter
    output = AiderExporter(repo_root=tmp_path).format_skill(make_skill(tmp_path))
    assert "Generated by tools/exporter.py" in output


def test_aider_agent_format_preserves_content(tmp_path):
    from tools.exporter import AiderExporter
    output = AiderExporter(repo_root=tmp_path).format_agent(make_agent(tmp_path))
    assert "You are Jarvis" in output


# ── ExportOrchestrator ────────────────────────────────────────────────────────

def make_skills_dir(tmp_path: Path) -> Path:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "java_advanced_skill.md").write_text(SKILL_MD, encoding="utf-8")
    (skills_dir / "test_skill.md").write_text(SKILL_INLINE_LIST, encoding="utf-8")
    return skills_dir


def make_agents_dir(tmp_path: Path) -> Path:
    agents_dir = tmp_path / "agents"
    dev_dir = agents_dir / "developer"
    dev_dir.mkdir(parents=True)
    (dev_dir / "java_advanced_agent.md").write_text(AGENT_MD, encoding="utf-8")
    (agents_dir / "README.md").write_text("# Agents\n", encoding="utf-8")
    return agents_dir


def test_orchestrator_discovers_all_skills(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    skills = orch.discover_skills()
    assert len(skills) == 2
    assert any(s.slug == "java_advanced_skill" for s in skills)


def test_orchestrator_discover_skills_raises_when_dir_missing(tmp_path):
    from tools.exporter import ExportOrchestrator
    with pytest.raises(FileNotFoundError, match="skills/"):
        ExportOrchestrator(repo_root=tmp_path).discover_skills()


def test_orchestrator_skips_skill_without_frontmatter(tmp_path):
    from tools.exporter import ExportOrchestrator
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "bad.md").write_text("# No frontmatter", encoding="utf-8")
    assert len(ExportOrchestrator(repo_root=tmp_path).discover_skills()) == 0


def test_orchestrator_discovers_all_agents(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_agents_dir(tmp_path)
    agents = ExportOrchestrator(repo_root=tmp_path).discover_agents()
    assert len(agents) == 1
    assert agents[0].slug == "java_advanced_agent"


def test_orchestrator_skips_readme_in_agents(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_agents_dir(tmp_path)
    agents = ExportOrchestrator(repo_root=tmp_path).discover_agents()
    assert not any(a.slug.lower() == "readme" for a in agents)


def test_orchestrator_filter_skills_by_slug(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    filtered = orch.filter_skills(orch.discover_skills(), ["java"])
    assert len(filtered) == 1
    assert filtered[0].slug == "java_advanced_skill"


def test_orchestrator_filter_skills_empty_returns_all(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    all_skills = orch.discover_skills()
    assert orch.filter_skills(all_skills, []) == all_skills


def test_orchestrator_filter_agents_by_role(tmp_path):
    from tools.exporter import ExportOrchestrator
    agents_dir = tmp_path / "agents"
    (agents_dir / "developer").mkdir(parents=True)
    (agents_dir / "reviewer").mkdir(parents=True)
    (agents_dir / "developer" / "java_advanced_agent.md").write_text(AGENT_MD, encoding="utf-8")
    (agents_dir / "reviewer" / "code_review_agent.md").write_text(AGENT_MD, encoding="utf-8")
    orch = ExportOrchestrator(repo_root=tmp_path)
    filtered = orch.filter_agents(orch.discover_agents(), ["developer"])
    assert len(filtered) == 1
    assert filtered[0].role == "developer"


def test_orchestrator_run_writes_files_for_single_target(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    make_agents_dir(tmp_path)
    results = ExportOrchestrator(repo_root=tmp_path).run(
        targets=["claude"], skill_filter=[], agent_filter=[], dry_run=False
    )
    assert len(results) == 1
    assert results[0].target == "claude"
    assert (tmp_path / ".claude" / "skills" / "java_advanced_skill.md").exists()
    assert (tmp_path / ".claude" / "agents" / "java_advanced_agent.md").exists()


def test_orchestrator_run_dry_run_writes_nothing(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    make_agents_dir(tmp_path)
    ExportOrchestrator(repo_root=tmp_path).run(
        targets=["claude"], skill_filter=[], agent_filter=[], dry_run=True
    )
    assert not (tmp_path / ".claude").exists()


def test_orchestrator_clean_removes_export_dirs(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    make_agents_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    orch.run(targets=["claude"], skill_filter=[], agent_filter=[], dry_run=False)
    assert (tmp_path / ".claude").exists()
    orch.clean()
    assert not (tmp_path / ".claude" / "skills").exists()
    assert not (tmp_path / ".claude" / "agents").exists()


# ── CLI ───────────────────────────────────────────────────────────────────────

def test_resolve_repo_root_raises_when_no_skills_dir(tmp_path):
    from tools.exporter import resolve_repo_root
    with pytest.raises(SystemExit):
        resolve_repo_root(provided=tmp_path)


def test_resolve_repo_root_succeeds_with_skills_dir(tmp_path):
    from tools.exporter import resolve_repo_root
    (tmp_path / "skills").mkdir()
    assert resolve_repo_root(provided=tmp_path) == tmp_path


def test_build_argument_parser_defaults(tmp_path):
    from tools.exporter import build_argument_parser
    parser = build_argument_parser()
    args = parser.parse_args([])
    assert args.target == ["all"]
    assert args.skills == []
    assert args.agents == []
    assert args.dry_run is False
    assert args.clean is False
    assert args.list is False
