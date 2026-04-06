FROM python:3.12-slim

WORKDIR /app

# Install system libs needed by trafilatura and reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies from lockfile
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy app source
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

RUN mkdir -p /app/output

EXPOSE 8000
CMD ["python", "main.py"]