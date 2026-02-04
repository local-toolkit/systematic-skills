import json
import os
import sys
import subprocess
import html
from pathlib import Path
from typing import Dict, List, Optional

class SkillManager:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.registry_path = root_dir / ".agent" / "skill_registry.json"
        self.skills_dir = root_dir / ".agent" / "skills"
        self.cache_dir = root_dir / ".tmp" / "anthropics_skills_cache"
        self._skills_cache = None

    def load_registry(self) -> List[Dict]:
        """Load skill registry from JSON file (cached)."""
        if self._skills_cache is not None:
            return self._skills_cache

        if not self.registry_path.exists():
            print("❌ Skill registry not found. Running discovery...")
            subprocess.run([sys.executable, str(self.root_dir / "scripts" / "discover_skills.py")])
        
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self._skills_cache = json.load(f)
                return self._skills_cache
        return []

    def get_skills_xml_prompt(self) -> str:
        """
        Generate <available_skills> XML block for agent system prompts.
        This enables 'Progressive Disclosure' by only providing metadata.
        """
        skills = self.load_registry()
        if not skills:
            return "<available_skills>\n</available_skills>"

        lines = ["<available_skills>"]
        
        for skill in skills:
            lines.append("<skill>")
            lines.append("<name>")
            lines.append(html.escape(skill.get("name", "unknown")))
            lines.append("</name>")
            lines.append("<description>")
            lines.append(html.escape(skill.get("description", "")))
            lines.append("</description>")
            
            # For local agents, providing the location helps
            if skill.get("skill_md"):
                 lines.append("<location>")
                 lines.append(skill["skill_md"])
                 lines.append("</location>")
            
            lines.append("</skill>")

        lines.append("</available_skills>")
        return "\n".join(lines)

    def find_skill_by_name(self, name: str) -> Optional[Dict]:
        """Find a loaded skill by its name."""
        skills = self.load_registry()
        for skill in skills:
            if skill['name'] == name or skill.get('function_name') == name:
                return skill
        return None

    def search_remote_skills(self, query: str) -> List[Dict]:
        """
        Search for skills in the remote anthropics/skills repository.
        Uses the 'anthropics-skills-expert' if available, otherwise manual fallback.
        """
        # TODO: Implement deeper search. For now, we list all and filter.
        print(f"🌐 Searching remote repository for '{query}'...")
        
        # Ensure we have the list
        self._ensure_remote_cache()
        
        results = []
        remote_list_file = self.cache_dir / "remote_skills.json"
        
        if remote_list_file.exists():
            with open(remote_list_file, 'r') as f:
                remote_skills = json.load(f)
                
            # Simple keyword match
            keywords = query.lower().split()
            for skill in remote_skills:
                text = (skill['name'] + " " + skill.get('description', '')).lower()
                if any(k in text for k in keywords):
                    results.append(skill)
        
        return results

    def _ensure_remote_cache(self):
        """Clone/Update the remote repo to cache to list skills."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        repo_path = self.cache_dir / "skills_repo"
        
        if not repo_path.exists():
            print("⬇️  Cloning anthropics/skills for the first time...")
            subprocess.run(
                ["git", "clone", "https://github.com/anthropics/skills.git", str(repo_path)],
                check=True, capture_output=True # Silence output
            )
        else:
            # git pull to update? skip for speed for now
            pass
            
        # Parse skills from repo
        skills_found = []
        # Support both root-level skills and 'skills/' subdirectory (used by anthropics/skills)
        search_paths = [repo_path, repo_path / "skills"]
        
        for base in search_paths:
            if not base.exists(): continue
            for item in base.iterdir():
                if item.is_dir() and (item / "SKILL.md").exists():
                    # Parse basic info
                    name = item.name
                    desc = "Remote skill"
                    try: 
                        content = (item / "SKILL.md").read_text()
                        for line in content.splitlines():
                            if line.startswith("description:"):
                                desc = line.split(":", 1)[1].strip()
                                break
                    except: pass
                    
                    skills_found.append({
                        "name": name,
                        "description": desc,
                        "remote_path": str(item)
                    })
        
        with open(self.cache_dir / "remote_skills.json", "w") as f:
            json.dump(skills_found, f)

    def install_remote_skill(self, skill_name: str) -> bool:
        """Install a skill from the cached remote repo."""
        self._ensure_remote_cache()
        
        # Check remote matching info
        remote_list_file = self.cache_dir / "remote_skills.json"
        source_path = None
        if remote_list_file.exists():
            with open(remote_list_file, 'r') as f:
                remote_skills = json.load(f)
                for s in remote_skills:
                    if s['name'] == skill_name:
                        source_path = Path(s['remote_path'])
                        break
        
        if not source_path or not source_path.exists():
            # Fallback to legacy root search
            source_path = self.cache_dir / "skills_repo" / skill_name
        
        if not source_path.exists():
            print(f"❌ Remote skill '{skill_name}' not found.")
            return False
            
        target_path = self.skills_dir / (skill_name + "-expert")
            
        if target_path.exists():
            print(f"⚠️  Skill '{skill_name}' already exists locally.")
            return True
        
        print(f"📦 Installing '{skill_name}' to {target_path}...")
        subprocess.run(["cp", "-r", str(source_path), str(target_path)], check=True)
        
        # Rename directory to conform to our -expert convention if it doesn't match
        # (The copy command above effectively creates target_path)
        
        # Refresh registry
        subprocess.run([sys.executable, str(self.root_dir / "scripts" / "discover_skills.py")])
        self._skills_cache = None # Invalidate cache
        return True

