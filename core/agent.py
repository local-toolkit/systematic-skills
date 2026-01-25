import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

def load_skill_registry() -> List[Dict]:
    """Load skill registry from JSON file."""
    root_dir = Path(__file__).parent.parent
    registry_path = root_dir / ".agent" / "skill_registry.json"
    
    if not registry_path.exists():
        print("❌ Skill registry not found. Run: python scripts/discover_skills.py")
        sys.exit(1)
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def select_skill(query: str, skills: List[Dict]) -> Optional[Dict]:
    """Use AI to select the most appropriate skill for the query."""
    
    # Build skill descriptions for AI context
    skill_descriptions = []
    for skill in skills:
        desc = f"- {skill['name']}: {skill['description']}"
        if skill['type'] == 'execution':
            desc += f" (tool: {skill['tool_dir']})"
        else:
            desc += " (meta-skill: provides guidance only)"
        skill_descriptions.append(desc)
    
    skills_text = "\n".join(skill_descriptions)
    
    # Build AI prompt for skill selection
    selection_prompt = f"""You are a task routing system. Analyze the user's request and select the most appropriate skill.

Available skills:
{skills_text}

Your task:
1. Analyze the user's request: "{query}"
2. Select the ONE most appropriate skill that can handle this request
3. If NO skill matches, respond with: NO_MATCH
4. If multiple skills could match, select the MOST SUITABLE one (prefer execution skills over meta-skills when possible)

Respond with ONLY the skill name (e.g., "yt-dlp-expert") or "NO_MATCH"."""
    
    print("🤖 Analyzing your request to select the appropriate skill...")
    
    # Try to use different AI services in order of preference
    selected_skill = try_ai_selection(selection_prompt, skills)
    
    return selected_skill

def try_ai_selection(prompt: str, skills: List[Dict]) -> Optional[Dict]:
    """Try different AI services for skill selection."""
    
    # Try openai-compatible API first (check for OPENAI_API_KEY)
    if 'OPENAI_API_KEY' in os.environ or 'OPENAI_BASE_URL' in os.environ:
        result = try_openai_api(prompt)
        if result:
            return find_skill_by_name(result, skills)
    
    # Try to import and use local LLM libraries
    try:
        import requests
        result = try_local_llm(prompt)
        if result:
            return find_skill_by_name(result, skills)
    except ImportError:
        pass
    
    # Fallback: Ask user to select
    return ask_user_to_select(prompt, skills)

def try_openai_api(prompt: str) -> Optional[str]:
    """Try using OpenAI-compatible API."""
    try:
        import openai
        base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        client = openai.OpenAI(base_url=base_url)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️  OpenAI API failed: {e}")
        return None

def try_local_llm(prompt: str) -> Optional[str]:
    """Try using local LLM via HTTP API."""
    try:
        import requests
        
        # Try common local LLM endpoints
        endpoints = [
            "http://localhost:1234/v1/chat/completions",
            "http://localhost:11434/api/chat",
            os.environ.get('LOCAL_LLM_URL', '')
        ]
        
        for endpoint in endpoints:
            if not endpoint:
                continue
            
            try:
                response = requests.post(
                    endpoint,
                    json={"messages": [{"role": "user", "content": prompt}]},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Handle different response formats
                    if 'choices' in data:
                        return data['choices'][0]['message']['content'].strip()
                    elif 'message' in data:
                        return data['message']['content'].strip()
            except requests.RequestException:
                continue
        
        return None
    except Exception as e:
        return None

def find_skill_by_name(name: str, skills: List[Dict]) -> Optional[Dict]:
    """Find skill by name in registry."""
    if name == "NO_MATCH":
        return None
    
    for skill in skills:
        if skill['name'] == name or skill['function_name'] == name:
            return skill
    
    return None

def ask_user_to_select(prompt: str, skills: List[Dict]) -> Optional[Dict]:
    """Ask user to manually select the skill."""
    print("\n" + "="*60)
    print("🤔 Could not automatically determine the best skill.")
    print("Please select a skill manually:")
    print()
    
    for i, skill in enumerate(skills, 1):
        print(f"  [{i}] {skill['name']}")
        print(f"      {skill['description']}")
        if skill['type'] == 'execution':
            print(f"      → Will execute via {skill['tool_dir']}/agent_client.py")
        else:
            print(f"      → Will display guidance and instructions")
        print()
    
    print("  [0] Cancel")
    print("="*60)
    
    try:
        choice = input("Enter your choice (number): ").strip()
        choice_idx = int(choice)
        
        if choice_idx == 0:
            return None
        
        if 1 <= choice_idx <= len(skills):
            return skills[choice_idx - 1]
        
        print("❌ Invalid choice.")
        return None
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Cancelled.")
        return None

def execute_via_tool(skill: Dict, query: str):
    """Route to tool's agent_client.py."""
    tool_dir = skill['tool_dir']
    root_dir = Path(__file__).parent.parent
    tool_path = root_dir / tool_dir / "agent_client.py"
    
    if not tool_path.exists():
        print(f"❌ Tool not found: {tool_path}")
        return
    
    print(f"\n🚀 Routing to: {tool_dir}/agent_client.py")
    print(f"📝 Query: {query}")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, str(tool_path), query],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        sys.exit(result.returncode)
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        sys.exit(1)

def display_meta_skill_guidance(skill: Dict, query: str):
    """Display meta-skill instructions and guidance."""
    skill_md_path = skill['skill_md']
    
    if not skill_md_path or not Path(skill_md_path).exists():
        print(f"❌ Skill file not found: {skill_md_path}")
        return
    
    print("\n" + "="*60)
    print(f"📚 {skill['name']}")
    print(f"{'='*60}")
    print()
    print(f"Your request: {query}")
    print()
    print(f"Description: {skill['description']}")
    print()
    print("-"*60)
    print("📖 Skill Knowledge Base:")
    print("-"*60)
    
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Skip YAML frontmatter if present
        if content.startswith('---'):
            content = content.split('---', 2)[-1]
        print(content)
    
    print()
    print("="*60)

def main():
    """Main entry point for unified agent."""
    
    if len(sys.argv) < 2:
        print("🤖 Unified Agent - Single Entry Point for All Tools")
        print()
        print("Usage:")
        print(f"  {sys.argv[0]} \"<your request>\"")
        print()
        print("Examples:")
        print(f"  {sys.argv[0]} \"下载这个视频 https://www.youtube.com/watch?v=xxx\"")
        print(f"  {sys.argv[0]} \"Create a new MCP server for GitHub API\"")
        print(f"  {sys.argv[0]} \"Help me develop a tool for literature search\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    # Load skill registry
    skills = load_skill_registry()
    print(f"📋 Loaded {len(skills)} skill(s)")
    
    # Select appropriate skill
    selected_skill = select_skill(query, skills)
    
    if not selected_skill:
        print("\n❌ No suitable skill found for your request.")
        print("💡 Tip: Run 'python scripts/discover_skills.py' to see all available skills")
        print("💡 Or add a new skill for this task")
        sys.exit(1)
    
    print(f"✅ Selected skill: {selected_skill['name']}")
    
    # Execute or display guidance
    if selected_skill['type'] == 'execution':
        execute_via_tool(selected_skill, query)
    else:
        display_meta_skill_guidance(selected_skill, query)

if __name__ == "__main__":
    main()
