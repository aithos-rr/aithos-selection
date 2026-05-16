#!/usr/bin/env bash
# cli_detect.sh — detect CLI tools required by /web-builder
#
# Output: JSON line per CLI con name + path + version (se rilevabile).
#
# Usage:
#   bash cli_detect.sh                # all CLIs
#   bash cli_detect.sh --tool vercel  # specific CLI

set -euo pipefail

TARGET_CLIS=(node npm npx git gh vercel convex supabase astro)

check_cli() {
    local cli="$1"
    local path version

    if ! command -v "$cli" >/dev/null 2>&1; then
        printf '{"name":"%s","installed":false,"path":null,"version":null}\n' "$cli"
        return
    fi

    path="$(command -v "$cli")"

    case "$cli" in
        node|npm|gh|vercel)
            version="$("$cli" --version 2>/dev/null | head -1 | tr -d '\n' || echo unknown)"
            ;;
        npx)
            version="$(npx --version 2>/dev/null | head -1 | tr -d '\n' || echo unknown)"
            ;;
        git)
            version="$(git --version 2>/dev/null | awk '{print $3}' | tr -d '\n' || echo unknown)"
            ;;
        convex|supabase|astro)
            # Possono fallire se non config — usiamo --version
            version="$("$cli" --version 2>/dev/null | head -1 | tr -d '\n' || echo unknown)"
            ;;
        *)
            version="unknown"
            ;;
    esac

    # Escape per JSON
    version="${version//\"/\\\"}"

    printf '{"name":"%s","installed":true,"path":"%s","version":"%s"}\n' \
        "$cli" "$path" "$version"
}

if [[ "${1:-}" == "--tool" && -n "${2:-}" ]]; then
    check_cli "$2"
    exit 0
fi

# Output array JSON di tutti i CLI
printf '['
first=true
for cli in "${TARGET_CLIS[@]}"; do
    if [[ "$first" == "true" ]]; then
        first=false
    else
        printf ','
    fi
    check_cli "$cli"
done
printf ']\n'
