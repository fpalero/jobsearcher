import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

MOCK_CLIENT = patch("app.core.extractor_repository.MongoClient").start()
MOCK_UNIFIED_CLIENT = patch("app.core.data_unified_repository.MongoClient").start()


def test_extractor_parses_dry_run():
    from app.service.extractors.startupremotejobs.startupremotejobs_extractor import (
        fetch_startupremotejobs_jobs,
    )

    results = fetch_startupremotejobs_jobs(title="Senior Software Engineer", dry_run=True)
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["id"] == "test-001"
    assert results[1]["id"] == "test-002"


def test_to_job_dto_maps_fields():
    from app.service.extractors.startupremotejobs.toJobDto import to_job_dto

    raw = {
        "id": "test-001",
        "title": "Senior Software Engineer",
        "startup": {
            "name": "TechStartup GmbH",
            "logo": "https://example.com/logo.png",
            "website_url": "https://techstartup.com",
        },
        "description": "We are looking for a Senior Software Engineer.",
        "remote": True,
        "salary_min": 80000,
        "salary_max": 120000,
        "jobType": "full-time",
        "location": "Berlin, Germany",
        "date": "2026-05-25T10:00:00Z",
        "url": "https://wellfound.com/jobs/123",
    }
    dto = to_job_dto(raw, "Software Engineer")
    d = dto.to_dict()
    assert d["job_id"] == "test-001"
    assert d["title"] == "Senior Software Engineer"
    assert d["company"] == "TechStartup GmbH"
    assert d["is_remote"] is True
    assert d["salary_min"] == 80000
    assert d["salary_max"] == 120000
    assert d["salary_string"] == "$80000 - $120000"
    assert d["employment_type"] == "full-time"
    assert d["location"] == "Berlin, Germany"
    assert d["apply_link"] == "https://wellfound.com/jobs/123"
    assert d["employer_logo"] == "https://example.com/logo.png"
    assert d["employer_website"] == "https://techstartup.com"
    assert d["source"] == "StartupRemoteJobs"
    assert d["role_query"] == "Software Engineer"


def test_to_job_dto_handles_null_fields():
    from app.service.extractors.startupremotejobs.toJobDto import to_job_dto

    raw = {
        "id": "test-002",
        "title": "Frontend Developer",
        "startup": None,
        "remote": None,
        "salary_min": None,
        "salary_max": None,
        "jobType": None,
        "location": None,
        "date": None,
        "url": None,
        "description": None,
    }
    dto = to_job_dto(raw, "")
    d = dto.to_dict()
    assert d["job_id"] == "test-002"
    assert d["title"] == "Frontend Developer"
    assert d["is_remote"] is True
    assert "salary_min" not in d
    assert "salary_max" not in d
    assert "employment_type" not in d
    assert "company" not in d
    assert d["source"] == "StartupRemoteJobs"


def test_to_job_dto_handles_company_as_string():
    from app.service.extractors.startupremotejobs.toJobDto import to_job_dto

    raw = {"id": "1", "title": "Engineer", "company": "Acme Corp"}
    dto = to_job_dto(raw, "")
    d = dto.to_dict()
    assert d["company"] == "Acme Corp"


def test_config_params_match_extractor_signature():
    import inspect
    from app.service.extractors.startupremotejobs.startupremotejobs_extractor import (
        fetch_startupremotejobs_jobs,
    )
    from app.service.extractors.startupremotejobs.startupremotejobs_data_ingestion_config import RESOURCES

    sig = inspect.signature(fetch_startupremotejobs_jobs)
    config = RESOURCES["startupremotejobs"]
    for target in config["targets"]:
        for key in target["params"]:
            if key == "dry_run":
                continue
            assert key in sig.parameters, (
                f"Config key '{key}' not found in fetch_startupremotejobs_jobs() "
                f"for query '{target['query']}'. "
                f"Available: {list(sig.parameters.keys())}"
            )


def test_ingestion_flow():
    from app.service.extractors.data_ingestion import run_ingestion
    from app.service.extractors.startupremotejobs.startupremotejobs_data_ingestion_config import RESOURCES

    config = RESOURCES["startupremotejobs"]
    for target in config["targets"]:
        target["params"]["dry_run"] = True
    run_ingestion(RESOURCES, ["startupremotejobs"])


if __name__ == "__main__":
    test_extractor_parses_dry_run()
    print("✓ extractor_parses_dry_run")

    test_to_job_dto_maps_fields()
    print("✓ to_job_dto_maps_fields")

    test_to_job_dto_handles_null_fields()
    print("✓ to_job_dto_handles_null_fields")

    test_to_job_dto_handles_company_as_string()
    print("✓ to_job_dto_handles_company_as_string")

    test_config_params_match_extractor_signature()
    print("✓ config_params_match_extractor_signature")

    print("\n--- Ejecutando ingestion dry-run ---")
    test_ingestion_flow()
    print("✓ ingestion_flow")
