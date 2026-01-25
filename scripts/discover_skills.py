#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discover Skills Script - Enhanced with Tool Type Detection

Automatically discovers and registers all skills from .agent/skills/ directory.
Now detects tool types: subprocess, mcp, or meta.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


def detect_tool_type(tool_dir: Path) -> Dict[str, bool]:
    """
    Detect the integration type of a tool by examining its files.

    Returns dictionary with detection results.
    """
    detection = {
        "has_main": False,
        "has_mcp_server": False,
        "is_subprocess_tool": False,
        "is_mcp_tool": False,
        "is_meta_skill": False,
        "integration": "unknown",
        "has_agent_client": False
    }

    # Check for agent_client.py (execution tools only)
    agent_client = tool_dir / "agent_client.py"
    detection["has_agent_client"] = agent_client.exists()

    # Check for main.py (subprocess tools)
    main_py = tool_dir / "main.py"
    detection["has_main"] = main_py.exists()

    # Check for mcp_server.py (MCP tools)
    mcp_server_py = tool_dir / "mcp_server.py"
    detection["has_mcp_server"] = mcp_server_py.exists()

    # Check for external MCP (TrendRadar pattern)
    trendradar_mcp = tool_dir / "trendradar-mcp"
    detection["has_external_mcp"] = trendradar_mcp.is_symlink() or trendradar_mcp.is_dir()

    # Determine tool type
    if not detection["has_agent_client"]:
        # Meta skill - no agent_client.py
        detection["integration"] = "meta"
        detection["is_meta_skill"] = True
    elif detection["has_mcp_server"]:
        # MCP server tool
        detection["integration"] = "mcp"
        detection["is_mcp_tool"] = True
    elif detection["has_external_mcp"]:
        # External MCP tool
        detection["integration"] = "mcp"
        detection["is_mcp_tool"] = True
        detection["is_external"] = True
    elif detection["has_main"]:
        # Subprocess tool
        detection["integration"] = "subprocess"
        detection["is_subprocess_tool"] = True
    else:
        detection["integration"] = "none"

    return detection


def discover_skills() -> List[Dict]:
    """
    Discover all skills from .agent/skills/ directory.

    Returns list of skill registry entries.
    """
    root_dir = Path(__file__).parent.parent
    skills_dir = root_dir / ".agent" / "skills"

    if not skills_dir.exists():
        print(f"❌ Skills directory not found: {skills_dir}")
        sys.exit(1)

    skills = []

    print("🔍 Discovering skills...")
    print()

    # Discover all skill directories
    for skill_path in sorted(skills_dir.iterdir()):
        if not skill_path.is_dir():
            continue

        skill_name = skill_path.name
        skill_md = skill_path / "SKILL.md"

        if not skill_md.exists():
            print(f"⚠️  Skipping {skill_name} (no SKILL.md)")
            continue

        # Read skill name from SKILL.md frontmatter
        function_name = skill_name.replace("-expert", "")
        description = ""
        tool_type = "meta"

        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract frontmatter
                if content.startswith('---'):
                    lines = content.split('\n')
                    for line in lines[1:]:
                        if line.startswith('name:'):
                            function_name = line.split(':')[1].strip().strip('"')
                        elif line.startswith('description:'):
                            description = line.split(':', 1)[1].strip().strip('"')
                        elif line == '---':
                            break
        except Exception as e:
            print(f"⚠️  Warning reading {skill_name}: {e}")

        # Determine tool directory
        tool_dir_guess = function_name + "-tool"
        
        # New: Search for tool in the 'tools' subdirectory
        tools_parent_dir = root_dir / "tools"
        tool_path = tools_parent_dir / tool_dir_guess
        
        # Fallback to root for legacy or non-standard tools
        if not tool_path.exists():
            tool_path = root_dir / tool_dir_guess
            tool_dir_path_for_registry = tool_dir_guess
        else:
            tool_dir_path_for_registry = f"tools/{tool_dir_guess}"

        # Detect integration type
        detection = detect_tool_type(tool_path)
        integration = detection["integration"]

        # Determine if execution or meta
        type_flag = "execution" if detection["has_agent_client"] else "meta"

        # Create registry entry
        skill_entry = {
            "name": skill_name,
            "function_name": function_name,
            "tool_dir": tool_dir_path_for_registry if tool_path.exists() else None,
            "type": type_flag,
            "integration": integration,
            "description": description,
            "status": "active",
            "path": str(skill_path),
            "skill_md": str(skill_md),
            # New fields for enhanced registry
            "has_main": detection["has_main"],
            "has_mcp_server": detection["has_mcp_server"],
            "is_external": detection.get("is_external", False)
        }

        skills.append(skill_entry)

        # Print discovery info
        type_icon = {
            "subprocess": "🔧",
            "mcp": "🌐",
            "meta": "📚",
            "none": "❓"
        }.get(integration, "❓")

        print(f"{type_icon} {skill_name}")
        print(f"   Type: {integration}")
        print(f"   Dir: {tool_dir_guess if tool_path.exists() else 'N/A'}")
        print()

    return skills


def save_registry(skills: List[Dict]) -> None:
    """Save skill registry to JSON file."""
    root_dir = Path(__file__).parent.parent
    registry_path = root_dir / ".agent" / "skill_registry.json"

    # Create .agent directory if needed
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    # Save with pretty formatting
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(skills, f, indent=2, ensure_ascii=False)

    print(f"✅ Registry saved to: {registry_path}")
    print(f"📊 Total skills: {len(skills)}")


def print_summary(skills: List[Dict]) -> None:
    """Print summary of discovered skills."""
    print("=" * 60)
    print("📊 SKILL DISCOVERY SUMMARY")
    print("=" * 60)
    print()

    # Count by type
    type_counts = {
        "execution": 0,
        "meta": 0
    }

    integration_counts = {
        "subprocess": 0,
        "mcp": 0,
        "meta": 0
    }

    for skill in skills:
        type_counts[skill["type"]] += 1
        integration = skill.get("integration", "unknown")
        if integration in integration_counts:
            integration_counts[integration] += 1

    print("📈 By Type:")
    print(f"  🔧 Execution: {type_counts['execution']} skills")
    print(f"  📚 Meta: {type_counts['meta']} skills")
    print()

    print("📈 By Integration:")
    print(f"  🛠️  Subprocess: {integration_counts['subprocess']} skills")
    print(f"  🌐 MCP: {integration_counts['mcp']} skills")
    print(f"  📚 Meta: {integration_counts['meta']} skills")
    print()

    print("=" * 60)


def main():
    """Main entry point."""
    print("🔍 Skill Discovery Tool - Enhanced")
    print()

    # Discover skills
    skills = discover_skills()

    # Save registry
    save_registry(skills)

    # Print summary
    print_summary(skills)

    print()
    print("✅ Discovery complete!")
    print()
    print("💡 Next steps:")
    print("  1. Test skill routing: python agent.py \"test query\"")
    print("  2. Check registry: cat .agent/skill_registry.json")
    print()


if __name__ == "__main__":
    main()
