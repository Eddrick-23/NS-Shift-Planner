FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY src/backend/pyproject.toml src/backend/uv.lock ./
RUN uv sync --frozen --no-dev

#distroless image for runtime
FROM nvcr.io/nvidia/distroless/python:3.13-v3.0.11 AS runtime-nvidia

WORKDIR /app

# Copy the virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

COPY src/__init__.py ./src/
COPY src/backend/ ./src/backend/


# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["fastapi", "run","src/backend/app.py", "--port", "8000"]

