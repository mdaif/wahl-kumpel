FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app

WORKDIR /app
RUN uv sync --frozen --no-cache

EXPOSE 80

CMD ["/app/.venv/bin/fastapi", "run", "/app/src/me/daif/main.py", "--port", "80", "--host", "0.0.0.0"]
