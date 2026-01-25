import sys
import subprocess
import os

TOOL_SCRIPT = os.path.join(os.path.dirname(__file__), "main.py")

def execute_tool(request):
    """Parses the request and executes main.py."""
    # Simple extraction of filename from request like "Move processed paper.pdf to completed"
    # or "Audit paper.pdf"
    words = request.split()
    filename = None
    for word in words:
        if word.endswith(".pdf"):
            filename = word
            break
            
    if not filename:
        return "ERROR: No PDF filename found in request."

    cmd = [sys.executable, TOOL_SCRIPT, filename]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr or e.stdout}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_client.py \"<request>\"")
        sys.exit(1)
        
    request = sys.argv[1]
    print(execute_tool(request))
