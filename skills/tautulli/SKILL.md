---
name: tautulli
description: Monitor and analyze Plex Media Server usage via Tautulli analytics API. Use when the user asks to "check Tautulli", "Plex analytics", "watch statistics", "viewing trends", "watch time", "who's been watching", "Plex history", "watch history", "most watched", "user activity", "library stats", "plays by platform", "stream analytics", "concurrent streams", "stream limit", "how many streams", "transcode vs direct play", or mentions Tautulli/Plex monitoring and analytics. Prefer this over the plex skill for historical data, usage trends, and statistics.
---

# Tautulli Analytics Skill

Monitor and analyze Plex Media Server usage through Tautulli's comprehensive analytics API. Track current streams, historical playback data, user activity, and library statistics.

## Purpose

This skill provides **read-only** access to Tautulli analytics:
- Monitor current activity and active streams
- View playback history with detailed filtering
- Track user statistics and viewing patterns
- Analyze library statistics and popular content
- View recently added media with metadata
- Monitor concurrent stream limits and bandwidth
- Analyze usage by time, platform, and stream type
- Track server and library performance metrics

All operations are **GET-only** and safe for monitoring and analytics.

**Note:** This skill complements the `plex` skill by adding analytics and historical data that Plex Media Server doesn't expose directly.

## Setup

Add credentials to `~/.config/overseerr-mcp/.env` (or `~/.config/overseerr-mcp/.env`). Run the `config-media-stack` skill to configure automatically.

```bash
# Tautulli Analytics
TAUTULLI_URL="http://192.168.1.100:8181"
TAUTULLI_API_KEY="<your_tautulli_api_key>"
```

- `TAUTULLI_URL`: Your Tautulli server URL with port (default: 8181)
- `TAUTULLI_API_KEY`: Your Tautulli API key

**Getting your API key:**
1. Open Tautulli web UI
2. Go to Settings → Web Interface → API
3. Enable "API enabled"
4. Copy the API key
5. Optionally set API HTTP Basic Authentication if desired

## Commands

All commands use the `tautulli-api` wrapper script and return JSON output.

The helper script is located at: `skills/tautulli/scripts/tautulli-api`

### Server Information

Get server identity and version:

```bash
bash skills/tautulli/scripts/tautulli-api server-info
```

### Current Activity

Monitor active streams and current playback:

```bash
# All active sessions
bash skills/tautulli/scripts/tautulli-api activity
```

**Returns:** Current streams with user, media, player, bandwidth, transcode info

### Playback History

View historical playback data:

```bash
# Recent history (default: 25 items)
bash skills/tautulli/scripts/tautulli-api history

# History with filters
bash skills/tautulli/scripts/tautulli-api history --user "username" --limit 50
bash skills/tautulli/scripts/tautulli-api history --days 7 --media-type movie
bash skills/tautulli/scripts/tautulli-api history --section-id 1 --limit 100

# Search history
bash skills/tautulli/scripts/tautulli-api history --search "Inception"
```

**Parameters:**
- `--user <username>`: Filter by username
- `--section-id <id>`: Filter by library section
- `--media-type <type>`: Filter by movie, episode, track, etc.
- `--days <n>`: History from last N days
- `--limit <n>`: Maximum results (default: 25)
- `--search <query>`: Search in titles

### User Statistics

Track user activity and viewing patterns:

```bash
# List all users (no args calls get_users — a user list, not watch statistics)
bash skills/tautulli/scripts/tautulli-api user-stats

# Per-user watch statistics (requires --user or --sort-by)
bash skills/tautulli/scripts/tautulli-api user-stats --user "username"

# Top users by play count
bash skills/tautulli/scripts/tautulli-api user-stats --sort-by plays --limit 10
```

**Parameters:**
- `--user <username>`: Specific user statistics
- `--sort-by <metric>`: Sort by plays, duration, last_seen
- `--limit <n>`: Maximum results
- `--days <n>`: Stats from last N days

### Library Statistics

Analyze library usage and popular content:

```bash
# All library sections
bash skills/tautulli/scripts/tautulli-api libraries

# Specific library stats
bash skills/tautulli/scripts/tautulli-api library-stats --section-id 1

# Popular content — media-type selects the stat (movie, show, or music)
bash skills/tautulli/scripts/tautulli-api popular --section-id 1 --limit 10
bash skills/tautulli/scripts/tautulli-api popular --media-type movie --days 30
bash skills/tautulli/scripts/tautulli-api popular --media-type show --days 30
```

**Parameters:**
- `--section-id <id>`: Specific library section
- `--media-type <type>`: `movie` (default), `show`, or `music` — selects which popularity stat to query
- `--days <n>`: Timeframe for popularity
- `--limit <n>`: Maximum results

### Recently Added

View recently added media with rich metadata:

```bash
# Recently added (default: 25 items)
bash skills/tautulli/scripts/tautulli-api recent

# Recent with filters
bash skills/tautulli/scripts/tautulli-api recent --section-id 1 --limit 50
bash skills/tautulli/scripts/tautulli-api recent --media-type movie --days 7
```

### Home Statistics

Get homepage dashboard statistics:

```bash
# Overview stats (most popular, most active, etc.)
bash skills/tautulli/scripts/tautulli-api home-stats

# Stats for specific timeframe
bash skills/tautulli/scripts/tautulli-api home-stats --days 30
```

### Stream Analytics

Analyze stream types and platform usage:

```bash
# Plays by stream type (direct/transcode)
bash skills/tautulli/scripts/tautulli-api plays-by-stream --days 30

# Plays by platform
bash skills/tautulli/scripts/tautulli-api plays-by-platform --days 30

# Plays by date/time
bash skills/tautulli/scripts/tautulli-api plays-by-date --days 30
bash skills/tautulli/scripts/tautulli-api plays-by-hour --days 7
bash skills/tautulli/scripts/tautulli-api plays-by-day --days 30
```

### Concurrent Streams

Monitor concurrent stream patterns by stream type (direct play vs transcode):

```bash
bash skills/tautulli/scripts/tautulli-api concurrent-streams --days 30
bash skills/tautulli/scripts/tautulli-api concurrent-streams --days 7
```

### Media Metadata

Get detailed metadata for specific media:

```bash
# By rating key
bash skills/tautulli/scripts/tautulli-api metadata --rating-key 12345

# By GUID
bash skills/tautulli/scripts/tautulli-api metadata --guid "plex://movie/5d776..."
```

## Workflow

When the user asks about Plex analytics:

1. **"Who's watching right now?"** → Run `activity`
2. **"What are the most watched movies?"** → Run `popular --media-type movie --days 30`
3. **"Show me recent watch history"** → Run `history --limit 25`
4. **"How much has [user] watched this week?"** → Run `user-stats --user "username" --days 7`
5. **"What's new in my library?"** → Run `recent --limit 10`
6. **"When do people watch most?"** → Run `plays-by-hour --days 30`
7. **"Are we hitting stream limits?"** → Run `concurrent-streams --days 7`

### Activity Monitoring Flow

1. Check current activity for active streams
2. If issues detected (buffering, transcoding), investigate specific session
3. Review user's watch history to understand patterns
4. Check library statistics to identify popular content
5. Analyze stream types to optimize server settings

### Analytics Flow

1. Get home statistics for overview
2. Drill into specific libraries with library-stats
3. Identify popular content with popular command
4. Analyze user behavior with user-stats
5. Review temporal patterns with plays-by-hour/date/day
6. Monitor platform distribution with plays-by-platform

## Output Format

All commands return JSON with standard Tautulli response structure:

```json
{
  "response": {
    "result": "success",
    "message": null,
    "data": { ... }
  }
}
```

Use `jq` to extract and format data:

```bash
# Get just the data
bash skills/tautulli/scripts/tautulli-api activity | jq '.response.data'

# Extract specific fields
bash skills/tautulli/scripts/tautulli-api history | jq '.response.data.data[] | {user: .friendly_name, title: .full_title, date: .date}'
```

## Notes

- Requires network access to your Tautulli server
- All operations are **read-only GET requests**
- Tautulli must be connected to your Plex Media Server
- Library section IDs match Plex library section keys
- Historical data depends on Tautulli's configured retention period
- Some statistics require sufficient historical data to be meaningful
- Response times may vary based on database size and query complexity
- Rating keys are Plex's unique identifiers for media items
- User-friendly names are shown by default (can show usernames with flags)

## Integration with Plex Skill

This skill complements the `plex` skill:

- **Plex skill**: Real-time server state (libraries, search, sessions)
- **Tautulli skill**: Historical analytics (trends, statistics, watch history)

Use both together:
1. Find content with `plex` skill search
2. Check popularity with `tautulli` skill analytics
3. Monitor current playback with either skill
4. Analyze viewing patterns with `tautulli` skill

## Multiple Servers

To use multiple Tautulli instances (monitoring different Plex servers):

```bash
# Use server 1 (default — from ~/.config/overseerr-mcp/.env)
bash skills/tautulli/scripts/tautulli-api activity

# Use a different server (inline env override)
TAUTULLI_URL="http://server2:8181" TAUTULLI_API_KEY="key2" \
  bash skills/tautulli/scripts/tautulli-api activity
```

The plugin config only supports one Tautulli instance. Multiple-server usage requires inline env overrides as shown above.

## Reference

- [Tautulli API Documentation](https://github.com/Tautulli/Tautulli/wiki/Tautulli-API-Reference)
- [Tautulli GitHub](https://github.com/Tautulli/Tautulli)
- [Tautulli Homepage](https://tautulli.com)

For detailed API reference, see:
- **[API Endpoints](./references/api-endpoints.md)** - Complete endpoint reference with parameters
- **[Quick Reference](./references/quick-reference.md)** - Common operations with copy-paste examples
- **[Troubleshooting](./references/troubleshooting.md)** - Authentication, connection, and error solutions

---

## Agent Tool Usage Requirements

When running script commands via the zsh tool, always pass `pty: true` — without it, command output will be suppressed even though the command executes successfully.
