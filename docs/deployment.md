# Deployment Guide

## Local Development

### Prerequisites
- Python 3.12+ (recommended: install via Homebrew on macOS)
- Node.js 18+
- npm or yarn

### Setup Steps

1. **Clone and enter project directory**
```bash
cd labtrail
```

2. **Python environment**
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

3. **Frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

4. **Environment configuration**
```bash
cp .env.example .env
```

5. **Load demo data**
```bash
PYTHONPATH=backend python scripts/load_demo_data.py
```

6. **Start backend**
```bash
cd backend
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

7. **Start frontend** (new terminal)
```bash
cd frontend
npm run dev
```

8. **Access application**
Open http://localhost:5173

## Docker Deployment

### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - SEEKDB_MODE=embedded
      - SEEKDB_PATH=/app/data/seekdb

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:80"
    depends_on:
      - backend
```

### Build and Run
```bash
docker-compose up -d
```

## Qoder Sites Deployment

The frontend is deployed via Qoder Sites as a static site. The backend API is accessed via the development server or a separately hosted endpoint.

### Frontend Build
```bash
cd frontend
npm run build
```

The built files are in `frontend/dist/` and can be deployed to any static hosting service.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SEEKB_MODE` | seekdb mode: `embedded` or `server` | `embedded` |
| `SEEKB_PATH` | Path for embedded seekdb data | `./data/seekdb` |
| `SEEKB_HOST` | seekdb server host | `localhost` |
| `SEEKB_PORT` | seekdb server port | `2881` |
| `EMBEDDING_MODEL` | Sentence transformer model | `sentence-transformers/all-MiniLM-L6-v2` |
| `HOST` | Backend server host | `0.0.0.0` |
| `PORT` | Backend server port | `8000` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `OPENAI_API_KEY` | Optional LLM API key | (empty) |
| `OPENAI_BASE_URL` | Optional LLM API base URL | `https://api.openai.com/v1` |
| `LLM_MODEL` | Optional LLM model name | `gpt-4o-mini` |

## Troubleshooting

### Python version issues
- pyseekdb and powercontext require Python 3.11+
- Install Python 3.12 via Homebrew: `brew install python@3.12`

### seekdb initialization slow on first run
- The embedding model (all-MiniLM-L6-v2) is downloaded on first use
- Subsequent runs use the cached model (~86MB)

### Frontend proxy issues
- The Vite dev server proxies `/api` requests to `http://localhost:8000`
- Ensure the backend is running before starting the frontend

### Memory/disk usage
- seekdb embedded mode stores data in `backend/data/seekdb/`
- Uploaded files are stored in `backend/uploads/`
- Clear these directories to reset all data
