---
name: sabnzbd
description: Manage Usenet downloads with SABnzbd. Use when the user asks to "check SABnzbd", "list NZB queue", "add NZB", "pause downloads", "resume downloads", "SABnzbd status", "Usenet queue", "NZB history", "retry failed downloads", "what's the download speed", "clear the queue", "failed NZBs", or mentions SABnzbd/sab/Usenet download management.
---

# SABnzbd API

Manage Usenet downloads via SABnzbd's REST API.

## Purpose

This skill provides **read and write** access to your SABnzbd Usenet downloader:
- Monitor download queue and history
- Add NZB files by URL or upload
- Control downloads (pause, resume, delete)
- Adjust download speed limits
- Manage categories and post-processing scripts
- Retry failed downloads
- View server statistics and warnings

Operations include both read and write actions. **Always confirm before deleting downloads with file deletion.**

## Setup

Credentials: `~/.config/overseerr-mcp/.env` (or `~/.config/overseerr-mcp/.env`). Run the `config-media-stack` skill to configure automatically.

```bash
SABNZBD_URL="http://localhost:8080"
SABNZBD_API_KEY="your-api-key-from-config-general"
```

Get your API key from SABnzbd Config → General → Security.

**Security:** Never commit `.env` file. Set permissions: `chmod 600 "~/.config/overseerr-mcp/.env"`

## Quick Reference

### Queue Status

```bash
# Full queue
bash skills/sabnzbd/scripts/sab-api queue

# With filters
bash skills/sabnzbd/scripts/sab-api queue --limit 10 --category tv

# Specific job
bash skills/sabnzbd/scripts/sab-api queue --nzo-id SABnzbd_nzo_xxxxx
```

### Add NZB

```bash
# By URL (indexer link)
bash skills/sabnzbd/scripts/sab-api add "https://indexer.com/get.php?guid=..."

# With options
bash skills/sabnzbd/scripts/sab-api add "URL" --name "My Download" --category movies --priority high

# By local file
bash skills/sabnzbd/scripts/sab-api add-file /path/to/file.nzb --category tv
```

Priority: `force`, `high`, `normal`, `low`, `paused`, `duplicate`

### Control Queue

```bash
bash skills/sabnzbd/scripts/sab-api pause              # Pause all
bash skills/sabnzbd/scripts/sab-api resume             # Resume all
bash skills/sabnzbd/scripts/sab-api pause-job <nzo_id>
bash skills/sabnzbd/scripts/sab-api resume-job <nzo_id>
bash skills/sabnzbd/scripts/sab-api delete <nzo_id>    # Keep files
bash skills/sabnzbd/scripts/sab-api delete <nzo_id> --files  # Delete files too
bash skills/sabnzbd/scripts/sab-api purge              # Clear queue
```

### Speed Control

```bash
bash skills/sabnzbd/scripts/sab-api speedlimit 50      # 50% of max
bash skills/sabnzbd/scripts/sab-api speedlimit 5M      # 5 MB/s
bash skills/sabnzbd/scripts/sab-api speedlimit 0       # Unlimited
```

### History

```bash
bash skills/sabnzbd/scripts/sab-api history
bash skills/sabnzbd/scripts/sab-api history --limit 20 --failed
bash skills/sabnzbd/scripts/sab-api retry <nzo_id>     # Retry failed
bash skills/sabnzbd/scripts/sab-api retry-all          # Retry all failed
bash skills/sabnzbd/scripts/sab-api delete-history <nzo_id>
bash skills/sabnzbd/scripts/sab-api rename <nzo_id> "New Name" [password]
```

### Categories & Scripts

```bash
bash skills/sabnzbd/scripts/sab-api categories
bash skills/sabnzbd/scripts/sab-api scripts
bash skills/sabnzbd/scripts/sab-api change-category <nzo_id> movies
bash skills/sabnzbd/scripts/sab-api change-script <nzo_id> notify.py
```

### Status & Info

```bash
bash skills/sabnzbd/scripts/sab-api status             # Full status
bash skills/sabnzbd/scripts/sab-api version
bash skills/sabnzbd/scripts/sab-api warnings
bash skills/sabnzbd/scripts/sab-api warnings-clear     # Clear all warnings
bash skills/sabnzbd/scripts/sab-api server-stats       # Download stats
```

### Job Management

```bash
bash skills/sabnzbd/scripts/sab-api change-category <nzo_id> movies
bash skills/sabnzbd/scripts/sab-api change-priority <nzo_id> high
```

## Response Format

Queue slot includes:
- `nzo_id`, `filename`, `status`
- `mb`, `mbleft`, `percentage`
- `timeleft`, `priority`, `cat`
- `script`, `labels`

Status values: `Downloading`, `Queued`, `Paused`, `Propagating`, `Fetching`

History status: `Completed`, `Failed`, `Queued`, `Verifying`, `Repairing`, `Extracting`

## Workflow

When the user asks about Usenet downloads:

1. **"What's downloading?"** → Run `queue` to show active downloads
2. **"Add this NZB"** → Run `add "<url>"` with appropriate category and priority
3. **"Pause all downloads"** → Run `pause`
4. **"Resume downloads"** → Run `resume`
5. **"Show download history"** → Run `history`
6. **"Retry failed downloads"** → Run `retry-all` or `retry <nzo_id>`
7. **"Slow down downloads"** → Run `speedlimit <percentage>` or `speedlimit <MB>M`

**Important:** Always confirm before deleting jobs with `--files` — this permanently removes downloaded data.

## Notes

- Requires network access to your SABnzbd server
- Uses SABnzbd API (v2+)
- All data operations return JSON
- **Delete operations with --files are permanent** - always confirm before deleting downloaded files
- Speed limits can be percentage (of configured max) or absolute values
- NZB files can be added by URL (indexer links) or local file upload
- Post-processing scripts are executed after download completion

---

## Agent Tool Usage Requirements

When running script commands via the zsh tool, always pass `pty: true` — without it, command output will be suppressed even though the command executes successfully.
