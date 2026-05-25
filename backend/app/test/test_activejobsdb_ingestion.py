import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.service.extractors.data_ingestion import run_ingestion
from app.service.extractors.activejobsdb.activejobsdb_data_ingestion_config import RESOURCES
from app.service.extractors.activejobsdb.activejobsdb_extractor import fetch_activejobsdb_jobs


def test_extractor_parses_response():
    results = fetch_activejobsdb_jobs("Senior Software Engineer Java", dry_run=True)
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["id"] == "test-001"
    assert results[1]["id"] == "test-002"


def test_extractor_returns_empty_list_on_dry_run_without_file():
    original_dry_run = fetch_activejobsdb_jobs.__globals__.get("SAMPLE_PATH")
    if original_dry_run and not original_dry_run.exists():
        results = fetch_activejobsdb_jobs("any query", dry_run=True)
        assert results == []


def test_to_job_dto_maps_fields():
    from app.service.extractors.activejobsdb.toJobDto import to_job_dto
    raw = {
        "id": "test-001",
        "title": "Senior Software Engineer",
        "organization": "Test Company",
        "locations_derived": ["Berlin, Germany"],
        "countries_derived": ["Germany"],
        "remote_derived": True,
        "date_posted": "2026-05-25T10:00:00",
        "salary_raw": "€80k - €100k",
        "employment_type": ["FULL_TIME"],
        "url": "https://example.com/job/123",
        "source_domain": "example.com",
        "organization_logo": "https://example.com/logo.png",
        "organization_url": "https://example.com",
        "description_text": "Job description here",
        "cities_derived": ["Berlin"],
        "regions_derived": ["Berlin"],
    }
    dto = to_job_dto(raw, "Software Engineer")
    d = dto.to_dict()
    assert d["job_id"] == "test-001"
    assert d["title"] == "Senior Software Engineer"
    assert d["company"] == "Test Company"
    assert d["location"] == "Berlin, Germany"
    assert d["country"] == "Germany"
    assert d["is_remote"] is True
    assert d["posted_at"] == "2026-05-25T10:00:00"
    assert d["salary_string"] == "€80k - €100k"
    assert d["employment_type"] == "FULL_TIME"
    assert d["apply_link"] == "https://example.com/job/123"
    assert d["publisher"] == "example.com"
    assert d["employer_logo"] == "https://example.com/logo.png"
    assert d["employer_website"] == "https://example.com"
    assert d["description"] == "Job description here"
    assert d["source"] == "ActiveJobsDB"
    assert d["role_query"] == "Software Engineer"


def test_to_job_dto_handles_null_fields():
    from app.service.extractors.activejobsdb.toJobDto import to_job_dto
    raw = {
        "id": "test-002",
        "title": "Software Engineer",
        "organization": None,
        "description_text": None,
        "locations_derived": None,
        "countries_derived": None,
        "remote_derived": None,
        "date_posted": None,
        "salary_raw": None,
        "employment_type": None,
        "url": None,
        "source_domain": None,
        "organization_logo": None,
        "organization_url": None,
    }
    dto = to_job_dto(raw, "")
    d = dto.to_dict()
    assert d["job_id"] == "test-002"
    assert d["title"] == "Software Engineer"
    assert "company" not in d
    assert "description" not in d
    assert "location" not in d
    assert "country" not in d
    assert "employment_type" not in d
    assert d["source"] == "ActiveJobsDB"


def test_config_params_match_extractor_signature():
    import inspect
    sig = inspect.signature(fetch_activejobsdb_jobs)
    config = RESOURCES["activejobsdb"]
    for target in config["targets"]:
        for key in target["params"]:
            if key == "dry_run":
                continue
            assert key in sig.parameters, (
                f"Config key '{key}' not found in fetch_activejobsdb_jobs() parameters "
                f"for query '{target['query']}'. "
                f"Available: {list(sig.parameters.keys())}"
            )


def test_ingestion_flow():
    config = RESOURCES["activejobsdb"]
    for target in config["targets"]:
        target["params"]["dry_run"] = True
    run_ingestion(RESOURCES, ["activejobsdb"])


if __name__ == "__main__":
    test_extractor_parses_response()
    print("✓ extractor_parses_response")

    test_to_job_dto_maps_fields()
    print("✓ to_job_dto_maps_fields")

    test_to_job_dto_handles_null_fields()
    print("✓ to_job_dto_handles_null_fields")

    test_config_params_match_extractor_signature()
    print("✓ config_params_match_extractor_signature")

    print("\n--- Ejecutando ingestion dry-run ---")
    test_ingestion_flow()
    print("✓ ingestion_flow")
