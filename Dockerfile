# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Set uv environment variables
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies (this will create the lock file and install deps)
RUN uv sync --no-install-project

# Copy source code and configuration
COPY src/ src/
COPY config/ config/

# Install the project in development mode
RUN uv pip install -e .

# Create directories for persistent data
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8001 8002

# Copy and set up startup script
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src:/app
ENV PYTHONUNBUFFERED=1

# Default command
ENTRYPOINT ["./docker-entrypoint.sh"]
