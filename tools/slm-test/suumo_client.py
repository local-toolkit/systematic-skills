import requests
import json
import subprocess
import sys

# Configuration
LOCAL_LLM_URL = "http://localhost:1234/v1/chat/completions"

# Import our actual crawler logic from suumo_mcp.py to execute it here
# This simulates the "MCP Server" executing the requested tool
try:
    from suumo_mcp import _search_rentals_logic
except ImportError:
    print("Error: suumo_mcp.py not found or dependencies missing (fastmcp, bs4).")
    sys.exit(1)

def chat_with_local_llm(user_query):
    """
    Sends a query to the Local LLM, handles tool calls manually (simulating MCP),
    and returns the final response.
    """
    
    # 1. Define the Tool Schema (OpenAI Format)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_rentals",
                "description": "Search for rental properties on Suumo. Best for finding apartments in Tokyo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "station_name": {
                            "type": "string", 
                            "description": "The station name in Japanese (e.g., '渋谷', '新宿')."
                        },
                        "min_rent_yen": {"type": "integer", "description": "Minimum rent in Yen."},
                        "max_rent_yen": {"type": "integer", "description": "Maximum rent in Yen."}
                    },
                    "required": ["station_name"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": "You are a helpful real estate assistant. Use the provided tools to search for information."},
        {"role": "user", "content": user_query}
    ]

    print(f"🤖 User: {user_query}")
    print("⏳ Sending to Local LLM...")

    # 2. First Call: Ask LLM what to do
    payload = {
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.0 # Deterministic for tool calls
    }

    try:
        response = requests.post(LOCAL_LLM_URL, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error connecting to LLM: {e}")
        return

    message = data['choices'][0]['message']
    
    # 3. Check for Tool Calls
    if message.get('tool_calls'):
        tool_call = message['tool_calls'][0]
        function_name = tool_call['function']['name']
        arguments_str = tool_call['function']['arguments']
        
        print(f"🛠️  LLM wants to call: {function_name}({arguments_str})")
        
        if function_name == "search_rentals":
            # Execute the python function directly
            args = json.loads(arguments_str)
            
            # Call our suumo_mcp function logic
            # Note: search_rentals in suumo_mcp returns a JSON string directly
            result_json_str = _search_rentals_logic(
                station_name=args.get("station_name"),
                min_rent_yen=args.get("min_rent_yen", 0),
                max_rent_yen=args.get("max_rent_yen", 200000)
            )
            
            print(f"✅ Tool Output (Snippet): {result_json_str[:100]}...")

            # 4. Feed result back to LLM
            messages.append(message) # Add the assistant's tool-call message
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "content": result_json_str
            })
            
            # 5. Final completion
            payload = {
                "messages": messages,
                "tools": tools
            }
            res2 = requests.post(LOCAL_LLM_URL, json=payload, headers={"Content-Type": "application/json"})
            data2 = res2.json()
            final_content = data2['choices'][0]['message']['content']
            
            print(f"🤖 Assistant: {final_content}")
            
    else:
        print(f"🤖 Assistant: {message['content']}")

if __name__ == "__main__":
    # Test Query
    query = "帮我找一下涩谷站附近的房子，租金预算15万日元以内。"
    if len(sys.argv) > 1:
        query = sys.argv[1]
        
    chat_with_local_llm(query)
