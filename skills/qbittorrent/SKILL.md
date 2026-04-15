---
name: qbittorrent
description: Manage torrents with qBittorrent. Use when the user asks to "list torrents", "what's seeding", "torrent stuck", "torrent stalled", "reannounce torrent", "tracker not responding", "unstick torrent", "clear completed torrents", "add torrent", "pause torrent", "resume torrent", "delete torrent", "check download status", "torrent speed", "qBittorrent stats", or mentions qBittorrent/qbit torrent management.
---

# qBittorrent WebUI API

Manage torrents via qBittorrent's WebUI API (v4.1+).

## Purpose

This skill provides **read and write** access to your qBittorrent torrent client:
- Monitor active, seeding, and completed torrents
- Add torrents by magnet link, URL, or file upload
- Control torrent state (pause, resume, delete)
- Manage categories and tags
- Adjust global and per-torrent speed limits
- View torrent files, trackers, and properties
- Recheck torrent data integrity

Operations include both read and write actions. **Always confirm before deleting torrents with file deletion.**

## Setup

Add credentials to `~/.config/overseerr-mcp/.env` (or `~/.config/overseerr-mcp/.env`). Run the `config-media-stack` skill to configure automatically.

```bash
QBITTORRENT_URL="http://localhost:8080"
QBITTORRENT_USERNAME="admin"
QBITTORRENT_PASSWORD="adminadmin"
```

Set file permissions:
```bash
chmod 600 "~/.config/overseerr-mcp/.env"
```

## Quick Reference

### List Torrents

```bash
# All torrents
bash skills/qbittorrent/scripts/qbit-api list

# Filter by status
bash skills/qbittorrent/scripts/qbit-api list --filter downloading
bash skills/qbittorrent/scripts/qbit-api list --filter seeding
bash skills/qbittorrent/scripts/qbit-api list --filter paused

# Filter by category
bash skills/qbittorrent/scripts/qbit-api list --category movies
```

Filters: `all`, `downloading`, `seeding`, `completed`, `paused`, `active`, `inactive`, `stalled`, `stalled_uploading`, `stalled_downloading`, `errored`

### Get Torrent Info

```bash
bash skills/qbittorrent/scripts/qbit-api info <hash>
bash skills/qbittorrent/scripts/qbit-api files <hash>
bash skills/qbittorrent/scripts/qbit-api trackers <hash>
```

### Add Torrent

```bash
# By magnet or URL
bash skills/qbittorrent/scripts/qbit-api add "magnet:?xt=..." --category movies

# By file
bash skills/qbittorrent/scripts/qbit-api add-file /path/to/file.torrent --paused
```

### Control Torrents

```bash
bash skills/qbittorrent/scripts/qbit-api pause <hash>           # or "all"
bash skills/qbittorrent/scripts/qbit-api resume <hash>          # or "all"
bash skills/qbittorrent/scripts/qbit-api delete <hash>          # keep files
bash skills/qbittorrent/scripts/qbit-api delete <hash> --files  # delete files too
bash skills/qbittorrent/scripts/qbit-api recheck <hash>
bash skills/qbittorrent/scripts/qbit-api reannounce <hash>      # re-announce to trackers (unstick stalled)
```

### Categories & Tags

```bash
bash skills/qbittorrent/scripts/qbit-api categories
bash skills/qbittorrent/scripts/qbit-api tags
bash skills/qbittorrent/scripts/qbit-api set-category <hash> movies
bash skills/qbittorrent/scripts/qbit-api add-tags <hash> "important,archive"
bash skills/qbittorrent/scripts/qbit-api remove-tags <hash> "important"
```

### Transfer Info

```bash
bash skills/qbittorrent/scripts/qbit-api transfer          # global speed/stats
bash skills/qbittorrent/scripts/qbit-api speedlimit        # current limits
bash skills/qbittorrent/scripts/qbit-api set-speedlimit --down 5M --up 1M
bash skills/qbittorrent/scripts/qbit-api toggle-alt-speed  # toggle alternative speed limits
```

### App Info

```bash
bash skills/qbittorrent/scripts/qbit-api version
bash skills/qbittorrent/scripts/qbit-api preferences
```

## Response Format

Torrent object includes:
- `hash`, `name`, `state`, `progress`
- `dlspeed`, `upspeed`, `eta`
- `size`, `downloaded`, `uploaded`
- `category`, `tags`, `save_path`

States: `downloading`, `stalledDL`, `uploading`, `stalledUP`, `pausedDL`, `pausedUP`, `queuedDL`, `queuedUP`, `checkingDL`, `checkingUP`, `error`, `missingFiles`

## Workflow

When the user asks about torrents:

1. **"What's downloading?"** → Run `list --filter downloading`
2. **"Add this magnet link"** → Run `add "<magnet>"` with appropriate category
3. **"Pause all torrents"** → Run `pause all`
4. **"Resume seeding"** → Run `resume all` or filter by hash
5. **"Show torrent details"** → Run `info <hash>` and `files <hash>`
6. **"List by category"** → Run `list --category movies`
7. **"Set speed limits"** → Run `set-speedlimit --down 5M --up 1M`

## Notes

- Requires network access to your qBittorrent server
- Uses qBittorrent WebUI API v4.1+
- All data operations return JSON
- **Delete operations with --files are permanent** - always confirm before deleting downloaded files
- Speed limits support units: K (KB/s), M (MB/s), or raw bytes
- Magnet links and torrent URLs are added without local file upload
- Categories must exist before assignment (create via WebUI or API)

---

## Agent Tool Usage Requirements

When running script commands via the zsh tool, always pass `pty: true` — without it, command output will be suppressed even though the command executes successfully.

### Scripts

| Script | Purpose |
|--------|---------|
| `qbit-api` | Main API wrapper — use this directly when `pty: true` is set in the zsh tool |
| `qbit-api-wrapper` | PTY shim for environments without PTY support — not needed when using `pty: true` |
