#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

uv run python -c "
from application.extractors.data_ingestion import run_ingestion
from application.extractors.jsearch.jsearch_data_ingestion_config import RESOURCES

run_ingestion(RESOURCES, ['jsearch'])
"
