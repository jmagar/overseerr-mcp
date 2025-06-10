#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

echo "Overseerr MCP Service: Initializing..."

# Validate required environment variables
if [ -z "$OVERSEERR_URL" ]; then
    echo "Error: OVERSEERR_URL environment variable is required"
    exit 1
fi

if [ -z "$OVERSEERR_API_KEY" ]; then
    echo "Error: OVERSEERR_API_KEY environment variable is required"
    exit 1
fi

# Set defaults for MCP server configuration
export OVERSEERR_MCP_HOST=${OVERSEERR_MCP_HOST:-"0.0.0.0"}
export OVERSEERR_MCP_PORT=${OVERSEERR_MCP_PORT:-"9151"}
export OVERSEERR_MCP_TRANSPORT=${OVERSEERR_MCP_TRANSPORT:-"sse"}
export OVERSEERR_LOG_LEVEL=${OVERSEERR_LOG_LEVEL:-"INFO"}

echo "Overseerr MCP Service: Configuration validated"
echo "  - OVERSEERR_URL: $OVERSEERR_URL"
echo "  - OVERSEERR_API_KEY: ***SET***"
echo "  - MCP_HOST: $OVERSEERR_MCP_HOST"
echo "  - MCP_PORT: $OVERSEERR_MCP_PORT"
echo "  - MCP_TRANSPORT: $OVERSEERR_MCP_TRANSPORT"
echo "  - LOG_LEVEL: $OVERSEERR_LOG_LEVEL"

# Change to app directory (important for relative path handling)
cd /app

echo "Overseerr MCP Service: Starting server..."
exec python3 overseerr-mcp-server.py 