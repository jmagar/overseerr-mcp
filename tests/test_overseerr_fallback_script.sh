#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/skills/overseerr/scripts/overseerr-api"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

assert_eq() {
    local actual="$1"
    local expected="$2"
    local message="$3"

    if [[ "$actual" != "$expected" ]]; then
        echo "ASSERTION FAILED: $message" >&2
        echo "Expected: $expected" >&2
        echo "Actual:   $actual" >&2
        exit 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="$3"

    if [[ "$haystack" != *"$needle"* ]]; then
        echo "ASSERTION FAILED: $message" >&2
        echo "Missing: $needle" >&2
        echo "In: $haystack" >&2
        exit 1
    fi
}

cat >"$TMPDIR/load-env" <<'EOF'
#!/usr/bin/env bash
load_service_credentials() {
    export OVERSEERR_URL="http://overseerr.test"
    export OVERSEERR_API_KEY="test-api-key"
}
EOF
chmod +x "$TMPDIR/load-env"

cat >"$TMPDIR/curl" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

method="GET"
data=""
args=("$@")
i=0
while [[ $i -lt ${#args[@]} ]]; do
    arg="${args[$i]}"
    case "$arg" in
        -X)
            i=$((i + 1))
            method="${args[$i]}"
            ;;
        -d|--data|--data-raw)
            i=$((i + 1))
            data="${args[$i]}"
            ;;
    esac
    i=$((i + 1))
done

url="${args[$((${#args[@]} - 1))]}"
printf '%s %s\n' "$method" "$url" >>"$TEST_LOG"
if [[ -n "$data" ]]; then
    printf 'DATA %s\n' "$data" >>"$TEST_LOG"
fi

case "$method $url" in
    "GET http://overseerr.test/api/v1/search?query=The%20Matrix")
        cat <<'JSON'
{"results":[{"id":603,"mediaType":"movie","title":"The Matrix","releaseDate":"1999-03-30","mediaInfo":{"status":3}},{"id":1399,"mediaType":"tv","name":"Game of Thrones","firstAirDate":"2011-04-17","mediaInfo":{"status":4}},{"id":287,"mediaType":"person","name":"Brad Pitt"}]}
JSON
        ;;
    "GET http://overseerr.test/api/v1/movie/603")
        cat <<'JSON'
{"id":603,"mediaInfo":{"status":3},"request":[{"id":88}],"title":"The Matrix"}
JSON
        ;;
    "GET http://overseerr.test/api/v1/tv/1399")
        cat <<'JSON'
{"id":1399,"mediaInfo":{"status":4},"numberOfSeasons":8,"request":[{"id":99}],"name":"Game of Thrones"}
JSON
        ;;
    "GET http://overseerr.test/api/v1/request?filter=failed&take=10&skip=5&sort=added")
        cat <<'JSON'
{"results":[{"id":77,"type":"movie","media":{"tmdbId":603,"title":"The Matrix"}}]}
JSON
        ;;
    "POST http://overseerr.test/api/v1/request")
        printf '%s\n' "$data"
        ;;
    *)
        echo "{\"error\":\"unexpected request\",\"method\":\"$method\",\"url\":\"$url\"}" >&2
        exit 1
        ;;
esac
EOF
chmod +x "$TMPDIR/curl"

export PATH="$TMPDIR:$PATH"
export TEST_LOG="$TMPDIR/requests.log"

search_output="$("$SCRIPT_PATH" search "The Matrix")"
assert_contains "$search_output" "1. movie: The Matrix (1999) - https://www.themoviedb.org/movie/603" "search should format movie results"
assert_contains "$search_output" "2. tv: Game of Thrones (2011) - https://www.themoviedb.org/tv/1399" "search should format tv results"

movie_output="$("$SCRIPT_PATH" movie 603)"
assert_eq "$movie_output" '{"id":603,"mediaInfo":{"status":3},"request":[{"id":88}],"title":"The Matrix"}' "movie should return raw JSON"

tv_output="$("$SCRIPT_PATH" tv 1399)"
assert_eq "$tv_output" '{"id":1399,"mediaInfo":{"status":4},"numberOfSeasons":8,"request":[{"id":99}],"name":"Game of Thrones"}' "tv should return raw JSON"

request_movie_output="$("$SCRIPT_PATH" request-movie 603)"
assert_eq "$request_movie_output" '{"mediaType":"movie","mediaId":603}' "request-movie should post expected payload"

request_tv_output="$("$SCRIPT_PATH" request-tv 1399 --season 1 --season 3)"
assert_eq "$request_tv_output" '{"mediaType":"tv","mediaId":1399,"seasons":[1,3]}' "request-tv should post explicit seasons"

request_tv_all_output="$("$SCRIPT_PATH" request-tv 1399)"
assert_eq "$request_tv_all_output" '{"mediaType":"tv","mediaId":1399,"seasons":"all"}' "request-tv should default to all seasons"

failed_output="$("$SCRIPT_PATH" failed-requests --take 10 --skip 5 --sort added)"
assert_eq "$failed_output" '{"results":[{"id":77,"type":"movie","media":{"tmdbId":603,"title":"The Matrix"}}]}' "failed-requests should return raw JSON"

request_log="$(cat "$TEST_LOG")"
assert_contains "$request_log" 'GET http://overseerr.test/api/v1/search?query=The%20Matrix' "search endpoint should be called"
assert_contains "$request_log" 'DATA {"mediaType":"tv","mediaId":1399,"seasons":[1,3]}' "season request payload should be logged"

echo "test_overseerr_fallback_script.sh: PASS"
