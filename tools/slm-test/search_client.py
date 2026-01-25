import requests
import json
import sys
import time

# Configuration - Updated to your local LLM address
LOCAL_LLM_URL = "http://localhost:1234/v1/chat/completions"

try:
    from search_mcp import _web_search_logic, _visit_page_logic
except ImportError:
    print("Error: search_mcp.py not found or dependencies missing (fastmcp, duckduckgo-search).")
    sys.exit(1)

def chat_with_search(user_query):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for real-time information and news.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "visit_page",
                "description": "Visit a URL to read its full content. Use this to find specific details missing from search summaries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The URL to visit."}
                    },
                    "required": ["url"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": "You are a professional researcher. 1. Use `web_search` to find relevant pages. 2. Use `visit_page` to read details if the search snippet is not enough (especially for dates, specs, or specific events). 3. Synthesize the final answer with citations. Don't guess."},
        {"role": "user", "content": user_query}
    ]

    print(f"🤖 User: {user_query}")
    
    # Allow up to 5 turns of thought/action
    for turn in range(5):
        payload = {
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0.5
        }

        try:
            response = requests.post(LOCAL_LLM_URL, json=payload)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            break

        message = data['choices'][0]['message']
        
        if message.get('tool_calls'):
            print(f"🔄 Turn {turn+1}: Processing tool calls...")
            
            messages.append(message) # Append assistant's intent
            
            for tool_call in message['tool_calls']:
                function_name = tool_call['function']['name']
                args = json.loads(tool_call['function']['arguments'])
                
                result_content = ""
                
                if function_name == "web_search":
                    print(f"🛠️  Searching: {args['query']}")
                    result_content = _web_search_logic(args['query'])
                elif function_name == "visit_page":
                    print(f"🌐 Visiting: {args['url']}")
                    result_content = _visit_page_logic(args['url'])
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "content": result_content
                })
            
            # Loop continues to send tool outputs back to LLM
        else:
            # No more tools, final answer
            print(f"🤖 Assistant: {message['content']}")
            break

if __name__ == "__main__":
    query = "川普什么时候总统任期满？"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    chat_with_search(query)
