FROM python:3.12.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get -o Acquire::Retries=5 update \
    && apt-get -o Acquire::Retries=5 install -y --no-install-recommends libgomp1 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
ARG PIP_INDEX_URL=https://pypi.org/simple
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --timeout 120 --retries 5 --index-url "$PIP_INDEX_URL" -r backend/requirements.txt

# Bake pyseekdb's all-MiniLM-L6-v2 ONNX model into the image (no runtime download).
RUN python -c "from pyseekdb import DefaultEmbeddingFunction; DefaultEmbeddingFunction()(['warmup'])"

COPY backend backend
COPY scripts scripts
COPY demo-data demo-data
COPY .env.example .env.example

EXPOSE 8000

CMD ["bash", "-lc", "cd backend && PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000"]
