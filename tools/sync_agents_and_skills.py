#!/usr/bin/env python3
"""Sync and verify agents and skills between Antigravity and OpenCode directories.

Usage:
    python tools/sync_agents_and_skills.py --check
    python tools/sync_agents_and_skills.py --sync
"""

import argparse
import os
import shutil
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")
AGENTS_SKILLS_DIR = os.path.join(ROOT_DIR, ".agents", "skills")
OPENCODE_AGENT_DIR = os.path.join(ROOT_DIR, ".opencode", "agent")
OPENCODE_SKILL_DIR = os.path.join(ROOT_DIR, ".opencode", "skill")


def check_frontmatter(file_path: str, required_fields=("name", "description")) -> list:
    """Validate that markdown file begins with YAML frontmatter containing required fields."""
    issues = []
    if not os.path.exists(file_path):
        return [f"File missing: {file_path}"]

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return [f"Missing YAML frontmatter opening in {file_path}"]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return [f"Unclosed YAML frontmatter in {file_path}"]

    frontmatter = parts[1]
    for field in required_fields:
        if f"{field}:" not in frontmatter:
            issues.append(f"Missing required '{field}:' in frontmatter of {file_path}")

    # OpenCode color validator: hex ^#[0-9a-fA-F]{6}$ or enum
    import re
    color_regex = re.compile(r'^#[0-9a-fA-F]{6}$')
    valid_color_enums = {"primary", "secondary", "accent", "success", "warning", "error", "info"}
    for line in frontmatter.splitlines():
        if line.strip().startswith("color:"):
            val = line.split("color:", 1)[1].strip().strip('"').strip("'")
            if not (color_regex.match(val) or val in valid_color_enums):
                issues.append(f"Invalid 'color: {val}' in {file_path}. Must match ^#[0-9a-fA-F]{{6}}$ or one of {sorted(valid_color_enums)}")

    return issues


def sync_files(source_dir: str, target_dir: str, label: str) -> int:
    """Sync files from source_dir to target_dir."""
    if not os.path.exists(source_dir):
        return 0

    os.makedirs(target_dir, exist_ok=True)
    count = 0
    for root, _, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        dest_root = os.path.join(target_dir, rel_path) if rel_path != "." else target_dir
        os.makedirs(dest_root, exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dest_file = os.path.join(dest_root, f)
            if not os.path.exists(dest_file) or open(src_file, "rb").read() != open(dest_file, "rb").read():
                shutil.copy2(src_file, dest_file)
                print(f"  [Synced {label}] {os.path.relpath(dest_file, ROOT_DIR)}")
                count += 1
    return count


def verify_all() -> bool:
    """Check parity and frontmatter compliance between Antigravity and OpenCode."""
    all_ok = True
    print("Checking Antigravity <-> OpenCode agents and skills parity...\n")

    # 1. Agents check
    agent_files_ag = sorted(os.listdir(AGENTS_AGENTS_DIR)) if os.path.exists(AGENTS_AGENTS_DIR) else []
    agent_files_oc = sorted(os.listdir(OPENCODE_AGENT_DIR)) if os.path.exists(OPENCODE_AGENT_DIR) else []

    print(f"Antigravity Agents (.agents/agents): {len(agent_files_ag)} files")
    print(f"OpenCode Agents (.opencode/agent):   {len(agent_files_oc)} files")

    missing_in_ag = set(agent_files_oc) - set(agent_files_ag)
    missing_in_oc = set(agent_files_ag) - set(agent_files_oc)

    if missing_in_ag:
        print(f"  ERROR: Missing in Antigravity (.agents/agents): {missing_in_ag}")
        all_ok = False
    if missing_in_oc:
        print(f"  ERROR: Missing in OpenCode (.opencode/agent): {missing_in_oc}")
        all_ok = False

    # Check agent frontmatter in both
    for ag in agent_files_ag:
        if ag.endswith(".md"):
            ag_path = os.path.join(AGENTS_AGENTS_DIR, ag)
            issues = check_frontmatter(ag_path)
            for iss in issues:
                print(f"  [AG Agent Warning] {iss}")
                all_ok = False

    for oc in agent_files_oc:
        if oc.endswith(".md"):
            oc_path = os.path.join(OPENCODE_AGENT_DIR, oc)
            issues = check_frontmatter(oc_path)
            for iss in issues:
                print(f"  [OC Agent Warning] {iss}")
                all_ok = False

    # 2. Skills check
    skills_ag = sorted(os.listdir(AGENTS_SKILLS_DIR)) if os.path.exists(AGENTS_SKILLS_DIR) else []
    skills_oc = sorted(os.listdir(OPENCODE_SKILL_DIR)) if os.path.exists(OPENCODE_SKILL_DIR) else []

    print(f"\nAntigravity Skills (.agents/skills): {len(skills_ag)} skills")
    print(f"OpenCode Skills (.opencode/skill):   {len(skills_oc)} skills")

    missing_skills_ag = set(skills_oc) - set(skills_ag)
    missing_skills_oc = set(skills_ag) - set(skills_oc)

    if missing_skills_ag:
        print(f"  ERROR: Skills missing in Antigravity: {missing_skills_ag}")
        all_ok = False
    if missing_skills_oc:
        print(f"  ERROR: Skills missing in OpenCode: {missing_skills_oc}")
        all_ok = False

    for s in skills_ag:
        skill_file = os.path.join(AGENTS_SKILLS_DIR, s, "SKILL.md")
        issues = check_frontmatter(skill_file)
        for iss in issues:
            print(f"  [Skill Warning] {iss}")
            all_ok = False

    if all_ok:
        print("\nAll agents and skills are 100% synchronized and compatible between Antigravity and OpenCode!")
    else:
        print("\nSome discrepancies found. Run `python tools/sync_agents_and_skills.py --sync` to synchronize.")

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Sync and verify Antigravity/OpenCode agents and skills")
    parser.add_argument("--sync", action="store_true", help="Synchronize agents and skills bidirectionally")
    parser.add_argument("--check", action="store_true", help="Check parity and validation")
    args = parser.parse_args()

    if args.sync or not args.check:
        print("Synchronizing agents and skills...")
        # Bidirectional sync: union
        sync_files(OPENCODE_AGENT_DIR, AGENTS_AGENTS_DIR, "Agent -> Antigravity")
        sync_files(AGENTS_AGENTS_DIR, OPENCODE_AGENT_DIR, "Agent -> OpenCode")
        sync_files(OPENCODE_SKILL_DIR, AGENTS_SKILLS_DIR, "Skill -> Antigravity")
        sync_files(AGENTS_SKILLS_DIR, OPENCODE_SKILL_DIR, "Skill -> OpenCode")

    success = verify_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
