# syntax=docker/dockerfile:1

# ── builder ──────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml uv.lock* ./
RUN touch README.md
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy source and install project
COPY overseerr_mcp/ ./overseerr_mcp/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── runtime ──────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid mcpuser --shell /bin/bash --create-home mcpuser && \
    apt-get update && apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the built venv and source from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/overseerr_mcp /app/overseerr_mcp
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Copy entrypoint
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh && \
    mkdir -p /app/logs && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

EXPOSE 9151

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OVERSEERR_MCP_HOST=0.0.0.0 \
    OVERSEERR_MCP_PORT=9151 \
    OVERSEERR_MCP_TRANSPORT=http

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget -qO- http://localhost:9151/health || exit 1

CMD ["./entrypoint.sh"]
