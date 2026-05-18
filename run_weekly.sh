#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

uv run python -m application.extractors.data_ingestion
