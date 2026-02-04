import sys
import os
import json
import subprocess
import re
from typing import Optional

script_dir = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = os.path.join(os.path.dirname(script_dir), "../.agent", "skills", "pdf-downloader-expert", "SKILL.md")
TOOL_SCRIPT = os.path.join(script_dir, "main.py")

def load_skill_context() -> str:
    """Load skill knowledge base."""
    try:
        with open(SKILL_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read SKILL.md: {e}")
        return ""

def extract_url(text: str) -> Optional[str]:
    """Extract URL from text."""
    # Basic URL regex
    url_pattern = re.compile(r'https?://[^\s,]+')
    match = url_pattern.search(text)
    if match:
        return match.group(0)
    return None

def run_pdf_downloader_tool(url: str) -> str:
    """Execute pdf-downloader tool with the given URL."""
    venv_python = os.path.join(script_dir, "venv", "bin", "python")

    if os.path.exists(venv_python):
        python_exe = venv_python
    else:
        python_exe = sys.executable

    cmd = [python_exe, TOOL_SCRIPT, url]

    print(f"\n🚀 Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"SUCCESS:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"ERROR (Exit Code {e.returncode}):\n{e.stderr or e.stdout}"
    except Exception as e:
        return f"EXECUTION FAILED: {str(e)}"

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python agent_client.py \"<query>\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    url = extract_url(query)
    
    if not url:
        print("ERROR: No URL found in the request. Please provide a link starting with http:// or https://")
        sys.exit(1)
        
    print(run_pdf_downloader_tool(url))

if __name__ == "__main__":
    main()
