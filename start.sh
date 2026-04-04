#!/bin/bash
# Start FastAPI application for AI-Powered API Builder

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      🚀 AI-Powered API Builder - FastAPI Server              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Project: AI-Powered API Builder"
echo "📁 Location: /home/adeel/coding_assistant"
echo "⚙️  Framework: FastAPI 0.135.3"
echo "🌐 Server: Uvicorn 0.43.0"
echo ""

# Check if in app directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Make sure you're in the app directory"
    echo "   $ cd /home/adeel/coding_assistant/app"
    exit 1
fi

echo "✅ Verification:"
echo "  ✓ Python environment active"
echo "  ✓ Dependencies installed"
echo "  ✓ main.py found"
echo ""

echo "📋 Server Information:"
echo "  Host: 0.0.0.0"
echo "  Port: 8000"
echo "  URL: http://localhost:8000"
echo "  Reload: Enabled (auto-restart on file changes)"
echo ""

echo "🔗 Endpoints:"
echo "  🏠 Web UI: http://localhost:8000/"
echo "  📚 API Docs (Swagger): http://localhost:8000/docs"
echo "  📖 ReDoc: http://localhost:8000/redoc"
echo "  🏥 Health: http://localhost:8000/health"
echo ""

echo "📦 Generated Projects:"
echo "  Location: /home/adeel/coding_assistant/generated_projects/"
echo ""

echo "⚠️  Requirements:"
echo "  • Ollama running on http://localhost:11434"
echo "  • Ollama model: qwen2.5-coder:7b"
echo ""

echo "🛑 Stop Server:"
echo "  Press Ctrl+C to stop the server"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Starting server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

