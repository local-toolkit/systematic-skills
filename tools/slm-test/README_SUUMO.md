# Suumo MCP Crawler Setup Guide

This guide explains how to run the Suumo crawler with your local LLM.

## Prerequisites

- **Python 3.10+** installed.
- **Local LLM** running at `http://localhost:1234`.

## Installation

1.  Open your terminal in this directory.
2.  Install the required Python packages:

    ```bash
    pip install fastmcp requests beautifulsoup4
    ```

## Usage

### Option 1: Run as a Standalone Script (Recommended for Testing)

Use the client script to simulate the whole process (LLM -> Tool -> Suumo -> LLM).

```bash
python suumo_client.py "Find me a cheap apartment in Shinjuku"
```

1.  The script sends your query to the local LLM.
2.  The LLM decides to call `search_rentals`.
3.  The script executes the Python logic in `suumo_mcp.py`.
4.  The results are sent back to the LLM for a final summary.

### Option 2: Run as a Pure MCP Server

If you want to connect this to an official MCP Client (like Claude Desktop or a future LM Studio version that supports direct remote MCP connection):

```bash
fastmcp run suumo_mcp.py
```

This will start an MCP server that exposes the `search_rentals` tool.

## Troubleshooting

-   **Connection Refused:** Ensure your Local LLM is running and accessible at `http://localhost:1234`.
-   **No Properties Found:** Suumo might be blocking the request or the search parameters are too restrictive. The script prints the URL it tried to fetch; you can check it in a browser.
