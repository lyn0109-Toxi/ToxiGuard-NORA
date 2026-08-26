#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/scripts/publish_to_github.sh" "$@"
