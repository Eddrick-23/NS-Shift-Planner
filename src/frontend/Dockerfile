# Build stage - uses uv for dependency installation
FROM python:3.13-slim AS builder

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY src/frontend/pyproject.toml src/frontend/uv.lock /app/

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# distroless image for runtime
FROM nvcr.io/nvidia/distroless/python:3.13-v3.0.11 AS runtime-nvidia

# Set working directory
WORKDIR /app

# Copy the virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/frontend ./src/frontend

# Add the virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8080

CMD ["python", "-m", "src.frontend.main"]
