# Q-DNA Quick Start Guide

## Prerequisites

Before running the project, ensure you have:

1. **Docker & Docker Compose** installed
2. **Ollama** installed and running locally
3. **Git** for cloning the repository

## Setup Steps

### 1. Install and Start Ollama

```bash
# Install Ollama (if not installed)
# macOS/Linux:
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download

# Pull required models
ollama pull llama3.2-vision:11b
ollama pull llama3.1:8b

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### 2. Clone and Setup Project

```bash
git clone <your-repo-url>
cd q-dna

# Environment files are already created (.env)
# Check backend/.env and frontend/.env if needed
```

### 3. Option A: Run with Docker Compose (Recommended)

```bash
# Start all services
docker-compose up --build

# Wait for services to start...
# Backend will be at: http://localhost:8000
# Frontend will be at: http://localhost:5173
```

### 4. Option B: Run Locally (Development)

#### Backend

```bash
# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install Tesseract OCR
# macOS:
brew install tesseract tesseract-lang

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-kor tesseract-ocr-eng

# Install dependencies and run
cd backend
poetry install
poetry run alembic upgrade head
poetry run python -m scripts.seed_database
poetry run uvicorn app.main:app --reload

# API will be at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

#### Frontend

```bash
cd frontend
npm install
npm run dev

# UI will be at: http://localhost:5173
```

### 5. Seed Database

```bash
# If running with Docker
docker-compose exec backend python -m scripts.seed_database

# If running locally
cd backend
poetry run python -m scripts.seed_database
```

## Testing the System

### 1. Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "ollama": "connected"
}
```

### 2. Test AI Tagging

```bash
curl -X GET "http://localhost:8000/api/v1/tags/suggest?text=이차방정식을 풀어라: x^2 - 5x + 6 = 0"
```

### 3. Browse API Documentation

Visit: http://localhost:8000/docs

### 4. Use the Frontend

Visit: http://localhost:5173

- **Dashboard**: View statistics
- **Question Editor**: Create questions with AI auto-tagging
- **Analytics**: View student performance (mock data)

## Key Features Now Working

✅ **Real AI Integration**
- OCR: Tesseract + Ollama vision (llama3.2-vision)
- Auto-tagging: Ollama text model (llama3.1:8b)
- Metadata generation: Curriculum mapping, difficulty estimation

✅ **Database Integration**
- PostgreSQL with ltree for hierarchical curriculum
- Real BKT (Bayesian Knowledge Tracing) implementation
- Student mastery tracking

✅ **API Endpoints**
- `POST /api/v1/questions/` - Create question
- `GET /api/v1/questions/` - List questions
- `GET /api/v1/curriculum/tree` - Get curriculum tree
- `GET /api/v1/tags/suggest?text=...` - AI tag suggestions
- `POST /api/v1/analytics/attempt` - Submit attempt, update BKT
- `GET /api/v1/analytics/report/{user_id}` - Get user analytics
- `GET /api/v1/analytics/recommend/{user_id}` - Get recommendations

✅ **Frontend**
- Material-UI based dashboard
- Question editor with AI integration
- Analytics visualization (Nivo charts)
- Real API connectivity

## Troubleshooting

### Ollama Not Connected

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

### Database Connection Failed

```bash
# Check PostgreSQL
docker-compose ps postgres

# View logs
docker-compose logs postgres
```

### Poetry/Dependencies Issues

```bash
cd backend
rm poetry.lock
poetry install --no-cache
```

### Frontend Build Issues

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Development Workflow

1. **Backend changes**: Auto-reload with `--reload` flag
2. **Frontend changes**: Hot Module Replacement (HMR) enabled
3. **Database changes**: Create migration with `alembic revision --autogenerate -m "message"`
4. **Add new models**: Pull with `ollama pull <model-name>`

## Project Structure

```
q-dna/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, DB setup
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # AI services (Ollama, OCR, Tagging, Analytics)
│   │   └── main.py
│   ├── scripts/          # Seed data, utilities
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml
└── QUICKSTART.md
```

## Next Steps

1. **Customize Curriculum**: Edit `backend/scripts/seed_database.py`
2. **Add More Questions**: Use the Question Editor UI
3. **Fine-tune AI**: Adjust prompts in `backend/app/services/tagging_service.py`
4. **Deploy**: Use Docker Compose for production deployment

## Support

- API Docs: http://localhost:8000/docs
- Issues: Check backend logs with `docker-compose logs backend`
- Ollama Status: `ollama list` to see installed models
