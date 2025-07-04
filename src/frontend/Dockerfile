FROM python:3.13-slim-bookworm
# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY src/frontend/pyproject.toml uv.lock ./

RUN uv sync

COPY src/frontend ./src/frontend

EXPOSE 8080

CMD ["uv","run", "-m", "src.frontend.main"]
