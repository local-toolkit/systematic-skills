import requests
import json
import subprocess
import sys
import os

# Configuration
LOCAL_LLM_URL = os.getenv("LLM_URL", "http://localhost:1234/v1/chat/completions")
script_dir = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = os.path.join(script_dir, "../../.agent/skills/imgconv-expert/SKILL.md")
TOOL_SCRIPT = os.path.join(script_dir, "main.py")

def load_skill_context():
    """Load the SKILL.md file for imgconv expertise."""
    try:
        with open(SKILL_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read SKILL.md: {e}")
        return ""

def run_imgconv_tool(**kwargs):
    """Execute the imgconv tool with the given arguments."""
    # Attempt to find venv python first
    venv_python = os.path.join(script_dir, "venv", "bin", "python")

    if os.path.exists(venv_python):
        python_exe = venv_python
    else:
        python_exe = sys.executable

    cmd = [python_exe, TOOL_SCRIPT]

    # Add action argument (required)
    if kwargs.get('action'):
        cmd.extend(['--action', kwargs['action']])
    else:
        return "ERROR: 'action' parameter is required"

    # Add input file (required)
    if kwargs.get('input'):
        cmd.extend(['--input', kwargs['input']])
    else:
        return "ERROR: 'input' parameter is required"

    # Add output file
    if kwargs.get('output'):
        cmd.extend(['--output', kwargs['output']])

    # Add format
    if kwargs.get('format'):
        cmd.extend(['--format', kwargs['format']])

    # Add resize options
    if kwargs.get('width'):
        cmd.extend(['--width', str(kwargs['width'])])

    if kwargs.get('height'):
        cmd.extend(['--height', str(kwargs['height'])])

    if kwargs.get('percent'):
        cmd.extend(['--percent', str(kwargs['percent'])])

    # Add watermark options
    if kwargs.get('watermark'):
        cmd.extend(['--watermark', kwargs['watermark']])

    if kwargs.get('opacity'):
        cmd.extend(['--opacity', str(kwargs['opacity'])])

    if kwargs.get('random'):
        cmd.append('--random')

    if kwargs.get('offset_x'):
        cmd.extend(['--offset-x', str(kwargs['offset_x'])])

    if kwargs.get('offset_y'):
        cmd.extend(['--offset-y', str(kwargs['offset_y'])])

    # Add split options
    if kwargs.get('split_parts'):
        cmd.extend(['--split-parts', str(kwargs['split_parts'])])

    if kwargs.get('split_mode'):
        cmd.extend(['--split-mode', kwargs['split_mode']])

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
    """Process user query using local LLM with imgconv tool capabilities."""
    skill_content = load_skill_context()

    system_prompt = f"""You are an advanced AI assistant capable of controlling a terminal tool called 'imgconv-tool'.
You have access to a specific 'Skill' knowledge base which describes how to use imgconv effectively.

--- SKILL KNOWLEDGE BASE ---
{skill_content}
----------------------------

Your job is to interpret the user's natural language request and call the `run_imgconv` tool with the appropriate arguments.
Always use the tools provided to fulfill the user's request.

IMPORTANT RULES:
1. The 'action' parameter is REQUIRED and must be one of: 'convert', 'resize', 'watermark', 'split'
2. The 'input' parameter is REQUIRED - this is the path to the input image
3. For 'convert' action: specify --format for the output format (jpeg, png, gif, tiff, bmp, webp)
4. For 'resize' action: specify --width, --height, or --percent (one or more)
5. For 'watermark' action: specify --watermark (path to watermark image), optionally --opacity (0-255), --random, --offset-x, --offset-y
6. For 'split' action: specify --split-parts (number of parts) and --split-mode (horizontal or vertical)
7. Always specify --output for the result file path
"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_imgconv",
                "description": "Process images using imgconv tool: convert format, resize, add watermark, or split images",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["convert", "resize", "watermark", "split"],
                            "description": "The action to perform: convert format, resize, add watermark, or split image"
                        },
                        "input": {
                            "type": "string",
                            "description": "Path to the input image file"
                        },
                        "output": {
                            "type": "string",
                            "description": "Path to the output file"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["jpeg", "png", "gif", "tiff", "bmp", "webp"],
                            "description": "Target format for conversion (required for convert action)"
                        },
                        "width": {
                            "type": "integer",
                            "description": "Target width in pixels (for resize)"
                        },
                        "height": {
                            "type": "integer",
                            "description": "Target height in pixels (for resize)"
                        },
                        "percent": {
                            "type": "integer",
                            "description": "Percentage to resize (for resize, e.g. 50 for 50%)"
                        },
                        "watermark": {
                            "type": "string",
                            "description": "Path to watermark image (required for watermark action)"
                        },
                        "opacity": {
                            "type": "integer",
                            "description": "Watermark opacity 0-255 (default 128 for watermark)"
                        },
                        "random": {
                            "type": "boolean",
                            "description": "Place watermark at random position (for watermark)"
                        },
                        "offset_x": {
                            "type": "integer",
                            "description": "Watermark offset X from position (for watermark)"
                        },
                        "offset_y": {
                            "type": "integer",
                            "description": "Watermark offset Y from position (for watermark)"
                        },
                        "split_parts": {
                            "type": "integer",
                            "description": "Number of parts to split into (required for split action)"
                        },
                        "split_mode": {
                            "type": "string",
                            "enum": ["horizontal", "vertical"],
                            "description": "Split direction: horizontal or vertical (for split action)"
                        }
                    },
                    "required": ["action", "input"]
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

        if function_name == "run_imgconv":
            args = json.loads(arguments_str)
            tool_output = run_imgconv_tool(**args)

            print(f"✅ Tool Output: {tool_output[:500]}...")  # Truncate for display

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
        print("\nExamples:")
        print('  python agent_client.py "Convert image.png to JPEG format"')
        print('  python agent_client.py "Resize photo.jpg to width 800px"')
        print('  python agent_client.py "Add watermark.png to image.jpg with 50% opacity"')
        print('  python agent_client.py "Split longimage.png into 3 parts horizontally"')
        sys.exit(1)

    query = sys.argv[1]
    chat_with_local_llm(query)
