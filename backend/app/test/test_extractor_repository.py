import sys
import os
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

MOCK_CLIENT = patch("app.core.extractor_repository.MongoClient").start()
MOCK_UNIFIED_CLIENT = patch("app.core.data_unified_repository.MongoClient").start()


def _import_repo_module(env_vars: dict[str, str]):
    with patch.dict(os.environ, env_vars, clear=True):
        import importlib
        import app.core.extractor_repository as repo
        importlib.reload(repo)
        return repo


def test_mongo_uri_uses_mongodb_url_first():
    repo = _import_repo_module({
        "MONGODB_URL": "mongodb://user:pass@mongodb:27017/db?authSource=admin",
        "MONGO_URI": "mongodb://should-not-be-used:27017/db",
    })
    assert repo.MONGO_URI == "mongodb://user:pass@mongodb:27017/db?authSource=admin"


def test_mongo_uri_falls_back_to_mono_uri():
    repo = _import_repo_module({
        "MONGO_URI": "mongodb://fallback:27017/db",
    })
    assert repo.MONGO_URI == "mongodb://fallback:27017/db"


def test_mongo_uri_uses_default_when_no_env():
    repo = _import_repo_module({})
    assert "midzospa" in repo.MONGO_URI
    assert "localhost" in repo.MONGO_URI


def test_data_unified_repository_also_reads_mongodb_url():
    with patch.dict(os.environ, {
        "MONGODB_URL": "mongodb://user:pass@mongodb:27017/db?authSource=admin",
        "MONGO_URI": "mongodb://should-not-be-used:27017/db",
    }, clear=True):
        import importlib
        import app.core.data_unified_repository as repo
        importlib.reload(repo)
        assert "mongodb://user:pass@mongodb:27017/db?authSource=admin" in repo.MONGO_URI


def test_both_repositories_use_same_mongo_uri_when_mongodb_url_set():
    with patch.dict(os.environ, {
        "MONGODB_URL": "mongodb://common-service:27017/db",
    }, clear=True):
        import importlib
        import app.core.extractor_repository as extractor_repo
        import app.core.data_unified_repository as unified_repo
        importlib.reload(extractor_repo)
        importlib.reload(unified_repo)
        assert extractor_repo.MONGO_URI == unified_repo.MONGO_URI
        assert "common-service" in extractor_repo.MONGO_URI


def test_store_results_handles_empty_list():
    from app.core.extractor_repository import store_results
    store_results([], "ActiveJobsDB", "test query")


if __name__ == "__main__":
    test_mongo_uri_uses_mongodb_url_first()
    print("✓ mongo_uri_uses_mongodb_url_first")

    test_mongo_uri_falls_back_to_mono_uri()
    print("✓ mongo_uri_falls_back_to_mono_uri")

    test_mongo_uri_uses_default_when_no_env()
    print("✓ mongo_uri_uses_default_when_no_env")

    test_data_unified_repository_also_reads_mongodb_url()
    print("✓ data_unified_repository_also_reads_mongodb_url")

    test_both_repositories_use_same_mongo_uri_when_mongodb_url_set()
    print("✓ both_repositories_use_same_mongo_uri_when_mongodb_url_set")

    test_store_results_handles_empty_list()
    print("✓ store_results_handles_empty_list")
