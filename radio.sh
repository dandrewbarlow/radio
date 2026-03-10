#!/usr/bin/env bash
# radio.sh
# Andrew Barlow
#
# Description:
#   Simple CLI internet radio player. A bash port of radio.py.
#   Uses fzf for station selection and cvlc for playback.
#
# Dependencies:
#   fzf   - fuzzy finder for station selection (https://github.com/junegunn/fzf)
#   cvlc  - command-line VLC media player (https://www.videolan.org/vlc/)
#   curl  - stream verification
#
# Usage:
#   ./radio.sh
#
# Config (config.txt):
#   Place stream URLs in config.txt next to this script, one per line.
#   Optionally precede a URL with a commented name:
#
#     # Station Name
#     https://stream-url.com
#
#   Lines not starting with "http" or "#" are ignored.
#   If no name comment is found above a URL, the URL is used as the name.

# Check that all required external tools are installed before doing anything.
check_dependencies() {
    local missing=()
    for cmd in fzf cvlc curl; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        printf "Error: missing required dependencies: %s\n" "${missing[*]}" >&2
        printf "Install them and try again.\n" >&2
        exit 1
    fi
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.txt"

# ANSI color codes
RED='\033[31m'
BLUE='\033[34m'
PURPLE='\033[35m'
RESET='\033[0m'

# Station data stored in parallel arrays, indexed together.
# names[i] and urls[i] always refer to the same station.
names=()
urls=()

# Parse config.txt into the names[] and urls[] arrays.
# For each line starting with "http", check the previous line for a "# Name"
# comment. If found, use it as the station name; otherwise fall back to the URL.
parse_stations() {
    local filepath="$1"
    local prev=""

    while IFS= read -r line; do
        if [[ "$line" == http* ]]; then
            local url="$line"
            local name
            if [[ "$prev" == "#"* ]]; then
                # Strip leading "# " or bare "#"
                name="${prev#\# }"
                name="${name#\#}"
            else
                name="$url"
            fi
            names+=("$name")
            urls+=("$url")
        fi
        prev="$line"
    done < <(tr -d '\r' < "$filepath")  # tr strips Windows-style CR line endings
}

# Check that a stream URL is reachable before handing it to VLC.
# Skips the check for local file:// URLs.
# Uses curl --head to avoid downloading the stream body.
verify_stream() {
    local url="$1"

    printf "Verifying stream...\n"

    if [[ "$url" == file://* ]]; then
        return 0
    fi

    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 --head "$url" 2>/dev/null) || true

    if [[ "$code" -ge 200 && "$code" -lt 400 ]]; then
        return 0
    else
        printf "Failed to connect to stream (HTTP %s)\n" "$code"
        return 1
    fi
}

# Print currently playing station info to the terminal.
display_info() {
    local name="$1"
    local url="$2"
    clear
    printf "\n"
    printf "  === Radio ===\n\n"
    printf "  Station : ${PURPLE}%s${RESET}\n" "$name"
    printf "  URL     : ${BLUE}%s${RESET}\n" "$url"
    printf "\n"
    printf "  Return to menu : ${RED}Ctrl+C${RESET}\n"
    printf "  Quit           : ${RED}Ctrl+C${RESET} twice\n"
    printf "\n"
}

# Verify and play a station.
# cvlc runs in the background so we can trap Ctrl+C to stop it cleanly
# and return to the station picker rather than exiting the script.
play_station() {
    local name="$1"
    local url="$2"

    if ! verify_stream "$url"; then
        sleep 2
        return 1
    fi

    display_info "$name" "$url"

    cvlc -q --intf dummy "$url" 2>/dev/null &
    local vlc_pid=$!

    # On Ctrl+C: kill cvlc, clear the trap, and return to the main loop.
    trap "kill $vlc_pid 2>/dev/null; wait $vlc_pid 2>/dev/null; trap - INT; return 1" INT

    wait $vlc_pid
    trap - INT
}

# Present the station list via fzf and return the user's choice.
# fzf exits non-zero on Esc/Ctrl+C; the caller treats that as "exit".
pick_station() {
    printf '%s\n' "${names[@]}" "Exit" \
        | fzf --prompt="Radio > " --height=40% --reverse
}

main() {
    check_dependencies

    if [[ ! -f "$CONFIG_FILE" ]]; then
        printf "Error: config file not found at %s\n" "$CONFIG_FILE" >&2
        exit 1
    fi

    parse_stations "$CONFIG_FILE"

    if [[ ${#names[@]} -eq 0 ]]; then
        printf "Error: no stations found in %s\n" "$CONFIG_FILE" >&2
        exit 1
    fi

    # Main loop: pick a station, play it, repeat.
    # Ctrl+C during playback returns here; Ctrl+C or Esc at the fzf prompt exits.
    while true; do
        clear
        local choice
        choice=$(pick_station) || true

        if [[ -z "$choice" || "$choice" == "Exit" ]]; then
            clear
            exit 0
        fi

        # Look up the URL that corresponds to the chosen station name
        local selected_url=""
        local selected_name=""
        for i in "${!names[@]}"; do
            if [[ "${names[$i]}" == "$choice" ]]; then
                selected_url="${urls[$i]}"
                selected_name="${names[$i]}"
                break
            fi
        done

        if [[ -z "$selected_url" ]]; then
            printf "Error: station not found\n" >&2
            sleep 1
            continue
        fi

        play_station "$selected_name" "$selected_url" || true
    done
}

main
