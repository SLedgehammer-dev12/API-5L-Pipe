#!/usr/bin/env python3
"""Sync Ponytail (https://github.com/DietrichGebert/ponytail) into OpenCode and Antigravity.

Usage:
    python tools/sync_ponytail.py
"""

import os
import shutil
import subprocess
import sys
import tempfile

REPO_URL = "https://github.com/DietrichGebert/ponytail.git"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SKILLS = [
    "ponytail",
    "ponytail-review",
    "ponytail-audit",
    "ponytail-debt",
    "ponytail-gain",
    "ponytail-help",
]

COMMANDS = [
    "ponytail.md",
    "ponytail-review.md",
    "ponytail-audit.md",
    "ponytail-debt.md",
    "ponytail-gain.md",
    "ponytail-help.md",
]


def sync_ponytail(source_dir: str):
    print(f"Syncing Ponytail from {source_dir}...")

    # 1. Sync Antigravity skills (.agents/skills)
    agents_skills_dir = os.path.join(ROOT_DIR, ".agents", "skills")
    os.makedirs(agents_skills_dir, exist_ok=True)
    for skill in SKILLS:
        src = os.path.join(source_dir, "skills", skill)
        dst = os.path.join(agents_skills_dir, skill)
        if os.path.exists(src):
            os.makedirs(dst, exist_ok=True)
            shutil.copy2(os.path.join(src, "SKILL.md"), os.path.join(dst, "SKILL.md"))
            print(f"  [Antigravity Skill] -> .agents/skills/{skill}/SKILL.md")

    # 2. Sync Antigravity rules (.agents/rules/ponytail.md)
    agents_rules_dir = os.path.join(ROOT_DIR, ".agents", "rules")
    os.makedirs(agents_rules_dir, exist_ok=True)
    agents_rule_src = os.path.join(source_dir, "AGENTS.md")
    if os.path.exists(agents_rule_src):
        shutil.copy2(agents_rule_src, os.path.join(agents_rules_dir, "ponytail.md"))
        print("  [Antigravity Rule]  -> .agents/rules/ponytail.md")

    # 3. Sync OpenCode skills (.opencode/skill)
    opencode_skills_dir = os.path.join(ROOT_DIR, ".opencode", "skill")
    os.makedirs(opencode_skills_dir, exist_ok=True)
    for skill in SKILLS:
        src = os.path.join(source_dir, "skills", skill)
        dst = os.path.join(opencode_skills_dir, skill)
        if os.path.exists(src):
            os.makedirs(dst, exist_ok=True)
            shutil.copy2(os.path.join(src, "SKILL.md"), os.path.join(dst, "SKILL.md"))
            print(f"  [OpenCode Skill]    -> .opencode/skill/{skill}/SKILL.md")

    # 4. Sync OpenCode commands (.opencode/command)
    opencode_cmd_dir = os.path.join(ROOT_DIR, ".opencode", "command")
    os.makedirs(opencode_cmd_dir, exist_ok=True)
    for cmd in COMMANDS:
        src = os.path.join(source_dir, ".opencode", "command", cmd)
        dst = os.path.join(opencode_cmd_dir, cmd)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  [OpenCode Command]  -> .opencode/command/{cmd}")

    # 5. Sync ponytail-reviewer agent to both Antigravity and OpenCode
    agents_agents_dir = os.path.join(ROOT_DIR, ".agents", "agents")
    opencode_agent_dir = os.path.join(ROOT_DIR, ".opencode", "agent")
    os.makedirs(agents_agents_dir, exist_ok=True)
    os.makedirs(opencode_agent_dir, exist_ok=True)
    reviewer_filename = "ponytail-reviewer.md"
    # Source might be in source_dir/.opencode/agent or existing
    src_reviewer = os.path.join(source_dir, ".opencode", "agent", reviewer_filename)
    if os.path.exists(src_reviewer):
        shutil.copy2(src_reviewer, os.path.join(agents_agents_dir, reviewer_filename))
        shutil.copy2(src_reviewer, os.path.join(opencode_agent_dir, reviewer_filename))
        print("  [Agent Dual Sync]   -> .agents/agents & .opencode/agent ponytail-reviewer.md")

    print("Sync completed successfully.")


def main():
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        sync_ponytail(sys.argv[1])
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        clone_dir = os.path.join(tmp_dir, "ponytail")
        print(f"Cloning latest Ponytail from {REPO_URL}...")
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, clone_dir], check=True)
        sync_ponytail(clone_dir)


if __name__ == "__main__":
    main()
