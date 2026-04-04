#!/bin/bash
# Setup script for AI-Powered API Builder

set -e

echo "🚀 AI-Powered API Builder Setup"
echo "=================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "  Found Python $python_version"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python -m venv venv
fi

echo "✓ Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null

# Setup environment file
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Start Ollama (in another terminal):"
echo "   ollama serve"
echo ""
echo "2. Pull the model (first time only):"
echo "   ollama pull qwen2.5-coder:7b"
echo ""
echo "3. Run the application:"
echo "   cd app"
echo "   python -m uvicorn main:app --reload"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:8000"
echo ""

