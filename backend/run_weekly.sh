#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

bash application/cron/jsearch_cron.sh

# Run transformation pipeline (applicable → technologies → match)
uv run python -m application.service.transformation
