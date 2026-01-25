import os
import json
import re
from pathlib import Path
from typing import List, Dict

def load_skill_registry() -> List[Dict]:
    """Load skill registry from JSON file."""
    root_dir = Path(__file__).parent.parent
    registry_path = root_dir / ".agent" / "skill_registry.json"
    
    if not registry_path.exists():
        print("❌ Skill registry not found. Run: python scripts/discover_skills.py")
        return []
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_markdown_table(skills: List[Dict]) -> str:
    """Generate markdown table from skill registry."""
    if not skills:
        return "| Skill Name | Tool Directory | Description | Status |\n|-----------|---------------|-------------|--------|"
    
    table = "| Skill Name | Tool Directory | Description | Status |\n|-----------|---------------|-------------|--------|\n"
    
    for skill in skills:
        skill_name = skill['name']
        tool_dir = skill['tool_dir'] if skill['tool_dir'] else '(Not Applicable)'
        description = skill['description'][:50] + '...' if len(skill['description']) > 50 else skill['description']
        status = skill['status'].capitalize()
        
        table += f"| {skill_name} | {tool_dir} | {description} | {status} |\n"
    
    return table

def generate_agents_table(skills: List[Dict]) -> str:
    """Generate markdown table for AGENTS.md."""
    if not skills:
        return "| Skill Name | Tool Directory | Description | Status |\n|-----------|---------------|-------------|--------|"
    
    table = "| Skill Name | Tool Directory | Description | Status |\n|-----------|---------------|-------------|--------|\n"
    
    for skill in skills:
        skill_name = f"`{skill['name']}`"
        
        if skill['type'] == 'execution':
            tool_dir = f"`{skill['tool_dir']}/`"
        else:
            tool_dir = "(Meta-skill)"
        
        description = skill['description'][:40] + '...' if len(skill['description']) > 40 else skill['description']
        status = skill['status'].capitalize()
        
        table += f"| {skill_name} | {tool_dir} | {description} | {status} |\n"
    
    return table

def update_file_with_table(file_path: Path, new_table: str, section_start_marker: str, section_end_marker: str):
    """Update file by replacing content between markers."""
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find section with table - use more flexible pattern
    # Escape special regex characters in markers
    escaped_start = re.escape(section_start_marker)
    escaped_end = re.escape(section_end_marker)
    
    # Match from section header to next section header (allow any whitespace)
    pattern = rf'({escaped_start}\s*)(.*?)(\s*{escaped_end})'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"❌ Could not find section to update in {file_path}")
        print(f"   Start marker: {section_start_marker}")
        print(f"   End marker: {section_end_marker}")
        return False
    
    # Replace table content (keep header and footer)
    header = match.group(1)
    footer = match.group(3)
    updated_content = content[:match.start(2)] + new_table + content[match.end(2):]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ Updated: {file_path}")
    return True

def update_agents_md(skills: List[Dict]):
    """Update AGENTS.md with current skills."""
    root_dir = Path(__file__).parent.parent
    agents_md = root_dir / "AGENTS.md"
    
    new_table = generate_agents_table(skills)
    return update_file_with_table(
        agents_md,
        new_table,
        "### Skill-to-Tool Mapping",
        "### Using Skills"
    )

def update_agent_instructions_md(skills: List[Dict]):
    """Update AGENT_INSTRUCTIONS.md with current skills."""
    root_dir = Path(__file__).parent.parent
    instructions_md = root_dir / "docs" / "AGENT_INSTRUCTIONS.md"
    
    new_table = generate_markdown_table(skills)
    # Use simpler markers - just the section titles
    return update_file_with_table(
        instructions_md,
        new_table,
        "## 3. Current Available Tools Mapping",
        "## 4. Tool Execution Standards"
    )

def main():
    """Main entry point for documentation synchronization."""
    print("📝 Synchronizing documentation with skill registry...")
    
    # Load skills
    skills = load_skill_registry()
    
    if not skills:
        print("❌ No skills found in registry.")
        return
    
    print(f"📋 Found {len(skills)} skill(s)")
    
    # Update documentation files
    success = True
    
    if not update_agents_md(skills):
        success = False
    
    if not update_agent_instructions_md(skills):
        success = False
    
    if success:
        print("\n✅ All documentation files synchronized successfully!")
    else:
        print("\n⚠️  Some files could not be updated.")

if __name__ == "__main__":
    main()
