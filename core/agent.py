import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from core.skill_manager import SkillManager


def select_skill(query: str, manager: SkillManager) -> Optional[Dict]:
    """Use AI to select the most appropriate skill for the query."""

    # 1. Progressive Disclosure: Get partial metadata prompt
    skills_prompt = manager.get_skills_xml_prompt()

    # 2. Build Selection Prompt
    selection_prompt = f"""You are a task routing system. Analyze the user's request and select the most appropriate skill from the available skills below.

 {skills_prompt}

 Special hints for matching:
 - If user mentions "Python", "code", "script", "calculate", "program", "编程", "代码", "计算" → Select "monty-expert"
 - If user wants to write/execute Python code or perform calculations → Select "monty-expert"
 - If user needs multi-step data processing or data transformations → Select "monty-expert"
 - If user wants to combine multiple tools programmatically → Select "monty-expert"

 Your task:
 1. Analyze the user's request: "{query}"
 2. Select the ONE most appropriate skill that can handle this request.
 3. If NO skill matches, respond with: NO_MATCH

 Respond with ONLY the <name> of the skill (e.g., "yt-dlp-expert", "monty-expert") or "NO_MATCH"."""

    print("🤖 Analyzing request...")

    # 3. Call AI
    selected_name = try_ai_selection(selection_prompt)
    if not selected_name:
        return None

    print(f"🤔 AI Suggestion: {selected_name}")

    # 4. Handle Match
    if selected_name == "NO_MATCH":
        return None

    return manager.find_skill_by_name(selected_name)


def try_ai_selection(prompt: str) -> Optional[str]:
    """Try different AI services for skill selection."""

    # Try openai-compatible API first
    if "OPENAI_API_KEY" in os.environ or "OPENAI_BASE_URL" in os.environ:
        result = try_openai_api(prompt)
        if result:
            return result

    # Try local LLM
    try:
        import requests

        result = try_local_llm(prompt)
        if result:
            return result
    except ImportError:
        pass

    # Fallback: Ask user manually if AI fails completely (not if AI returns NO_MATCH)
    # For now, just return NO_MATCH to trigger remote search
    return "NO_MATCH"


def try_openai_api(prompt: str) -> Optional[str]:
    """Try using OpenAI-compatible API."""
    try:
        import openai

        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        client = openai.OpenAI(base_url=base_url)

        response = client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # print(f"⚠️  OpenAI API failed: {e}")
        return None


def try_local_llm(prompt: str) -> Optional[str]:
    """Try using local LLM via HTTP API."""
    try:
        import requests

        endpoints = [
            "http://localhost:1234/v1/chat/completions",
            "http://localhost:11434/api/chat",
            os.environ.get("LOCAL_LLM_URL", ""),
        ]

        for endpoint in endpoints:
            if not endpoint:
                continue
            try:
                response = requests.post(
                    endpoint,
                    json={"messages": [{"role": "user", "content": prompt}]},
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data:
                        return data["choices"][0]["message"]["content"].strip()
                    elif "message" in data:
                        return data["message"]["content"].strip()
            except requests.RequestException:
                continue
        return None
    except Exception:
        return None


def execute_via_tool(skill: Dict, query: str):
    """Route to tool's agent_client.py."""
    tool_dir = skill["tool_dir"]
    if not tool_dir:
        print(f"❌ Skill '{skill['name']}' has no executable tool.")
        return

    # Handle relative paths from registry
    if not tool_dir.startswith("/"):
        tool_path = root_dir / tool_dir / "agent_client.py"
    else:
        tool_path = Path(tool_dir) / "agent_client.py"

    if not tool_path.exists():
        print(f"❌ Tool script not found: {tool_path}")
        return

    print(f"\n🚀 Executing: {skill['name']}")
    print(f"   Script: {tool_path}")
    print(f"   Query: {query}")
    print()

    try:
        result = subprocess.run(
            [sys.executable, str(tool_path), query],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        # sys.exit(result.returncode) # Don't exit main process
    except Exception as e:
        print(f"❌ Execution failed: {e}")


def display_meta_skill_guidance(skill: Dict, query: str):
    """Display meta-skill instructions."""
    skill_md_path = skill["skill_md"]
    if not skill_md_path or not Path(skill_md_path).exists():
        print(f"❌ Skill file not found: {skill_md_path}")
        return

    print("\n" + "=" * 60)
    print(f"📚 {skill['name']} (Meta-Skill)")
    print(f"{'=' * 60}")
    print(f"Description: {skill['description']}")
    print("-" * 60)

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()
        if content.startswith("---"):
            content = content.split("---", 2)[-1]
        print(content)
    print("=" * 60)


def handle_remote_fallback(manager: SkillManager, query: str):
    """Handle case when no local skill is found."""
    print("\n🤷 No suitable local skill found.")
    print("🌐 Searching remote 'agentskills' repository...")

    remote_matches = manager.search_remote_skills(query)

    if not remote_matches:
        print("❌ No remote skills found matching your query.")
        return

    print(f"\n✨ Found {len(remote_matches)} potential remote skills:")
    for i, skill in enumerate(remote_matches, 1):
        print(f"  [{i}] {skill['name']}")
        print(f"      {skill['description']}")

    choice = input(
        "\n📥 Install and run one of these? (Enter number or 0 to cancel): "
    ).strip()
    try:
        idx = int(choice)
        if idx > 0 and idx <= len(remote_matches):
            selected = remote_matches[idx - 1]
            if manager.install_remote_skill(selected["name"]):
                # Refresh and run
                manager._skills_cache = None  # Clear cache
                new_skill = manager.find_skill_by_name(selected["name"])
                if new_skill:
                    if new_skill["type"] == "execution":
                        execute_via_tool(new_skill, query)
                    else:
                        display_meta_skill_guidance(new_skill, query)
    except ValueError:
        pass


def main():
    if len(sys.argv) < 2:
        print('Usage: python core/agent.py "your query"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    manager = SkillManager(root_dir)

    # 1. Try Local Selection
    skill = select_skill(query, manager)

    if skill:
        # 2. Execute Local
        if skill["type"] == "execution":
            execute_via_tool(skill, query)
        else:
            display_meta_skill_guidance(skill, query)
    else:
        # 3. Fallback to Remote
        handle_remote_fallback(manager, query)


if __name__ == "__main__":
    main()
