"""LabTrail - AI Research Knowledge & Experiment Workspace Backend"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

SEEKDB_MODE = os.getenv("SEEKDB_MODE", "embedded")
SEEKDB_PATH = os.getenv("SEEKDB_PATH", str(DATA_DIR / "seekdb"))
SEEKDB_HOST = os.getenv("SEEKDB_HOST", "localhost")
SEEKDB_PORT = int(os.getenv("SEEKDB_PORT", "2881"))

POWERCONTEXT_URL = os.getenv("POWERCONTEXT_URL", "http://127.0.0.1:8890")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
