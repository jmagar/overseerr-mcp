---
name: prowlarr
description: Search indexers and manage Prowlarr. Use when the user asks to "search for a torrent", "search indexers", "find a release", "find releases for X", "search for a movie", "find TV show episodes", "search by IMDB ID", "search by TVDB ID", "what indexers do I have", "indexer not working", "check indexer status", "list indexers", "prowlarr search", "sync indexers", or mentions Prowlarr, indexer management, or NZB/torrent searching.
---

# Prowlarr Skill

Search across all your indexers and manage Prowlarr via API.

## Purpose

This skill provides **read and write** access to your Prowlarr indexer aggregation:
- Search for releases across all configured indexers
- Filter searches by protocol (torrent/usenet) and category
- List and monitor indexer health and statistics
- Enable/disable/delete indexers
- Sync indexer configurations to connected apps (Sonarr, Radarr)
- Test indexer connectivity

Operations include both read and write actions. **Always confirm before deleting or disabling indexers.**

## Setup

Credentials: `~/.config/overseerr-mcp/.env` (or `~/.config/overseerr-mcp/.env`). Run the `config-media-stack` skill to configure automatically.

```bash
PROWLARR_URL="http://localhost:9696"
PROWLARR_API_KEY="your-api-key"
```

Get your API key from: Prowlarr → Settings → General → Security → API Key

---

## Quick Reference

### Search Releases

```bash
# Basic search across all indexers
bash skills/prowlarr/scripts/prowlarr-api search "ubuntu 22.04"

# Search torrents only
bash skills/prowlarr/scripts/prowlarr-api search "ubuntu" --torrents

# Search usenet only
bash skills/prowlarr/scripts/prowlarr-api search "ubuntu" --usenet

# Search specific categories (2000=Movies, 5000=TV, 3000=Audio, 7000=Books)
bash skills/prowlarr/scripts/prowlarr-api search "inception" --category 2000

# TV search with TVDB ID
bash skills/prowlarr/scripts/prowlarr-api tv-search --tvdb 71663 --season 1 --episode 1

# Movie search with IMDB ID
bash skills/prowlarr/scripts/prowlarr-api movie-search --imdb tt0111161
```

### List Indexers

```bash
# All indexers
bash skills/prowlarr/scripts/prowlarr-api indexers

# With status details
bash skills/prowlarr/scripts/prowlarr-api indexers --verbose
```

### Indexer Health & Stats

```bash
# Usage stats per indexer
bash skills/prowlarr/scripts/prowlarr-api stats

# Test all indexers
bash skills/prowlarr/scripts/prowlarr-api test-all

# Test specific indexer
bash skills/prowlarr/scripts/prowlarr-api test <indexer-id>
```

### Indexer Management

```bash
# Enable/disable an indexer
bash skills/prowlarr/scripts/prowlarr-api enable <indexer-id>
bash skills/prowlarr/scripts/prowlarr-api disable <indexer-id>

# Delete an indexer
bash skills/prowlarr/scripts/prowlarr-api delete <indexer-id>
```

### App Sync

```bash
# Sync indexers to Sonarr/Radarr/etc
bash skills/prowlarr/scripts/prowlarr-api sync

# List connected apps
bash skills/prowlarr/scripts/prowlarr-api apps
```

### System

```bash
# System status
bash skills/prowlarr/scripts/prowlarr-api status

# Health check
bash skills/prowlarr/scripts/prowlarr-api health
```

---

## Search Categories

| ID | Category |
|----|----------|
| 2000 | Movies |
| 5000 | TV |
| 3000 | Audio |
| 7000 | Books |
| 1000 | Console |
| 4000 | PC |
| 6000 | XXX |

Sub-categories: 2010 (Movies/Foreign), 2020 (Movies/Other), 2030 (Movies/SD), 2040 (Movies/HD), 2045 (Movies/UHD), 2050 (Movies/BluRay), 2060 (Movies/3D), 5010 (TV/WEB-DL), 5020 (TV/Foreign), 5030 (TV/SD), 5040 (TV/HD), 5045 (TV/UHD), etc.

---

## Common Use Cases

**"Search for the latest Ubuntu ISO"**
```bash
bash skills/prowlarr/scripts/prowlarr-api search "ubuntu 24.04"
```

**"Find Game of Thrones S01E01"**
```bash
bash skills/prowlarr/scripts/prowlarr-api tv-search --tvdb 121361 --season 1 --episode 1
```

**"Search for Inception in 4K"**
```bash
bash skills/prowlarr/scripts/prowlarr-api search "inception 2160p" --category 2045
```

**"Check if my indexers are healthy"**
```bash
bash skills/prowlarr/scripts/prowlarr-api stats
bash skills/prowlarr/scripts/prowlarr-api test-all
```

**"Push indexer changes to Sonarr/Radarr"**
```bash
bash skills/prowlarr/scripts/prowlarr-api sync
```

## Workflow

When the user asks about indexers or searches:

1. **"Search for a torrent"** → Run `search "<query>"` and present results with download links
2. **"Find Breaking Bad S01E01"** → Run `tv-search --tvdb <id> --season 1 --episode 1`
3. **"Which indexers are working?"** → Run `stats` to show indexer health and usage
4. **"Test all my indexers"** → Run `test-all` to verify connectivity
5. **"Sync indexers to Sonarr"** → Run `sync` to push configuration changes
6. **"List available indexers"** → Run `indexers` or `indexers --verbose`

## Notes

- Requires network access to your Prowlarr server
- Uses Prowlarr API v1
- All data operations return JSON
- **Search operations query external indexers** - respect rate limits
- **Indexer deletion is permanent** - always confirm before removing
- Sync operations push indexer configs to all connected apps (Sonarr, Radarr, Lidarr, etc.)
- Category IDs follow Newznab/Torznab standards

---

## Agent Tool Usage Requirements

When running script commands via the zsh tool, always pass `pty: true` — without it, command output will be suppressed even though the command executes successfully.

## Reference

For detailed local reference, see:
- **[API Endpoints](./references/api-endpoints.md)** — Complete endpoint reference with parameters
- **[Quick Reference](./references/quick-reference.md)** — Common operations with copy-paste examples
- **[Troubleshooting](./references/troubleshooting.md)** — Authentication, connection, and error solutions
