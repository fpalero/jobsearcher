import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.service.extractors.data_ingestion import run_ingestion
from app.service.extractors.linkedin.linkedin_data_ingestion_config import RESOURCES
from app.service.extractors.linkedin.linkedin_extractor import fetch_linkedin_jobs


def test_extractor_parses_response():
    results = fetch_linkedin_jobs("Senior Software Engineer Java", dry_run=True)
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["id"] == "test-001"
    assert results[1]["id"] == "test-002"


def test_config_params_match_extractor_signature():
    import inspect
    sig = inspect.signature(fetch_linkedin_jobs)
    config = RESOURCES["linkedin"]
    for target in config["targets"]:
        for key in target["params"]:
            if key == "dry_run":
                continue
            assert key in sig.parameters, (
                f"Config key '{key}' not found in fetch_linkedin_jobs() parameters "
                f"for query '{target['query']}'. "
                f"Available: {list(sig.parameters.keys())}"
            )


def test_ingestion_flow():
    config = RESOURCES["linkedin"]
    for target in config["targets"]:
        target["params"]["dry_run"] = True
    run_ingestion(RESOURCES, ["linkedin"])


if __name__ == "__main__":
    test_extractor_parses_response()
    print("✓ extractor_parses_response")

    test_config_params_match_extractor_signature()
    print("✓ config_params_match_extractor_signature")

    print("\n--- Ejecutando ingestion dry-run ---")
    test_ingestion_flow()
    print("✓ ingestion_flow")
