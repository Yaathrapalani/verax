# Use official Python 3.11 slim image
FROM python:3.11-slim

# Prevent Python from writing bytecode and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency definition files
COPY pyproject.toml requirements.txt uv.lock* ./

# Install Python dependencies reproducibly
RUN uv pip install --system -r requirements.txt

# Copy application source code, dataset, and artifacts
COPY src/ ./src/
COPY data/ ./data/
COPY artifacts/ ./artifacts/
COPY frontend_demo_summary.json ./

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "src.foulx.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
