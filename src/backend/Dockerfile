FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY src/backend/pyproject.toml uv.lock ./
RUN uv sync
COPY src/__init__.py ./src/
COPY src/backend/ ./src/backend/
COPY ../../secrets ./secrets

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run","src/backend/app.py"]

