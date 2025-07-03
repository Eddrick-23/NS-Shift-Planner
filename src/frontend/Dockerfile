FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

COPY .env .env
COPY src/frontend ./src/frontend

EXPOSE 8080
CMD ["uv", "run", "-m", "src.frontend.main"]
