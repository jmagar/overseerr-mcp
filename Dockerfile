FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid mcpuser --shell /bin/bash --create-home mcpuser

RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

RUN chmod +x entrypoint.sh && \
    mkdir -p /app/logs /app/backups && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

EXPOSE 9151

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget -qO- http://localhost:9151/health || exit 1

ENV OVERSEERR_MCP_HOST=0.0.0.0
ENV OVERSEERR_MCP_PORT=9151
ENV OVERSEERR_MCP_TRANSPORT=http

CMD ["./entrypoint.sh"]
