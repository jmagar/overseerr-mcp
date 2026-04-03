# Overseerr MCP Server

> **Intelligent media discovery and request management for Overseerr via the Model Context Protocol.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![Python Version](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-Enabled-brightgreen.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

---

## ✨ Overview
Overseerr MCP provides direct interaction with your Overseerr instance. It allows AI assistants to search for movies and TV shows, retrieve deep metadata, and manage media requests through natural language.

### 🎯 Key Features
| Feature | Description |
|---------|-------------|
| **Unified Search** | Search for movies or TV shows across TMDB |
| **Request Management** | Seamlessly request media with season-level granularity |
| **Failure Tracking** | Identify and list failed requests for troubleshooting |
| **Metadata Rich** | Retrieve TMDB-backed details for any media item |

---

## 🎯 Claude Code Integration
The easiest way to use this plugin is through the Claude Code marketplace:

```bash
# Add the marketplace
/plugin marketplace add jmagar/claude-homelab

# Install the plugin
/plugin install overseerr-mcp @jmagar-claude-homelab
```

---

## ⚙️ Configuration & Credentials
Credentials follow the standardized `homelab-core` pattern.

**Location:** `~/.claude-homelab/.env`

### Required Variables
```bash
OVERSEERR_URL="http://your-overseerr-url:5055"
OVERSEERR_API_KEY="your-api-key"
OVERSEERR_MCP_TRANSPORT="stdio" # Recommended for Claude Desktop
OVERSEERR_LOG_LEVEL="INFO"
```

> **Security Note:** Never commit `.env` files. Ensure permissions are set to `chmod 600`.

---

## 🛠️ Available Tools

### 🔧 Primary Tools
The server exposes specific tools for media lifecycle management.

| Tool | Parameters | Description |
|------|------------|-------------|
| **`search_media`** | `query`, `media_type` | Search for movies or TV shows |
| **`get_movie_details`** | `tmdb_id` | Retrieve detailed movie metadata |
| **`get_tv_show_details`** | `tmdb_id` | Retrieve detailed TV show metadata |
| **`request_movie`** | `tmdb_id` | Request a specific movie |
| **`request_tv_show`** | `tmdb_id`, `seasons` | Request a show or specific seasons |
| **`list_failed_requests`** | `count`, `skip` | Identify requests that failed to process |

---

## 🏗️ Architecture & Design
This plugin is built as a modular FastMCP Python package:
- **Async Client:** High-performance `httpx` client for API interactions.
- **Lifespan Management:** Optimized connection pooling and resource cleanup.
- **Smart Logging:** Rotating logs to `overseerr_mcp.log` and system console.

---

## 🔧 Development
### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup
```bash
uv sync
uv run python src/overseerr-mcp/overseerr-mcp-server.py
```

### Quality Assurance
```bash
uv run ruff check .        # Linting
uv run pytest              # Unit Tests (if available)
```

---

## 🐛 Troubleshooting
| Issue | Cause | Solution |
|-------|-------|----------|
| **401 Unauthorized** | Invalid API Key | Verify `OVERSEERR_API_KEY` in settings |
| **Connection Refused** | Service Down | Verify `OVERSEERR_URL` is reachable |
| **Tool Failures** | Schema Mismatch | Check `overseerr_mcp.log` for details |

---

## 📄 License
MIT © jmagar
