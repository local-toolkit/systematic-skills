# Antigravity Tools: The One-Stop Agentic Toolkit

**Antigravity Tools** is a unified, high-performance agentic framework designed to turn your command line into a powerhouse of capability. It integrates a diverse set of specialized tools—from media downloading and conversion to news aggregation and paper auditing—under a single, intelligent interface.

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

</div>

## 🚀 Why This Project is Unique

- **Unified Intelligence**: Instead of juggling dozens of scripts, you have **one** intelligent entry point (`core/agent.py`). Just tell it what you want, and it routes your request to the right expert tool.
- **MCP-Native Architecture**: Built from the ground up with the **Model Context Protocol (MCP)** in mind. Tools are designed to be easily exposed to LLMs, making them future-proof and agent-ready.
- **Skill-Based Routing**: The system doesn't just match keywords; it understands "Skills". It uses a semantic registry to find the perfect tool for your task, whether it's an execution tool (subprocess) or a guidance tool (meta-skill).
- **Plug & Play Extensibility**: Adding a new tool is as simple as running `python scripts/create_tool.py`. The infrastructure handles the rest.

## 🌟 Key Features

- **📺 Media Extraction**: Industrial-strength video/audio downloader with format controls (`yt-dlp-tool`).
- **📰 News Aggregation**: Scrape and summarize tech news from HackerNews, GitHub, and more (`news-aggregator-tool`).
- **🖼️ Image Processing**: Convert, resize, watermark, and split images with a single command (`imgconv-tool`).
- **📑 Academic Workflow**: Automate paper downloading and auditing (`paper-audit-tool`, `pdf-downloader-tool`).
- **🕷️ Browser Automation**: Control a headless browser for scraping and testing (`playwright-tool`).

## 🛠️ Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/antigravity-tools.git
    cd antigravity-tools
    ```

2.  **Set up the environment:**

    ```bash
    # Create and activate a virtual environment (recommended)
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate.ps1
    ```

3.  **Install dependencies:**
    Each tool has its own dependencies to keep things lightweight. You can install what you need, or everything:

    ```bash
    # Install core dependencies
    pip install -r requirements.txt

    # Or navigate to specific tools to install their requirements
    pip install -r tools/yt-dlp-tool/requirements.txt
    ```

4.  **Discover Skills:**
    Initialize the skill registry to register all available tools.
    ```bash
    python scripts/discover_skills.py
    ```

## ⚡ Usage

The magic happens via the unified agent entry point. You don't need to remember specific script names.

**Basic Syntax:**

```bash
python core/agent.py "<your natural language request>"
```

**Examples:**

- **Download a video:**

  ```bash
  python core/agent.py "Download the audio from this video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  ```

- **Get the latest AI news:**

  ```bash
  python core/agent.py "Get me the top 10 AI news from HackerNews"
  ```

- **Convert an image:**

  ```bash
  python core/agent.py "Convert my photo.png to jpg and resize it to 800px width"
  ```

- **Download a research paper:**
  ```bash
  python core/agent.py "Download this paper https://arxiv.org/pdf/1706.03762.pdf"
  ```

## 🤝 Contributing

We love contributions! Whether you want to add a new "Skill" or improve an existing "Tool", please feel free to submit a Pull Request.

1.  Use `python scripts/create_tool.py <name>` to scaffold a new tool.
2.  Implement your logic.
3.  Run `python scripts/discover_skills.py` to register it.
4.  Submit your PR!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# systematic-skills
