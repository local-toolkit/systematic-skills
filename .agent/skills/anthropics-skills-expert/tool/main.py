import os
import sys
import subprocess
import shutil

# Configuration
REPO_URL = "https://github.com/anthropics/skills.git"
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(WORKSPACE_ROOT, ".tmp", "anthropics_skills_cache")

def ensure_repo():
    """Clones or updates the repository cache."""
    if not os.path.exists(CACHE_DIR):
        print(f"📦 Cloning {REPO_URL} to cache...", file=sys.stderr)
        try:
            subprocess.run(["git", "clone", "--depth", "1", REPO_URL, CACHE_DIR], check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repo: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Optional: Auto-update or just rely on cache? 
        # For speed, we skipp pull if it exists, let user rm -rf cache if needed.
        pass

def find_skills():
    """Walks the repo to find folders containing SKILL.md"""
    ensure_repo()
    
    found_skills = []
    
    for root, dirs, files in os.walk(CACHE_DIR):
        if ".git" in root: continue
        
        # Look for SKILL.md file
        # Note: some anthropics skills might name it differently, but usually it's SKILL.md or README.md in a skill folder
        # We'll look for folders that *look* like skills (have a README or SKILL.md and code)
        
        # Actually the search result said "folders for each skill with SKILL.md"
        if "SKILL.md" in files:
            rel_path = os.path.relpath(root, CACHE_DIR)
            found_skills.append(rel_path)
            
    return sorted(found_skills)

def list_command():
    skills = find_skills()
    if not skills:
        print("No skills found. The repository structure might have changed.")
        return

    print(f"Found {len(skills)} skills in anthropics/skills:\n")
    for s in skills:
        print(f" - {s}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pythonMain.py [list|port]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    if cmd == "list":
        list_command()
    elif cmd == "port":
        print("Porting functionality is coming soon. For now, please manually copy from:")
        print(f"{CACHE_DIR}/<skill_name>")
    else:
        print(f"Unknown command: {cmd}")
