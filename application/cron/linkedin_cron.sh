#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PROJECT_ROOT="$(pwd)"

uv run python -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from application.extractors.data_ingestion import run_ingestion
from application.extractors.linkedin_data_ingestion_config import RESOURCES

run_ingestion(RESOURCES, ['linkedin'])
"
