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

SEEKB_MODE = os.getenv("SEEKB_MODE", "embedded")
SEEKB_PATH = str(DATA_DIR / "seekdb")
SEEKB_HOST = os.getenv("SEEKB_HOST", "localhost")
SEEKB_PORT = int(os.getenv("SEEKB_PORT", "2881"))

POWERCONTEXT_DB_PATH = str(DATA_DIR / "powercontext")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
