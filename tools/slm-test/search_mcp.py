import json
import requests
from bs4 import BeautifulSoup
from fastmcp import FastMCP
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException

# Initialize the MCP Server
mcp = FastMCP("Pro Web Search Tool")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def _web_search_logic(query: str, max_results: int = 5) -> str:
    """
    Robust web search with backend fallbacks.
    """
    print(f"🔍 Pro Searching for: {query}")
    backends = ['api', 'lite', 'html'] # 'api' is usually best, 'lite' is fallback
    
    for backend in backends:
        try:
            print(f"   Trying backend: {backend}...")
            with DDGS() as ddgs:
                # region='wt-wt' (Global), safesearch='moderate'
                results = [r for r in ddgs.text(query, region='wt-wt', safesearch='moderate', max_results=max_results, backend=backend)]
                
                if results:
                    print(f"✅ Found {len(results)} results via {backend}.")
                    return json.dumps(results, ensure_ascii=False)
                
        except RatelimitException:
            print(f"⚠️  Rate limit hit on {backend}, switching...")
            continue
        except Exception as e:
            print(f"⚠️  Error on {backend}: {e}")
            continue
            
    # Final Fallback to News
    try:
        print("   Trying News fallback...")
        with DDGS() as ddgs:
             results = [r for r in ddgs.news(query, region='wt-wt', safesearch='moderate', max_results=max_results)]
             if results:
                 return json.dumps(results, ensure_ascii=False)
    except Exception:
        pass

    return json.dumps({"error": f"All search backends failed for '{query}'. Try again later."})

def _visit_page_logic(url: str) -> str:
    """
    Fetches and cleans the content of a URL.
    """
    print(f"🌐 Visiting page: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Remove clutter
        for element in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
            element.decompose()
            
        text = soup.get_text(separator="\n")
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Truncate to avoid context overflow (approx 4000 chars)
        preview = clean_text[:4000]
        if len(clean_text) > 4000:
            preview += "\n...[Content Truncated]..."
            
        print(f"📄 Extracted {len(preview)} chars.")
        return json.dumps({"url": url, "content": preview}, ensure_ascii=False)
        
    except Exception as e:
        print(f"❌ Visit Error: {e}")
        return json.dumps({"error": f"Failed to visit {url}: {str(e)}"})

@mcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for real-time information.
    """
    return _web_search_logic(query, max_results)

@mcp.tool()
def visit_page(url: str) -> str:
    """
    Visit a specific URL and extract its text content. 
    Use this when search results are insufficient or you need specific details (dates, specs, policies).
    """
    return _visit_page_logic(url)

if __name__ == "__main__":
    mcp.run()
