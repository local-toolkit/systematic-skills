#!/usr/bin/env python3
"""
Validate Skills Script

Checks for:
1. Absolute paths in SKILL.md and code files.
2. Completeness of SKILL.md (frontmatter).
"""

import os
import sys
import yaml
import re
from pathlib import Path

def check_no_absolute_paths(file_path: Path) -> bool:
    """Check if file contains absolute paths like /Users/xujintao..."""
    # Allow exceptions?
    if file_path.name == "validate_skills.py": return True
    
    try:
        content = file_path.read_text(errors='ignore')
    except:
        return True
        
    # Pattern for user home path (simplified)
    # We specifically look for the user's home dir which caused the issue
    pattern = r"/Users/[a-zA-Z0-9_-]+"
    
    matches = re.findall(pattern, content)
    if matches:
        print(f"❌ {file_path.relative_to(Path.cwd())} contains specific absolute paths:")
        for m in matches[:3]:
            print(f"   - {m}...")
        return False
    return True

def validate_skill_md(skill_dir: Path) -> bool:
    md_path = skill_dir / "SKILL.md"
    if not md_path.exists():
        print(f"❌ {skill_dir.name} missing SKILL.md")
        return False
        
    valid = True
    content = md_path.read_text(encoding='utf-8-sig')
    
    # Check frontmatter
    if not content.startswith("---"):
        print(f"❌ {skill_dir.name}/SKILL.md missing frontmatter")
        valid = False
    
    # Check for absolute paths
    if not check_no_absolute_paths(md_path):
        valid = False
        
    return valid

def main():
    root_dir = Path.cwd()
    skills_dir = root_dir / ".agent" / "skills"
    
    print("🔍 Validating skills...")
    
    all_valid = True
    
    # Check skills
    if skills_dir.exists():
        for skill in skills_dir.iterdir():
            if skill.is_dir():
                if not validate_skill_md(skill):
                    all_valid = False
                
                # Check code files in skill dir
                for root, _, files in os.walk(skill):
                    for file in files:
                        if file.endswith(('.py', '.sh', '.js')):
                            file_path = Path(root) / file
                            if not check_no_absolute_paths(file_path):
                                all_valid = False

    if all_valid:
        print("✅ All checks passed!")
        sys.exit(0)
    else:
        print("⚠️  Issues found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
