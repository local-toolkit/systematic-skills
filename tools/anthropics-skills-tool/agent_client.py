import sys
import subprocess
import os

# Standard Agent Client Wrapper
TOOL_SCRIPT = os.path.join(os.path.dirname(__file__), "main.py")

def run_tool():
    # Pass all arguments to the main script
    cmd = [sys.executable, TOOL_SCRIPT] + sys.argv[1:]
    
    try:
        # Run execution
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        # Output handling
        if res.returncode != 0:
            print(f"Error: {res.stderr}")
            sys.exit(res.returncode)
            
        print(res.stdout)
        
    except Exception as e:
        print(f"Execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_tool()
