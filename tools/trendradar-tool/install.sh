#!/bin/bash
# TrendRadar Tool Installation Script for Linux/Mac

set -e

echo "============================================="
echo "  TrendRadar Tool Installation"
echo "============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
PYTHON_CMD=python3
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD=python
fi

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Found Python: $PYTHON_VERSION${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo ""

# Clone TrendRadar if not exists
TRENDRADAR_PATH="$HOME/TrendRadar"
if [ ! -d "$TRENDRADAR_PATH" ]; then
    echo "📥 Cloning TrendRadar repository..."
    git clone https://github.com/sansan0/TrendRadar.git "$TRENDRADAR_PATH"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ TrendRadar cloned to $TRENDRADAR_PATH${NC}"
    else
        echo -e "${RED}❌ Failed to clone TrendRadar${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  TrendRadar already exists at $TRENDRADAR_PATH${NC}"
    echo "🔄 Updating TrendRadar..."
    cd "$TRENDRADAR_PATH"
    git pull
    cd "$SCRIPT_DIR"
fi

echo ""

# Create symlink for easier access
echo "🔗 Creating symlink to TrendRadar MCP server..."
if [ -L "trendradar-mcp" ]; then
    echo -e "${YELLOW}⚠️  Symlink already exists${NC}"
else
    ln -s "$TRENDRADAR_PATH/mcp_server" trendradar-mcp
    echo -e "${GREEN}✅ Symlink created: trendradar-mcp -> $TRENDRADAR_PATH/mcp_server${NC}"
fi

echo ""
echo "============================================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "============================================="
echo ""
echo "📖 Quick Start:"
echo ""
echo "1. Test installation:"
echo "   $PYTHON_CMD agent_client.py \"menu\""
echo ""
echo "2. Query latest news:"
echo "   $PYTHON_CMD agent_client.py \"查看今天的新闻\""
echo ""
echo "3. Use with LLM (set LLM_URL environment variable):"
echo "   LLM_URL=http://localhost:1234/v1/chat/completions $PYTHON_CMD agent_client.py \"分析AI的热度趋势\""
echo ""
echo "4. Start TrendRadar MCP server:"
echo "   cd trendradar-mcp"
echo "   $PYTHON_CMD server.py --transport stdio"
echo ""
echo "📚 For more information, see:"
echo "   - Tool README: $SCRIPT_DIR/README.md"
echo "   - TrendRadar: https://github.com/sansan0/TrendRadar"
echo "   - TrendRadar MCP FAQ: https://github.com/sansan0/TrendRadar/blob/master/README-MCP-FAQ.md"
echo ""
echo "💡 Tip: Configure AI API keys in TrendRadar's config/config.yaml for analysis features."
echo ""
