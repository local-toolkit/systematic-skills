#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Tool Script - Scaffolding for New Tools

Creates a new tool directory with proper structure based on tool type.

Usage:
    python scripts/create_tool.py <tool-name> --type subprocess|mcp|meta

Examples:
    python scripts/create_tool.py my-tool --type subprocess
    python scripts/create_tool.py my-mcp --type mcp
    python scripts/create_tool.py my-guide --type meta
"""

import argparse
import os
import sys
from pathlib import Path


def create_tool_directory(
    tool_name: str,
    tool_type: str,
    description: str = ""
) -> None:
    """
    Create a new tool directory with all necessary files.
    """
    root_dir = Path(__file__).parent.parent
    tool_dir = root_dir / "tools" / f"{tool_name}-tool"

    if tool_dir.exists():
        print(f"鉂?Tool directory already exists: {tool_dir}")
        sys.exit(1)

    # Create tool directory
    tool_dir.mkdir(parents=True, exist_ok=True)

    print(f"馃搧 Creating tool: {tool_dir}")
    print(f"   Type: {tool_type}")
    print()

    # Create skill directory
    skill_dir = root_dir / ".agent" / "skills" / f"{tool_name}-expert"
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Generate SKILL.md
    skill_md = skill_dir / "SKILL.md"
    with open(skill_md, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(f"name: {tool_name}-expert\n")
        f.write(f"description: \"{description}\"\n")
        f.write("---\n\n")
        f.write(f"# {tool_name.title()} Expert Skill\n\n")
        f.write("## Overview\n\n")
        f.write(f"Expert knowledge base for {tool_name} tool.\n")
        f.write("\n## Usage\n\n")
        f.write("See tool README for detailed usage instructions.\n")

    print(f"   鉁?{skill_md}")

    # Create templates.md
    templates_md = tool_dir / "templates.md"
    with open(templates_md, 'w', encoding='utf-8') as f:
        f.write(f"# {tool_name.title()} Command Templates\n\n")
        f.write("## Common Commands\n\n")
        f.write("### Example 1\n")
        f.write("```bash\n")
        f.write(f"python agent_client.py \"example command\"\n")
        f.write("```\n")
        f.write("\n### Example 2\n")
        f.write("```bash\n")
        f.write(f"python agent_client.py --action example --param1 value1\n")
        f.write("```\n")

    print(f"   鉁?{templates_md}")

    # Create README.md
    readme_md = tool_dir / "README.md"
    with open(readme_md, 'w', encoding='utf-8') as f:
        f.write(f"# {tool_name.title()} Tool\n\n")
        f.write(f"{description}\n\n")
        f.write("## Installation\n\n")
        f.write("```bash\n")
        f.write("pip install -r requirements.txt\n")
        f.write("```\n\n")
        f.write("## Usage\n\n")
        f.write("```bash\n")
        f.write(f"python agent_client.py \"<query>\"\n")
        f.write("```\n")

    print(f"   鉁?{readme_md}")

    # Create agent_client.py from template
    if tool_type == "subprocess":
        create_subprocess_agent_client(tool_dir, tool_name, description)
    elif tool_type == "mcp":
        create_mcp_agent_client(tool_dir, tool_name, description)
    elif tool_type == "meta":
        create_meta_agent_client(tool_dir, tool_name, description)
    else:
        print(f"鉂?Unknown tool type: {tool_type}")
        sys.exit(1)

    # Create requirements.txt
    requirements_txt = tool_dir / "requirements.txt"
    with open(requirements_txt, 'w', encoding='utf-8') as f:
        f.write("requests>=2.32.5,<3.0.0\n")
        if tool_type == "mcp":
            f.write("mcp>=0.9.0\n")

    print(f"   鉁?{requirements_txt}")

    # Create config directory
    config_dir = tool_dir / "config"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "config.yaml").touch()

    print(f"   鉁?{config_dir}")

    # Create reports directory
    reports_dir = tool_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    print(f"   鉁?{reports_dir}")

    print()
    print("鉁?Tool created successfully!")
    print()
    print(f"馃搧 Location: {tool_dir}")
    print()
    print("馃挕 Next steps:")
    print(f"  1. cd {tool_dir}")
    print("  2. Edit agent_client.py to implement tool logic")
    print("  3. If subprocess tool: Implement main.py")
    print("  4. If MCP tool: Implement mcp_server.py")
    print("  5. Register skill: python ../scripts/discover_skills.py")


def create_subprocess_agent_client(tool_dir: Path, tool_name: str, description: str) -> None:
    """Create agent_client.py for subprocess tools."""
    agent_client = tool_dir / "agent_client.py"
    with open(agent_client, 'w', encoding='utf-8') as f:
        f.write(f'#!/usr/bin/env python3\n')
        f.write(f'# -*- coding: utf-8 -*-\n')
        f.write(f'"""\n')
        f.write(f'{tool_name.title()} Tool Agent Client\n')
        f.write(f'"""\n')
        f.write(f'\n')
        f.write(f'import sys\n')
        f.write(f'import os\n')
        f.write(f'import json\n')
        f.write(f'import subprocess\n')
        f.write(f'from typing import Optional\n')
        f.write(f'\n')
        f.write(f'script_dir = os.path.dirname(os.path.abspath(__file__))\n')
        f.write(f'SKILL_PATH = os.path.join(os.path.dirname(script_dir), "../../.agent", "skills", "{tool_name}-expert", "SKILL.md")\n')
        f.write(f'TOOL_SCRIPT = os.path.join(script_dir, "main.py")\n')
        f.write(f'\n')
        f.write(f'def load_skill_context() -> str:\n')
        f.write(f'    """Load skill knowledge base."""\n')
        f.write(f'    try:\n')
        f.write(f'        with open(SKILL_PATH, \'r\', encoding=\'utf-8\') as f:\n')
        f.write(f'            return f.read()\n')
        f.write(f'    except Exception as e:\n')
        f.write('        print(f"Warning: Could not read SKILL.md: {e}")\n')
        f.write(f'        return ""\n')
        f.write(f'\n')
        f.write(f'def run_{tool_name.replace("-", "_")}_tool(**kwargs) -> str:\n')
        f.write(f'    """Execute {tool_name} tool with given arguments."""\n')
        f.write(f'    venv_python = os.path.join(script_dir, "venv", "bin", "python")\n')
        f.write(f'\n')
        f.write(f'    if os.path.exists(venv_python):\n')
        f.write(f'        python_exe = venv_python\n')
        f.write(f'    else:\n')
        f.write(f'        python_exe = sys.executable\n')
        f.write(f'\n')
        f.write(f'    cmd = [python_exe, TOOL_SCRIPT]\n')
        f.write(f'\n')
        f.write(f'    # Add arguments\n')
        f.write(f'    if kwargs.get("param"):\n')
        f.write(f'        cmd.extend(["--param", kwargs["param"]])\n')
        f.write(f'\n')
        f.write('    print(f"\\n馃殌 Executing: {\' \'.join(cmd)}")\n')
        f.write(f'    try:\n')
        f.write(f'        result = subprocess.run(cmd, capture_output=True, text=True, check=True)\n')
        f.write('        return f"SUCCESS:\\n{result.stdout}"\n')
        f.write(f'    except subprocess.CalledProcessError as e:\n')
        f.write('        return f"ERROR (Exit Code {e.returncode}):\\n{e.stderr}"\n')
        f.write(f'    except Exception as e:\n')
        f.write('        return f"EXECUTION FAILED: {str(e)}"\n')
        f.write(f'\n')
        f.write(f'def main():\n')
        f.write(f'    """Main entry point."""\n')
        f.write(f'    if len(sys.argv) < 2:\n')
        f.write(f'        print("Usage: python agent_client.py \\"<query>\\"")\n')
        f.write(f'        sys.exit(1)\n')
        f.write(f'\n')
        f.write(f'    query = " ".join(sys.argv[1:])\n')
        f.write(f'    run_{tool_name.replace("-", "_")}_tool()\n')
        f.write(f'\n')
        f.write(f'if __name__ == "__main__":\n')
        f.write(f'    main()\n')

    print(f"   鉁?{agent_client}")


def create_mcp_agent_client(tool_dir: Path, tool_name: str, description: str) -> None:
    """Create agent_client.py for MCP tools."""
    agent_client = tool_dir / "agent_client.py"
    with open(agent_client, 'w', encoding='utf-8') as f:
        f.write(f'#!/usr/bin/env python3\n')
        f.write(f'# -*- coding: utf-8 -*-\n')
        f.write(f'"""\n')
        f.write(f'{tool_name.title()} Tool Agent Client\n')
        f.write(f'"""\n')
        f.write(f'\n')
        f.write(f'import sys\n')
        f.write(f'import os\n')
        f.write(f'import asyncio\n')
        f.write(f'import json\n')
        f.write(f'from typing import Optional\n')
        f.write(f'\n')
        f.write(f'script_dir = os.path.dirname(os.path.abspath(__file__))\n')
        f.write(f'SKILL_PATH = os.path.join(os.path.dirname(script_dir), "../../.agent", "skills", "{tool_name}-expert", "SKILL.md")\n')
        f.write(f'MCP_SERVER_SCRIPT = os.path.join(script_dir, "mcp_server.py")\n')
        f.write(f'TEMPLATES_PATH = os.path.join(script_dir, "templates.md")\n')
        f.write(f'\n')
        f.write(f'def load_skill_context() -> str:\n')
        f.write(f'    """Load skill knowledge base."""\n')
        f.write(f'    try:\n')
        f.write(f'        with open(SKILL_PATH, \'r\', encoding=\'utf-8\') as f:\n')
        f.write(f'            return f.read()\n')
        f.write(f'    except Exception as e:\n')
        f.write('        print(f"Warning: Could not read SKILL.md: {e}")\n')
        f.write(f'        return ""\n')
        f.write(f'\n')
        f.write(f'from mcp_client import create_mcp_client\n')
        f.write(f'\n')
        f.write(f'def load_templates() -> str:\n')
        f.write(f'    """Load command templates."""\n')
        f.write(f'    try:\n')
        f.write(f'        with open(TEMPLATES_PATH, \'r\', encoding=\'utf-8\') as f:\n')
        f.write(f'            return f.read()\n')
        f.write(f'    except Exception as e:\n')
        f.write('        print(f"Warning: Could not read templates.md: {e}")\n')
        f.write(f'        return ""\n')
        f.write(f'\n')
        f.write(f'async def run_{tool_name.replace("-", "_")}_mcp_tool(action: str, **kwargs) -> str:\n')
        f.write(f'    """Execute {tool_name} MCP tools."""\n')
        f.write(f'    client = create_mcp_client(\n')
        f.write(f'        server_path=MCP_SERVER_SCRIPT,\n')
        f.write(f'        server_name="{tool_name}-mcp",\n')
        f.write(f'        is_external=False\n')
        f.write(f'    )\n')
        f.write(f'\n')
        f.write(f'    try:\n')
        f.write(f'        result = await client.call_tool(action, **kwargs)\n')
        f.write(f'        return result\n')
        f.write(f'    except Exception as e:\n')
        f.write('        return f"ERROR: {str(e)}"\n')
        f.write(f'\n')
        f.write(f'def main():\n')
        f.write(f'    """Main entry point."""\n')
        f.write(f'    if len(sys.argv) < 2:\n')
        f.write(f'        print("Usage: python agent_client.py \\"<query>\\"")\n')
        f.write(f'        sys.exit(1)\n')
        f.write(f'\n')
        f.write(f'    query = " ".join(sys.argv[1:])\n')
        f.write(f'    loop = asyncio.new_event_loop()\n')
        f.write(f'    loop.run_until_complete(run_{tool_name.replace("-", "_")}_mcp_tool(query))\n')
        f.write(f'\n')
        f.write(f'if __name__ == "__main__":\n')
        f.write(f'    main()\n')

    print(f"   鉁?{agent_client}")


def create_meta_agent_client(tool_dir: Path, tool_name: str, description: str) -> None:
    """Create agent_client.py for meta skills."""
    agent_client = tool_dir / "agent_client.py"
    with open(agent_client, 'w', encoding='utf-8') as f:
        f.write(f'#!/usr/bin/env python3\n')
        f.write(f'# -*- coding: utf-8 -*-\n')
        f.write(f'"""\n')
        f.write(f'{tool_name.title()} Meta Skill\n')
        f.write(f'"""\n')
        f.write(f'\n')
        f.write(f'import sys\n')
        f.write(f'import os\n')
        f.write(f'\n')
        f.write(f'script_dir = os.path.dirname(os.path.abspath(__file__))\n')
        f.write(f'SKILL_PATH = os.path.join(os.path.dirname(script_dir), "../../.agent", "skills", "{tool_name}-expert", "SKILL.md")\n')
        f.write(f'\n')
        f.write(f'def main():\n')
        f.write(f'    """Display skill knowledge base."""\n')
        f.write(f'    try:\n')
        f.write(f'        with open(SKILL_PATH, \'r\', encoding=\'utf-8\') as f:\n')
        f.write(f'            content = f.read()\n')
        f.write(f'            # Skip frontmatter\n')
        f.write(f'            if content.startswith(\'---\'):\n')
        f.write(f'                content = content.split(\'---\', 2)[-1]\n')
        f.write(f'            print(content)\n')
        f.write(f'    except Exception as e:\n')
        f.write(f'        print(f"Error: {e}")\n')
        f.write(f'        sys.exit(1)\n')
        f.write(f'\n')
        f.write(f'if __name__ == "__main__":\n')
        f.write(f'    main()\n')

    print(f"   鉁?{agent_client}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a new tool directory",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("tool_name", help="Tool name (e.g., my-tool)")
    parser.add_argument(
        "--type",
        choices=["subprocess", "mcp", "meta"],
        default="subprocess",
        help="Tool type: subprocess (simple), mcp (MCP server), or meta (guidance only)"
    )
    parser.add_argument(
        "--description",
        default="",
        help="Tool description"
    )

    args = parser.parse_args()

    if not args.tool_name:
        parser.print_help()
        sys.exit(1)

    create_tool_directory(
        tool_name=args.tool_name,
        tool_type=args.type,
        description=args.description
    )


if __name__ == "__main__":
    main()
