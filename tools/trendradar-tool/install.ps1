# TrendRadar Tool Installation Script for Windows PowerShell

# Requires PowerShell 5.1 or higher

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  TrendRadar Tool Installation" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

Write-Host "📁 Working directory: $SCRIPT_DIR" -ForegroundColor Green
Write-Host ""

# Check Python version
Write-Host "🐍 Checking Python version..." -ForegroundColor Yellow
$PYTHON_CMD = "python"

# Try python3 first, then python
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PYTHON_CMD = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PYTHON_CMD = "python"
} else {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

$PYTHON_VERSION = & $PYTHON_CMD --version 2>&1
Write-Host "✅ Found Python: $PYTHON_VERSION" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "🧪 Creating virtual environment..." -ForegroundColor Yellow
    & $PYTHON_CMD -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment already exists" -ForegroundColor Yellow
}

Write-Host ""

# Activate virtual environment (PowerShell)
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Clone TrendRadar if not exists
$TRENDRADAR_PATH = "$env:USERPROFILE\TrendRadar"

if (-not (Test-Path $TRENDRADAR_PATH)) {
    Write-Host "📥 Cloning TrendRadar repository..." -ForegroundColor Yellow
    git clone https://github.com/sansan0/TrendRadar.git $TRENDRADAR_PATH

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ TrendRadar cloned to $TRENDRADAR_PATH" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to clone TrendRadar" -ForegroundColor Red
        Write-Host "Please check your internet connection and git installation." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "⚠️  TrendRadar already exists at $TRENDRADAR_PATH" -ForegroundColor Yellow
    Write-Host "🔄 Updating TrendRadar..." -ForegroundColor Yellow
    Set-Location $TRENDRADAR_PATH
    git pull
    Set-Location $SCRIPT_DIR
}

Write-Host ""

# Create symbolic link (directory junction on Windows)
Write-Host "🔗 Creating link to TrendRadar MCP server..." -ForegroundColor Yellow
if (Test-Path "trendradar-mcp") {
    Write-Host "⚠️  Link already exists" -ForegroundColor Yellow
} else {
    # Use New-Item -ItemType Junction for Windows
    New-Item -ItemType Junction -Path "trendradar-mcp" -Target "$TRENDRADAR_PATH\mcp_server"
    Write-Host "✅ Link created: trendradar-mcp -> $TRENDRADAR_PATH\mcp_server" -ForegroundColor Green
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Quick Start:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Test installation:" -ForegroundColor White
Write-Host "   $PYTHON_CMD agent_client.py `"menu`"" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Query latest news:" -ForegroundColor White
Write-Host "   $PYTHON_CMD agent_client.py `"查看今天的新闻`"" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Use with LLM:" -ForegroundColor White
Write-Host "   `$env:LLM_URL='http://localhost:1234/v1/chat/completions'; $PYTHON_CMD agent_client.py `"分析AI的热度趋势`"" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Start TrendRadar MCP server:" -ForegroundColor White
Write-Host "   cd trendradar-mcp" -ForegroundColor Yellow
Write-Host "   $PYTHON_CMD server.py --transport stdio" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 For more information, see:" -ForegroundColor Cyan
Write-Host "   - Tool README: $SCRIPT_DIR\README.md" -ForegroundColor Yellow
Write-Host "   - TrendRadar: https://github.com/sansan0/TrendRadar" -ForegroundColor Yellow
Write-Host "   - TrendRadar MCP FAQ: https://github.com/sansan0/TrendRadar/blob/master/README-MCP-FAQ.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Tip: Configure AI API keys in TrendRadar's config\config.yaml for analysis features." -ForegroundColor Cyan
Write-Host ""
