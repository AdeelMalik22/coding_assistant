# 🚀 Quick Reference Guide

## Installation (30 seconds)

### Linux/Mac
```bash
cd /home/adeel/coding_assistant
./setup.sh
```

### Windows
```cmd
cd C:\path\to\coding_assistant
setup.bat
```

---

## Start Services (3 commands)

### Terminal 1 - Ollama
```bash
ollama serve
# Output: Listening on 127.0.0.1:11434 (http)
```

### Terminal 2 - Application
```bash
cd app
python -m uvicorn main:app --reload
# Output: Uvicorn running on http://0.0.0.0:8000
```

### Terminal 3 - Done!
Open browser: **http://localhost:8000**

---

## Usage (3 steps)

1. **Write Prompt**
   ```
   "Create a blog API with posts and comments using JWT"
   ```

2. **Select Features**
   - [ ] JWT Authentication
   - [x] CRUD Operations
   - [x] User Model
   - [x] Database

3. **Click Generate** → View Results

---

## File Locations

| What | Where |
|------|-------|
| Backend | `app/main.py` |
| API Routes | `app/routes/api.py` |
| UI Routes | `app/routes/ui.py` |
| Templates | `app/templates/` |
| Styling | `app/static/style.css` |
| AI Integration | `app/ai/llm.py` |
| Code Generator | `services/generator_service.py` |
| Generated Projects | `generated_projects/` |
| Config | `config/settings.py` |
| Environment | `.env` |

---

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Home page |
| `/api/generate` | POST | Generate API |
| `/api/projects/{id}` | GET | Get project |
| `/api/projects/{id}/files/{name}` | PUT | Edit file |
| `/results/{id}` | GET | View results |
| `/api-reference` | GET | API docs |
| `/health` | GET | Health check |

---

## Example Prompts

### Blog API
```
Create a blog API with posts and comments. 
Include JWT authentication, CRUD operations for posts and comments.
```

### E-commerce
```
Build an e-commerce backend with products, orders, and shopping cart.
Include user authentication and order tracking.
```

### Task Manager
```
Create a task management API with projects, tasks, and assignments.
Include user accounts with different roles.
```

---

## Troubleshooting

### Ollama Not Running
```bash
# Check connection
curl http://localhost:11434/api/tags

# Start service
ollama serve
```

### Model Missing
```bash
# Pull model
ollama pull qwen2.5-coder:7b

# List models
ollama list
```

### Port in Use
```bash
# Use different port
uvicorn main:app --port 8001
```

### Generation Slow
- Use smaller model: `qwen2.5-coder:3b`
- Increase RAM allocation
- Simplify your prompt
- Enable GPU in Ollama

---

## Configuration Files

### .env
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
DEBUG=true
```

### config/settings.py
```python
DEBUG = True
MAX_PROMPT_SIZE = 2000
OLLAMA_TIMEOUT = 120
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_core.py::TestPromptBuilder -v

# With coverage
pytest tests/ --cov=app
```

---

## Project Structure

```
app/
├── main.py                 # FastAPI app
├── routes/
│   ├── api.py             # API endpoints
│   └── ui.py              # UI routes
├── ai/
│   ├── llm.py             # Ollama client
│   ├── prompt_builder.py  # Prompts
│   └── parser.py          # Parse LLM output
├── generator/
│   ├── validator.py       # Validation
│   ├── cleaner.py         # Formatting
│   └── file_writer.py     # File generation
├── templates/             # HTML files
└── static/                # CSS, JS
```

---

## Common Tasks

### Generate API
```bash
# Via Web UI
1. Go to http://localhost:8000
2. Enter prompt
3. Click Generate

# Via API
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create user API",
    "jwt_auth": true,
    "crud_operations": true
  }'
```

### View Generated Code
```bash
# Via Web UI
http://localhost:8000/results/{project_id}

# Via API
curl http://localhost:8000/api/projects/{project_id}
```

### Edit Generated File
```bash
# Via Web UI
1. Click Edit button on file
2. Make changes
3. Click Save

# Via API
curl -X PUT http://localhost:8000/api/projects/{project_id}/files/models.py \
  -H "Content-Type: application/json" \
  -d '{"content": "..."}'
```

---

## Performance Tips

1. **Faster Generation**
   - Use `qwen2.5-coder:3b` instead of 7b
   - Shorter prompts
   - Enable GPU acceleration
   - More RAM

2. **Better Quality**
   - Use `qwen2.5-coder:7b`
   - Detailed prompts
   - Specific requirements
   - Clear examples

---

## Advanced Usage

### Use Different Model
Edit `.env`:
```env
OLLAMA_MODEL=deepseek-coder:6.7b
```

### Increase Timeout
Edit `.env`:
```env
OLLAMA_TIMEOUT=300  # 5 minutes
```

### Change Output Directory
Edit `.env`:
```env
GENERATED_PROJECTS_DIR=/path/to/projects
```

---

## Debug Mode

Enable verbose logging:
```env
DEBUG=true
```

View logs in terminal running the app.

---

## Browser Support

- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

---

## Dependencies

```
FastAPI==0.104.1
Uvicorn==0.24.0
Pydantic==2.5.0
Jinja2==3.1.2
HTTPx==0.25.2
SQLAlchemy==2.0.23
```

Full list: `requirements.txt`

---

## Getting Help

1. Check README.md
2. View PROJECT_SUMMARY.md
3. Try examples in `tests/test_core.py`
4. Check API Reference at `/api-reference`

---

## Next Steps

1. ✅ Run setup script
2. ✅ Start Ollama
3. ✅ Start application
4. ✅ Generate your first API
5. ✅ Review and customize
6. ✅ Deploy (see README.md Phase 3)

---

## Tips & Tricks

- **Cache models** - Ollama keeps models in memory
- **Batch generation** - Generate multiple APIs
- **Save projects** - Generated files stay in `generated_projects/`
- **Customize** - Edit templates and routes as needed
- **Test thoroughly** - Validate generated code before use

---

**Happy Building! 🚀**

