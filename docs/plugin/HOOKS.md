# Hooks — overseerr-mcp

## Configuration

File: `hooks/hooks.json`

```json
{
  "description": "Sync userConfig credentials to .env and enforce permissions",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/sync-env.sh", "timeout": 10},
          {"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/ensure-gitignore.sh", "timeout": 5}
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit|Bash",
        "hooks": [
          {"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/fix-env-perms.sh", "timeout": 5},
          {"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/ensure-gitignore.sh", "timeout": 5}
        ]
      }
    ]
  }
}
```

## Hook scripts

### sync-env.sh (SessionStart)

Syncs `userConfig` values from Claude Code plugin settings into the project `.env` file.

**Managed variables:**

| userConfig key | Env variable |
| --- | --- |
| `CLAUDE_PLUGIN_OPTION_OVERSEERR_URL` | `OVERSEERR_URL` |
| `CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY` | `OVERSEERR_API_KEY` |
| `CLAUDE_PLUGIN_OPTION_OVERSEERR_MCP_URL` | `OVERSEERR_MCP_URL` |
| `CLAUDE_PLUGIN_OPTION_OVERSEERR_MCP_TOKEN` | `OVERSEERR_MCP_TOKEN` |

Behavior:
- Creates `.env` if missing
- Backs up existing `.env` before modifying (keeps 3 most recent)
- Uses file locking (`flock`) for concurrent safety
- Sets `chmod 600` on `.env` and backups

### ensure-gitignore.sh (SessionStart, PostToolUse)

Ensures `.gitignore` contains required patterns:

```
.env
.env.*
!.env.example
backups/*
!backups/.gitkeep
logs/*
!logs/.gitkeep
```

### fix-env-perms.sh (PostToolUse)

Runs after Write, Edit, MultiEdit, or Bash tool use. If the tool touched a `.env` file, resets permissions to `chmod 600` on `.env` and all backup files.

Reads the tool call from stdin JSON to determine if `.env` was affected.

### ensure-ignore-files.sh (PostToolUse)

Full ignore-files checker for both `.gitignore` and `.dockerignore`. In hook context, runs in auto-fix mode (appends missing patterns).

## Script permissions

All hook scripts must be executable:

```bash
chmod +x hooks/scripts/*.sh
```

Ensure hook scripts have executable permissions.
