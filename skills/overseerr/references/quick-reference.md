# Overseerr Quick Reference

All script examples use `./skills/overseerr/scripts/overseerr-api` (from plugin root).

---

## Common Workflow

```bash
# 1. Search to find TMDB ID
./skills/overseerr/scripts/overseerr-api search "Inception"
# → "1. movie: Inception (2010) - https://www.themoviedb.org/movie/27205"

# 2. Check details / confirm not already requested
./skills/overseerr/scripts/overseerr-api movie 27205

# 3. Submit request
./skills/overseerr/scripts/overseerr-api request-movie 27205

# 4. Verify (use the request ID from step 3 output)
./skills/overseerr/scripts/overseerr-api request <request-id>
```

---

## Search & Details

```bash
# Search (formatted, numbered list with TMDB links)
./skills/overseerr/scripts/overseerr-api search "The Matrix"

# Search (raw JSON — pipe to jq)
./skills/overseerr/scripts/overseerr-api search-json "Dune" | jq '.results[] | {id, title, mediaType}'

# Movie details (title, year, overview, request status)
./skills/overseerr/scripts/overseerr-api movie 603

# TV show details (seasons, episode counts, request status)
./skills/overseerr/scripts/overseerr-api tv 1399

# Movie recommendations / similar
./skills/overseerr/scripts/overseerr-api movie-recommendations 603
./skills/overseerr/scripts/overseerr-api movie-similar 603

# Rotten Tomatoes / IMDB / TMDB ratings for a movie
./skills/overseerr/scripts/overseerr-api movie-ratings 603

# TV recommendations / similar
./skills/overseerr/scripts/overseerr-api tv-recommendations 1399
./skills/overseerr/scripts/overseerr-api tv-similar 1399

# Season/episode details
./skills/overseerr/scripts/overseerr-api tv-season 1399 1

# Actor/director details (use person ID from TMDB)
./skills/overseerr/scripts/overseerr-api person 6384
```

---

## Discover

```bash
# Trending movies and TV (mixed)
./skills/overseerr/scripts/overseerr-api trending

# Discover movies (optional filters)
./skills/overseerr/scripts/overseerr-api discover-movies
./skills/overseerr/scripts/overseerr-api discover-movies --sort popularity.desc
./skills/overseerr/scripts/overseerr-api discover-movies --genre 28 --sort vote_average.desc
./skills/overseerr/scripts/overseerr-api discover-movies --page 2

# Discover TV shows (same flags as discover-movies, plus --network)
./skills/overseerr/scripts/overseerr-api discover-tv
./skills/overseerr/scripts/overseerr-api discover-tv --sort popularity.desc --page 1

# Upcoming movies / TV
./skills/overseerr/scripts/overseerr-api upcoming-movies
./skills/overseerr/scripts/overseerr-api upcoming-tv

# Plex watchlist
./skills/overseerr/scripts/overseerr-api watchlist
```

---

## Requests

```bash
# Summary counts (pending / approved / declined / processing / available)
./skills/overseerr/scripts/overseerr-api request-count

# List requests (defaults: 20 results, all statuses)
./skills/overseerr/scripts/overseerr-api requests
./skills/overseerr/scripts/overseerr-api requests --filter pending
./skills/overseerr/scripts/overseerr-api requests --filter approved --take 50
./skills/overseerr/scripts/overseerr-api requests --filter failed --sort modified
./skills/overseerr/scripts/overseerr-api requests --user 1              # by user ID
# Filter values: all pending approved declined available failed processing

# Get a single request by ID
./skills/overseerr/scripts/overseerr-api request 42

# Create requests
./skills/overseerr/scripts/overseerr-api request-movie 603
./skills/overseerr/scripts/overseerr-api request-tv 1399               # all seasons
./skills/overseerr/scripts/overseerr-api request-tv 1399 --season 1
./skills/overseerr/scripts/overseerr-api request-tv 1399 --season 1 --season 2 --season 3

# Approve / decline (admin API key required)
./skills/overseerr/scripts/overseerr-api approve 42
./skills/overseerr/scripts/overseerr-api decline 42

# Retry a failed request
./skills/overseerr/scripts/overseerr-api retry 42

# Update a request (change seasons, server, quality profile, root folder)
./skills/overseerr/scripts/overseerr-api update-request 42 --season 1 --season 2
./skills/overseerr/scripts/overseerr-api update-request 42 --server 1 --profile 4 --root /movies

# Delete a request (destructive — confirm with user first)
./skills/overseerr/scripts/overseerr-api delete-request 42

# Failed requests shorthand
./skills/overseerr/scripts/overseerr-api failed-requests
./skills/overseerr/scripts/overseerr-api failed-requests --take 25
./skills/overseerr/scripts/overseerr-api failed-requests --sort modified
./skills/overseerr/scripts/overseerr-api failed-requests --sort added --take 50
```

---

## Media

```bash
# List media items
./skills/overseerr/scripts/overseerr-api media
./skills/overseerr/scripts/overseerr-api media --filter available --take 50
./skills/overseerr/scripts/overseerr-api media --filter processing
# Filter values: available partial processing pending unknown

# Update media status (admin only)
./skills/overseerr/scripts/overseerr-api media-status <media-id> available

# Watch / playback data for a media item
./skills/overseerr/scripts/overseerr-api watch-data <media-id>

# Delete a media item (admin only, destructive)
./skills/overseerr/scripts/overseerr-api delete-media <media-id>
```

---

## Users

```bash
# List users
./skills/overseerr/scripts/overseerr-api users
./skills/overseerr/scripts/overseerr-api users --take 5 --sort displayName

# Get user details
./skills/overseerr/scripts/overseerr-api user 1

# Get user request quotas (movie/TV limits and usage)
./skills/overseerr/scripts/overseerr-api user-quota 1

# Get requests for a specific user
./skills/overseerr/scripts/overseerr-api user-requests 1
./skills/overseerr/scripts/overseerr-api user-requests 1 --take 10 --skip 0
```

---

## Issues

```bash
# List issues
./skills/overseerr/scripts/overseerr-api issues
./skills/overseerr/scripts/overseerr-api issues --filter open
./skills/overseerr/scripts/overseerr-api issues --filter resolved --take 20
# Filter values: open resolved

# Get a single issue
./skills/overseerr/scripts/overseerr-api issue 7

# Create an issue
# Types: 1=video  2=audio  3=subtitle  4=other
./skills/overseerr/scripts/overseerr-api create-issue <media-id> 1 "Subtitles missing on episode 3"
./skills/overseerr/scripts/overseerr-api create-issue <media-id> 4 "Wrong movie version downloaded"

# Resolve / close an issue
./skills/overseerr/scripts/overseerr-api resolve-issue 7
./skills/overseerr/scripts/overseerr-api close-issue 7
```

---

## MCP Tools (when server is running)

```
search_media           query, [media_type]
get_movie_details      tmdb_id
get_tv_show_details    tmdb_id
request_movie          tmdb_id
request_tv_show        tmdb_id, [seasons]
list_failed_requests   [count], [skip]
overseerr_help         (returns available tool descriptions)
```

See [capability-map.md](./capability-map.md) for full MCP vs script coverage.
