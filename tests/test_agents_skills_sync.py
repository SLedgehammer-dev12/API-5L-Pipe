"""Tests for verifying Antigravity and OpenCode agents and skills synchronization and validity."""

import os
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
OPENCODE_DIR = os.path.join(ROOT_DIR, ".opencode")

EXPECTED_AGENTS = {
    "feature-scout.md",
    "improver.md",
    "perf-analyst.md",
    "ponytail-reviewer.md",
    "qa-auditor.md",
    "refactor-architect.md",
    "ux-reviewer.md",
    "verifier.md",
}

EXPECTED_SKILLS = {
    "improvement-loop",
    "ponytail",
    "ponytail-audit",
    "ponytail-debt",
    "ponytail-gain",
    "ponytail-help",
    "ponytail-review",
    "stageshow",
}


def parse_frontmatter(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content.startswith("---"), f"{file_path} must start with YAML frontmatter"
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{file_path} must have closed YAML frontmatter"
    frontmatter_raw = parts[1]
    return frontmatter_raw, parts[2]


def test_agents_dual_directory_presence():
    """Verify that all expected agents exist in both .agents/agents and .opencode/agent."""
    ag_agents_dir = os.path.join(AGENTS_DIR, "agents")
    oc_agents_dir = os.path.join(OPENCODE_DIR, "agent")

    assert os.path.isdir(ag_agents_dir), ".agents/agents directory must exist"
    assert os.path.isdir(oc_agents_dir), ".opencode/agent directory must exist"

    ag_files = set(f for f in os.listdir(ag_agents_dir) if f.endswith(".md"))
    oc_files = set(f for f in os.listdir(oc_agents_dir) if f.endswith(".md"))

    assert EXPECTED_AGENTS.issubset(ag_files), f"Missing in .agents/agents: {EXPECTED_AGENTS - ag_files}"
    assert EXPECTED_AGENTS.issubset(oc_files), f"Missing in .opencode/agent: {EXPECTED_AGENTS - oc_files}"


def test_agents_content_and_frontmatter_parity():
    """Verify agent frontmatter requirements (name, description) and parity between directories."""
    ag_agents_dir = os.path.join(AGENTS_DIR, "agents")
    oc_agents_dir = os.path.join(OPENCODE_DIR, "agent")

    for agent_file in EXPECTED_AGENTS:
        ag_path = os.path.join(ag_agents_dir, agent_file)
        oc_path = os.path.join(oc_agents_dir, agent_file)

        ag_fm, ag_body = parse_frontmatter(ag_path)
        oc_fm, oc_body = parse_frontmatter(oc_path)

        assert "name:" in ag_fm, f"{ag_path} must define 'name:' in frontmatter"
        assert "description:" in ag_fm, f"{ag_path} must define 'description:' in frontmatter"
        assert "name:" in oc_fm, f"{oc_path} must define 'name:' in frontmatter"
        assert "description:" in oc_fm, f"{oc_path} must define 'description:' in frontmatter"

        # Validate color format if present (OpenCode requirement: ^#[0-9a-fA-F]{6}$ or enum)
        import re
        color_regex = re.compile(r'^#[0-9a-fA-F]{6}$')
        valid_color_enums = {"primary", "secondary", "accent", "success", "warning", "error", "info"}
        for line in ag_fm.splitlines():
            if line.strip().startswith("color:"):
                val = line.split("color:", 1)[1].strip().strip('"').strip("'")
                assert color_regex.match(val) or val in valid_color_enums, f"Invalid color '{val}' in {ag_path}"

        # Content parity
        with open(ag_path, "r", encoding="utf-8") as f1, open(oc_path, "r", encoding="utf-8") as f2:
            assert f1.read() == f2.read(), f"{agent_file} differs between Antigravity and OpenCode directories"


def test_skills_dual_directory_presence_and_validity():
    """Verify skills exist in .agents/skills and .opencode/skill with valid SKILL.md."""
    ag_skills_dir = os.path.join(AGENTS_DIR, "skills")
    oc_skills_dir = os.path.join(OPENCODE_DIR, "skill")

    assert os.path.isdir(ag_skills_dir), ".agents/skills must exist"
    assert os.path.isdir(oc_skills_dir), ".opencode/skill must exist"

    ag_skills = set(os.listdir(ag_skills_dir))
    oc_skills = set(os.listdir(oc_skills_dir))

    assert EXPECTED_SKILLS.issubset(ag_skills), f"Missing skills in .agents/skills: {EXPECTED_SKILLS - ag_skills}"
    assert EXPECTED_SKILLS.issubset(oc_skills), f"Missing skills in .opencode/skill: {EXPECTED_SKILLS - oc_skills}"

    for skill in EXPECTED_SKILLS:
        ag_skill_file = os.path.join(ag_skills_dir, skill, "SKILL.md")
        oc_skill_file = os.path.join(oc_skills_dir, skill, "SKILL.md")

        assert os.path.isfile(ag_skill_file), f"Missing {ag_skill_file}"
        assert os.path.isfile(oc_skill_file), f"Missing {oc_skill_file}"

        ag_fm, _ = parse_frontmatter(ag_skill_file)
        oc_fm, _ = parse_frontmatter(oc_skill_file)

        assert "name:" in ag_fm
        assert "description:" in ag_fm
        assert "name:" in oc_fm
        assert "description:" in oc_fm


def test_opencode_json_config():
    """Verify .opencode/opencode.json configuration."""
    config_path = os.path.join(OPENCODE_DIR, "opencode.json")
    assert os.path.isfile(config_path), ".opencode/opencode.json must exist"

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    assert cfg.get("default_agent") == "improver"
    assert "AGENTS.md" in cfg.get("instructions", [])
    assert "@dietrichgebert/ponytail" in cfg.get("plugin", [])
