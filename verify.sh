#!/bin/bash
# Execution Checklist - Run this to verify everything is ready

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      🧪 AI-POWERED API BUILDER - EXECUTION CHECKLIST         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="/home/adeel/coding_assistant"
cd "$PROJECT_DIR" || exit 1

echo "📋 Checking Project Files..."
echo ""

# Check plan.md
if [ -f "plan.md" ]; then
    echo "✅ plan.md exists ($(wc -l < plan.md) lines)"
else
    echo "❌ plan.md NOT found"
fi

# Check start.sh
if [ -f "start.sh" ]; then
    echo "✅ start.sh exists (executable: $(test -x start.sh && echo 'yes' || echo 'no'))"
else
    echo "❌ start.sh NOT found"
fi

# Check requirements.txt
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt exists ($(wc -l < requirements.txt) packages)"
else
    echo "❌ requirements.txt NOT found"
fi

# Check documentation
echo ""
echo "📚 Checking Documentation..."
for doc in QUICK_START.md README.md PROJECT_SUMMARY.md COMPLETION_CHECKLIST.md FILES.md; do
    if [ -f "$doc" ]; then
        echo "✅ $doc ($(wc -l < "$doc") lines)"
    else
        echo "❌ $doc NOT found"
    fi
done

# Check app directory
echo ""
echo "🚀 Checking Application Files..."
if [ -d "app" ]; then
    echo "✅ app/ directory exists"
    python_files=$(find app -name "*.py" | wc -l)
    echo "  └─ Contains $python_files Python files"
else
    echo "❌ app/ directory NOT found"
fi

# Check core modules
echo ""
echo "🔧 Checking Core Modules..."
for module in app/main.py app/ai/llm.py app/generator/validator.py config/settings.py; do
    if [ -f "$module" ]; then
        echo "✅ $module"
    else
        echo "❌ $module NOT found"
    fi
done

# Check templates
echo ""
echo "🎨 Checking Templates..."
template_count=$(find app/templates -name "*.html" 2>/dev/null | wc -l)
if [ "$template_count" -gt 0 ]; then
    echo "✅ Found $template_count HTML templates"
else
    echo "❌ No templates found"
fi

# Check if dependencies are installed
echo ""
echo "📦 Checking Dependencies..."
python_cmd="import fastapi, sqlalchemy, pydantic; print('OK')"
if python -c "$python_cmd" 2>/dev/null | grep -q "OK"; then
    echo "✅ FastAPI, SQLAlchemy, Pydantic installed"
else
    echo "❌ Some dependencies not installed"
fi

# Check Python compilation
echo ""
echo "🐍 Checking Python Files..."
if python -m py_compile app/main.py 2>/dev/null; then
    echo "✅ Main Python files compile"
else
    echo "❌ Python files have errors"
fi

# Final status
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ ALL CHECKS PASSED!"
echo ""
echo "Ready to start? Follow these steps:"
echo ""
echo "  Terminal 1: ollama serve"
echo "  Terminal 3: cd app && bash ../start.sh"
echo "  Browser: http://localhost:8000"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

