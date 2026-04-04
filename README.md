# 🚀 AI-Powered API Builder

Generate FastAPI backends from natural language prompts using local LLM (Ollama).

## ✨ Features

- 🧠 **AI-Powered Generation** - Generate complete FastAPI projects from natural language
- 🔐 **JWT Authentication** - Built-in support for token-based auth
- 📊 **CRUD Operations** - Auto-generate CRUD endpoints
- 🗄️ **Database Integration** - SQLAlchemy ORM with models
- ✅ **Code Validation** - Multi-layer validation and security checks
- 📝 **Code Editor** - View and edit generated code in browser
- ▶️ **Run Locally** - Execute generated APIs instantly
- 🎨 **Clean UI** - Intuitive Jinja2 templates

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **Python 3.11+** - Programming language
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for database operations

### Frontend
- **Jinja2** - Server-side templates
- **HTML5 + CSS3** - Markup and styling
- **Vanilla JavaScript** - Interactivity

### AI Engine
- **Ollama** - Local LLM runtime
- **Qwen 2.5 Coder 7B** - Code generation model

## 📋 Prerequisites

1. **Python 3.11 or higher**
   ```bash
   python --version
   ```

2. **Ollama** - Download from [ollama.ai](https://ollama.ai)

3. **Ollama Model**
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
cd /path/to/coding_assistant
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` if needed (optional - defaults are set):
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
OLLAMA_TIMEOUT=120
DEBUG=true
```

### 5. Start Ollama Service

In a separate terminal:
```bash
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434 (http)
```

### 6. Pull the Model (First Time Only)

```bash
ollama pull qwen2.5-coder:7b
```

### 7. Run the Application

```bash
cd app
python -m uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 8. Open in Browser

Navigate to: **http://localhost:8000**

## 📖 Usage

### Basic Workflow

1. **Enter Prompt** - Describe your API in natural language
   ```
   Example: "Create a blog API with posts and comments, JWT authentication, and CRUD operations"
   ```

2. **Select Features** - Check desired features:
   - JWT Authentication
   - CRUD Operations
   - User Model
   - Database

3. **Generate** - Click "Generate API" and wait
   - Ollama processes the prompt
   - FastAPI code is generated
   - Code is validated

4. **Review** - View generated files:
   - Browse files in the sidebar
   - Read the generated code
   - Check for any validation warnings

5. **Edit** - Modify files if needed:
   - Click "Edit" button on any file
   - Make changes
   - Save changes

### Example Prompts

#### Blog API
```
Create a blog API with:
- Posts (title, content, author)
- Comments (text, author)
- Users with JWT authentication
- Full CRUD operations
- Timestamps for all models
```

#### E-commerce API
```
Build an e-commerce API with:
- Products (name, price, stock)
- Orders (status, total)
- Users with login
- Shopping cart
- Full CRUD for products
```

#### Task Manager
```
Create a task management API with:
- Users with authentication
- Projects/Categories
- Tasks (title, description, status)
- Task assignments
- Timestamps and completion tracking
```

## 🏗️ Project Structure

```
coding_assistant/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── routes/
│   │   ├── api.py              # API endpoints
│   │   └── ui.py               # UI routes
│   ├── ai/
│   │   ├── llm.py              # Ollama integration
│   │   ├── prompt_builder.py   # Prompt engineering
│   │   └── parser.py           # LLM output parsing
│   ├── generator/
│   │   ├── validator.py        # Code validation
│   │   ├── cleaner.py          # Code formatting
│   │   └── file_writer.py      # File generation
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── results.html
│   │   ├── error.html
│   │   └── about.html
│   └── static/                 # CSS, JS
│       ├── style.css
│       └── app.js
├── services/
│   └── generator_service.py    # Core orchestration
├── config/
│   └── settings.py             # Configuration
├── utils/
│   ├── logger.py               # Logging
│   ├── errors.py               # Custom exceptions
│   └── helpers.py              # Utility functions
├── generated_projects/         # Generated projects (created automatically)
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

Create or edit `.env`:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
OLLAMA_TIMEOUT=120

# Application
DEBUG=true
MAX_PROMPT_SIZE=2000
GENERATED_PROJECTS_DIR=./generated_projects
```

### Settings File

Edit `config/settings.py` for advanced configuration:

```python
# Database settings
DATABASE_URL = "sqlite:///./test.db"

# Validation settings
MAX_FILE_SIZE = 500000  # 500KB

# Model selection
OLLAMA_FALLBACK_MODEL = "qwen2.5-coder:3b"
```

## 🧪 Testing

### Run Tests

```bash
pytest tests/
```

### Test with Coverage

```bash
pytest tests/ --cov=app
```

### Run Specific Test

```bash
pytest tests/test_parser.py::test_parse_structured_output
```

## 🔒 Security

The application includes multiple security layers:

1. **Code Validation**
   - Syntax checking with AST parsing
   - Security pattern detection
   - Forbidden operation blocking

2. **File Operation Protection**
   - Path traversal prevention
   - Safe file writes
   - Directory isolation

3. **Input Validation**
   - Prompt size limits
   - Filename sanitization
   - Type checking

## 📊 API Endpoints

### Generation
- `POST /api/generate` - Generate API from prompt
- `GET /api/projects/{project_id}` - Get project info
- `GET /api/projects/{project_id}/files/{filename}` - Get file content
- `PUT /api/projects/{project_id}/files/{filename}` - Edit file
- `POST /api/projects/{project_id}/regenerate/{filename}` - Regenerate file

### UI Routes
- `GET /` - Home page
- `POST /generate` - Form submission
- `GET /results/{project_id}` - Results page
- `GET /api-reference` - API documentation
- `GET /about` - About page

### Health
- `GET /health` - Health check

## 🐛 Troubleshooting

### Ollama Not Found

**Error**: `Failed to connect to Ollama at http://localhost:11434`

**Solution**:
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, check connection
curl http://localhost:11434/api/tags
```

### Model Not Available

**Error**: `model "qwen2.5-coder:7b" not found`

**Solution**:
```bash
# Pull the model
ollama pull qwen2.5-coder:7b

# List available models
ollama list
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Use a different port
uvicorn main:app --port 8001
```

### Slow Generation

**Cause**: Large model or slow hardware

**Solution**:
- Use smaller model: `qwen2.5-coder:3b`
- Increase timeout in `.env`
- Add more RAM
- Use GPU if available

## 🚀 Advanced Usage

### Using Different Models

Edit `.env`:
```env
OLLAMA_MODEL=qwen2.5-coder:3b   # Faster but less accurate
OLLAMA_MODEL=deepseek-coder:6.7b  # Alternative model
```

### Custom Prompt Rules

Edit `app/ai/prompt_builder.py` to add custom generation rules.

### Extend Validation

Edit `app/generator/validator.py` to add custom validation checks.

## 📈 Performance Tips

1. **Use GPU** - Ollama supports GPU acceleration
2. **Smaller Model** - qwen2.5-coder:3b is faster
3. **More RAM** - 16GB+ recommended for 7B model
4. **Increase Timeout** - For slow hardware
5. **Cache Models** - Keep models in memory

## 🤝 Contributing

To extend the project:

1. Add new validators in `app/generator/validator.py`
2. Extend prompt rules in `app/ai/prompt_builder.py`
3. Add new templates in `app/templates/`
4. Create new API endpoints in `app/routes/api.py`

## 📝 License

This project is provided as-is for educational and development purposes.

## 🎯 Roadmap

- [ ] React frontend code generation
- [ ] Docker support
- [ ] Cloud deployment (Railway, Vercel)
- [ ] Database migration generation
- [ ] Project versioning
- [ ] Team collaboration
- [ ] Multi-language support
- [ ] Performance optimization

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review example prompts
3. Check Ollama logs
4. Ensure dependencies are installed correctly

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- AI powered by [Ollama](https://ollama.ai)
- Models from [Qwen](https://github.com/QwenLM/Qwen) and [DeepSeek](https://github.com/deepseek-ai/deepseek-coder)

---

**Happy API Building! 🚀**

