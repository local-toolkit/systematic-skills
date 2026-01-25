import requests
from bs4 import BeautifulSoup
from fastmcp import FastMCP
import json
import urllib.parse

# Initialize the MCP Server
mcp = FastMCP("Suumo Crawler")

# Common Headers to avoid simple bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def _search_rentals_logic(station_name: str, min_rent_yen: int = 0, max_rent_yen: int = 200000) -> str:
    # ... (all the logic moves here)
    base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/"
    params = {
        "ar": "030", 
        "bs": "040", 
        "ta": "13",  
        "sc": "13103", 
        "cb": str(min_rent_yen / 10000), 
        "ct": str(max_rent_yen / 10000),
        "mb": "0",   
        "mt": "9999999",
        "et": "9999999",
        "cn": "9999999",
        "pc": "30"
    }
    target_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        resp = requests.get(target_url, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        properties = []
        items = soup.find_all("div", class_="cassetteitem")
        for item in items[:5]:
            try:
                name = item.find("div", class_="cassetteitem_content-title").text.strip()
                address = item.find("li", class_="cassetteitem_detail-col1").text.strip()
                rent = item.find("span", class_="cassetteitem_other-emphasisUI").text.strip()
                properties.append({
                    "name": name,
                    "address": address,
                    "rent": rent,
                    "note": f"Station match for '{station_name}' not guaranteed in this simple demo mode."
                })
            except Exception:
                continue
        if not properties:
            return json.dumps({"error": "No properties found or anti-bot blocked us.", "url": target_url})
        return json.dumps(properties, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def search_rentals(station_name: str, min_rent_yen: int = 0, max_rent_yen: int = 200000) -> str:
    """
    Search for rental properties on Suumo using a station name and rent range.
    """
    return _search_rentals_logic(station_name, min_rent_yen, max_rent_yen)

def _get_property_details_logic(property_name: str) -> str:
    return f"Details for {property_name}: Close to station, heavily requested. (Mock Detail)"

@mcp.tool()
def get_property_details(property_name: str) -> str:
    """
    Get details for a specific property.
    """
    return _get_property_details_logic(property_name)


if __name__ == "__main__":
    mcp.run()
