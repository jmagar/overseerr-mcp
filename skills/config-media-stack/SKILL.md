---
name: homelab-setup
description: "Credential setup and diagnostics for the overseerr-mcp media stack. Automatically extracts API keys from service config files (local or via SSH) and writes them to the plugin credential store. Use when the user asks to 'setup credentials', 'configure plex', 'add my API key', 'setup media stack', 'authentication failed', 'API key not working', '401 error', '403 forbidden', 'why isn't X working', 'check my credentials', 'did my keys get extracted', or mentions any of the 8 bundled services (Plex, Overseerr, Radarr, Sonarr, Prowlarr, Tautulli, SABnzbd, qBittorrent) in a setup or authentication context."
---

# Media Stack Credential Setup

You manage credentials for 8 media services in `~/.config/overseerr-mcp/.env`. The goal is to get that file fully populated with minimal manual input — most API keys can be extracted automatically from service config files.

## How automatic extraction works

If the user set `appdata_path` in the plugin config UI (e.g. `/mnt/cache/appdata` or `myserver:/mnt/cache/appdata`), the `ConfigChange` hook already ran `extract-keys` when the plugin was enabled. Keys for Radarr, Sonarr, Prowlarr, Overseerr, Tautulli, SABnzbd, and Plex may already be populated — check before asking the user for anything.

All commands below assume the **plugin root** as the working directory.

## Step 1: Diagnose current state

Read the `.env` and report what's populated vs missing:

```bash
grep -E "^(PLEX|OVERSEERR|RADARR|SONARR|PROWLARR|TAUTULLI|SABNZBD|QBITTORRENT)_(URL|TOKEN|API_KEY|USERNAME|PASSWORD)=" \
  "~/.config/overseerr-mcp/.env" 2>/dev/null \
  | sed 's/=.*/=<set>/' \
  || echo "File missing or empty"
```

Also check for placeholder values that weren't replaced:
```bash
grep "your_" "~/.config/overseerr-mcp/.env" 2>/dev/null || true
```

If most keys are already set and only a few are missing, skip straight to those. If the file is missing or empty, bootstrap it first:

```bash
cp skills/config-media-stack/references/.env.example \
   "~/.config/overseerr-mcp/.env"
chmod 600 "~/.config/overseerr-mcp/.env"
```

## Step 2: Run extraction (if keys are missing)

If keys weren't auto-extracted (file is fresh, or `appdata_path` wasn't set), ask the user:

> 1. Are your services running on this machine or a remote host?
>    - If remote: what hostname? (must be in `~/.ssh/config` with key auth)
> 2. What is the base appdata path? (e.g. `/mnt/cache/appdata` or `/mnt/user/appdata`)

Then run extraction:

```bash
# Local
bash skills/config-media-stack/scripts/extract-keys \
  --appdata /mnt/cache/appdata \
  --env-file "~/.config/overseerr-mcp/.env"

# Remote
bash skills/config-media-stack/scripts/extract-keys \
  --host myserver \
  --appdata /mnt/cache/appdata \
  --env-file "~/.config/overseerr-mcp/.env"
```

The script cats each config file (via SSH if remote) and parses locally — credentials never travel as parsed values. It reports what it found and what it missed.

## Step 3: Manual entry for what extraction can't get

Never ask the user to paste credentials into the chat. For anything that wasn't auto-extracted, tell the user which key is missing, where to find it, and have them edit the file directly:

```bash
${EDITOR:-nano} "~/.config/overseerr-mcp/.env"
```

**qBittorrent** — password is stored as a salted hash; can't be extracted. Tell the user:
> Add your plaintext username and password to `~/.config/overseerr-mcp/.env`:
> ```
> QBITTORRENT_USERNAME=your_username
> QBITTORRENT_PASSWORD=your_password
> ```

**Plex token** — only extractable if Plex runs in Docker with the appdata volume mounted. If it wasn't found, tell the user:
> 1. Open Plex Web → any media item → ⋮ → Get Info → View XML
> 2. Copy the `X-Plex-Token` value from the URL
> 3. Add it to `~/.config/overseerr-mcp/.env`: `PLEX_TOKEN=your_token`

**Any other missing key** — tell the user which service, where to find the key (Settings → General → API Key for all \*arr apps and Overseerr, Settings → Web Interface for Tautulli, Config → General for SABnzbd), and that they should add it directly to the `.env` file. Do not ask them to paste it here.

## Step 4: Verify

Run the pre-flight check — it validates all env vars are set, tests connectivity and auth for each service, and checks container status if `appdata_path` is configured:

```bash
preflight   # bin/preflight — installed on PATH by the plugin
```

Any failures will be reported with the specific reason (missing var, auth error, unreachable). Fix those and re-run until all checks pass.

## Reconfiguration

To update a single key without touching anything else:
```bash
sed -i "s|^RADARR_API_KEY=.*|RADARR_API_KEY=newvalue|" "~/.config/overseerr-mcp/.env"
chmod 600 "~/.config/overseerr-mcp/.env"
```

To re-run full extraction (e.g. after a service reinstall):
```bash
bash skills/config-media-stack/scripts/extract-keys \
  --host myserver \
  --appdata /mnt/cache/appdata \
  --env-file "~/.config/overseerr-mcp/.env"
```

To update URLs, change them in the Claude Code plugin config UI — the `ConfigChange` hook writes them to `.env` automatically.

## Security rules

- Never print, echo, or display full credential values
- Always `chmod 600 "~/.config/overseerr-mcp/.env"` after any write
- If the user accidentally pastes a credential in chat, acknowledge it and don't repeat it back
