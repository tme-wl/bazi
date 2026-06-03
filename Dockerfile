# syntax=docker/dockerfile:1
# Bazi Mingyi — multi-stage Docker image

# ---- Stage 1: Build frontend ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY web/frontend/package*.json ./
RUN npm ci
COPY web/frontend/ ./
RUN npm run build

# ---- Stage 2: Run backend ----
FROM python:3.11-slim
WORKDIR /app

# Install runtime deps
COPY web/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy core skill
COPY skill/ ./skill/

# Copy built frontend
COPY --from=frontend-builder /app/dist ./web/frontend/dist

# Copy server
COPY web/server.py ./web/

# Default port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

CMD ["uvicorn", "web.server:app", "--host", "0.0.0.0", "--port", "8000"]
