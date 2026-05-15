#!/usr/bin/env bash
# vercel_deploy.sh — wrapper Vercel CLI con error handling per /web-builder
#
# Tier 2 fallback (CLI). Per Tier 1 (MCP) usa direttamente MCP tools.
# Per Tier 3 (token) chiama questo script con VERCEL_TOKEN env set.
#
# Usage:
#   bash vercel_deploy.sh init <project_path>           # init project link
#   bash vercel_deploy.sh deploy <project_path> [--prod]
#   bash vercel_deploy.sh env-add <project_path> <KEY> <ENV>  # ENV: preview|production|all
#   bash vercel_deploy.sh smoke-test <url>

set -euo pipefail

ACTION="${1:-}"
shift || true

err() {
    printf '{"status":"error","message":"%s"}\n' "$1" >&2
    exit 1
}

require_vercel_cli() {
    command -v vercel >/dev/null 2>&1 || err "vercel CLI not installed. Run: npm i -g vercel"
}

vercel_login_check() {
    # Check if logged in (auth.json exists)
    if ! vercel whoami >/dev/null 2>&1; then
        if [[ -z "${VERCEL_TOKEN:-}" ]]; then
            err "Not logged in. Run: vercel login (browser OAuth) — OR set VERCEL_TOKEN env var"
        fi
    fi
}

case "$ACTION" in
    init)
        project_path="${1:-}"
        [[ -z "$project_path" ]] && err "Missing project_path"
        require_vercel_cli
        vercel_login_check
        cd "$project_path"
        vercel link --yes 2>&1 | tee /tmp/vercel-link.log
        printf '{"status":"linked","project_path":"%s","log":"/tmp/vercel-link.log"}\n' "$project_path"
        ;;

    deploy)
        project_path="${1:-}"
        [[ -z "$project_path" ]] && err "Missing project_path"
        prod_flag=""
        if [[ "${2:-}" == "--prod" ]]; then
            prod_flag="--prod"
        fi
        require_vercel_cli
        vercel_login_check
        cd "$project_path"

        # Pre-deploy gate
        if ! npm run build >/tmp/vercel-build.log 2>&1; then
            err "Build failed. Check /tmp/vercel-build.log"
        fi

        deploy_url="$(vercel deploy $prod_flag --yes 2>&1 | tail -1)"
        printf '{"status":"deployed","url":"%s","prod":%s}\n' "$deploy_url" \
            "$( [[ -n "$prod_flag" ]] && echo true || echo false )"
        ;;

    env-add)
        project_path="${1:-}"
        key="${2:-}"
        env="${3:-preview}"
        [[ -z "$project_path" || -z "$key" ]] && err "Usage: env-add <project_path> <KEY> [preview|production|all]"
        require_vercel_cli
        vercel_login_check
        cd "$project_path"

        # Interactive: prompts for value
        # User must paste value securely (NO bash arg pass)
        echo "Insert value for $key (in $env). Press Enter when done:" >&2
        vercel env add "$key" "$env"
        printf '{"status":"env_added","key":"%s","env":"%s"}\n' "$key" "$env"
        ;;

    smoke-test)
        url="${1:-}"
        [[ -z "$url" ]] && err "Missing URL"

        status="$(curl -s -o /dev/null -w "%{http_code}" -L -m 10 "$url" || echo "000")"
        time_ms="$(curl -s -o /dev/null -w "%{time_total}" -L -m 10 "$url" 2>/dev/null \
            | awk '{printf "%.0f", $1 * 1000}')"

        if [[ "$status" == "200" ]]; then
            printf '{"status":"ok","http_status":%d,"time_ms":%d,"url":"%s"}\n' \
                "$status" "${time_ms:-0}" "$url"
        else
            printf '{"status":"fail","http_status":%d,"url":"%s"}\n' "$status" "$url"
            exit 1
        fi
        ;;

    *)
        err "Unknown action '$ACTION'. Use: init | deploy | env-add | smoke-test"
        ;;
esac
