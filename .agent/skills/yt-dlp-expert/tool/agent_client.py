import requests
import json
import subprocess
import sys
import os

# Configuration
LOCAL_LLM_URL = os.getenv("LLM_URL", "http://localhost:1234/v1/chat/completions")
script_dir = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = os.path.join(script_dir, "../../.agent/skills/yt-dlp-expert/SKILL.md")
TOOL_SCRIPT = os.path.join(script_dir, "main.py")

def load_skill_context():
    try:
        with open(SKILL_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read SKILL.md: {e}")
        return ""

def run_yt_dlp_tool(**kwargs):
    """Executes the yt-dlp tool with the given arguments."""
    # Attempt to find venv python first
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, "venv", "bin", "python")
    
    if os.path.exists(venv_python):
        python_exe = venv_python
    else:
        python_exe = sys.executable

    cmd = [python_exe, TOOL_SCRIPT]
    
    if kwargs.get('url'):
        cmd.append(kwargs['url'])
    
    if kwargs.get('audio_only'):
        cmd.append('--audio-only')
        
    if kwargs.get('format'):
        cmd.extend(['--format', kwargs['format']])
        
    if kwargs.get('playlist_items'):
        cmd.extend(['--playlist-items', str(kwargs['playlist_items'])])
        
    if kwargs.get('cookies_browser'):
        cmd.extend(['--cookies-browser', kwargs['cookies_browser']])
        
    if kwargs.get('cookies_file'):
        cmd.extend(['--cookies-file', kwargs['cookies_file']])

    if kwargs.get('proxy'):
        cmd.extend(['--proxy', kwargs['proxy']])

    if kwargs.get('subs'):
        cmd.append('--subs')
        
    if kwargs.get('simulate'):
        cmd.append('--simulate')

    print(f"\n🚀 Executing: {' '.join(cmd)}")
    try:
        # Run and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"SUCCESS:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"ERROR (Exit Code {e.returncode}):\n{e.stderr}\n{e.stdout}"
    except Exception as e:
        return f"EXECUTION FAILED: {str(e)}"

def chat_with_local_llm(user_query):
    skill_content = load_skill_context()
    
    system_prompt = f"""You are an advanced AI assistant capable of controlling a terminal tool called 'yt-dlp-tool'.
You have access to a specific 'Skill' knowledge base which describes how to use yt-dlp effectively.

--- SKILL KNOWLEDGE BASE ---
{skill_content}
----------------------------

Your job is to interpret the user's natural language request and call the `run_yt_dlp` tool with the appropriate arguments.
Always use the tools provided to fulfill the user's request.
"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_yt_dlp",
                "description": "Download videos or audio using yt-dlp wrapper. Use this for ALL download requests.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The URL of the video or playlist."},
                        "audio_only": {"type": "boolean", "description": "Set to true if user wants audio only (mp3)."},
                        "format": {"type": "string", "description": "Custom format string (e.g. 'bv+ba/b')."},
                        "playlist_items": {"type": "string", "description": "Specific items to download from playlist (e.g. '1,2,5-10')."},
                        "cookies_browser": {"type": "string", "description": "Browser to load cookies from (chrome, firefox)."},
                        "cookies_file": {"type": "string", "description": "Path to cookies file."},
                        "proxy": {"type": "string", "description": "Proxy URL."},
                        "subs": {"type": "boolean", "description": "Download subtitles."},
                        "simulate": {"type": "boolean", "description": "Simulate download without writing to disk."}
                    },
                    "required": ["url"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    print(f"🤖 User: {user_query}")
    print("⏳ Sending to Local SLM...")

    payload = {
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.0
    }

    try:
        response = requests.post(LOCAL_LLM_URL, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error connecting to LLM: {e}")
        return

    message = data['choices'][0]['message']

    if message.get('tool_calls'):
        tool_call = message['tool_calls'][0]
        function_name = tool_call['function']['name']
        arguments_str = tool_call['function']['arguments']
        
        print(f"🛠️  SLM wants to call: {function_name}({arguments_str})")

        if function_name == "run_yt_dlp":
            args = json.loads(arguments_str)
            tool_output = run_yt_dlp_tool(**args)
            
            print(f"✅ Tool Output: {tool_output[:200]}...") # Truncate for display

            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "content": tool_output
            })
            
            # Final response
            payload["messages"] = messages
            try:
                res2 = requests.post(LOCAL_LLM_URL, json=payload, headers={"Content-Type": "application/json"})
                final_content = res2.json()['choices'][0]['message']['content']
                print(f"\n🤖 Assistant: {final_content}")
            except Exception as e:
                 print(f"❌ Error getting final response: {e}")

    else:
        print(f"🤖 Assistant: {message['content']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_client.py \"<your query>\"")
        sys.exit(1)
    
    query = sys.argv[1]
    chat_with_local_llm(query)
