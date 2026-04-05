# Elicitation Patterns — overseerr-mcp

## Skill trigger phrases

The `skills/overseerr/SKILL.md` defines trigger phrases that cause Claude to invoke the skill:

- "request movie", "request TV show"
- "add to Plex", "search Overseerr"
- "request media", "find movie", "find TV show"
- "what's available on Plex"
- "submit media request"
- "get movie details", "get TV show details"
- "list failed requests"
- Mentions of Overseerr, Plex media requests, or wanting to watch something
- Discovering a movie/show during research and wanting to request it

## Workflow guidance

### Search-first pattern

Always search before requesting. The TMDB ID from search results is required by all other tools.

```
User: "I want to watch Dune: Part Two"
→ search_media(query="Dune: Part Two")
→ get_movie_details(tmdb_id=693134)   # confirm correct title
→ request_movie(tmdb_id=693134)        # submit request
```

### TV season scoping

When requesting TV shows, check seasons first to avoid requesting specials or unwanted content:

```
User: "Request Breaking Bad seasons 1-3"
→ search_media(query="Breaking Bad", media_type="tv")
→ get_tv_show_details(tmdb_id=1396)    # see available seasons
→ request_tv_show(tmdb_id=1396, seasons=[1, 2, 3])
```

### Error recovery

When a tool returns an error string, report the error to the user with context:

```
"Error: Overseerr API request failed (409)" → "That title has already been requested."
"Error: Overseerr API request failed (401)" → "The Overseerr API key may be invalid."
```

## Mode detection

The skill supports two modes:

1. **MCP mode** (preferred): Use `mcp__overseerr-mcp__*` tools when available
2. **HTTP fallback mode**: Use `curl` with `$CLAUDE_PLUGIN_OPTION_OVERSEERR_URL` and `$CLAUDE_PLUGIN_OPTION_OVERSEERR_API_KEY`

Check for MCP tools first; fall back to HTTP if unavailable.

## Help tool

Call `overseerr_help()` to get the full built-in help document. Useful when unsure about parameters or workflow.
