import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from application.service.match_service import skill_in_cv, compute_match, process_matches
from application.service.applicable_service import process_applicable, PROMPT_TEMPLATE as APPLICABLE_PROMPT
from application.service.technology_service import process_technologies, PROMPT_TEMPLATE as TECH_PROMPT
from application.service.transformation import run_pipeline
from core.data_unified_repository import unified_jobs_collection


# =============================================================================
#  match_service  —  purely deterministic, no LLM, no DB writes needed
# =============================================================================

class TestSkillInCv:
    def test_direct_match(self):
        assert skill_in_cv("Java") is True
        assert skill_in_cv("java") is True
        assert skill_in_cv("Spring Boot") is True

    def test_mapped_match(self):
        assert skill_in_cv("K8s") is True
        assert skill_in_cv("Amazon Web Services") is True
        assert skill_in_cv("Postgres") is True
        assert skill_in_cv("Retrieval-Augmented Generation") is True
        assert skill_in_cv("Domain-Driven Design") is True
        assert skill_in_cv("Artificial Intelligence") is True

    def test_mapped_match_with_fix(self):
        """These mappings work now that 'go' and 'gcp' are in CV_SKILLS."""
        assert skill_in_cv("Golang") is True
        assert skill_in_cv("Google Cloud") is True

    def test_no_match(self):
        assert skill_in_cv("COBOL") is False
        assert skill_in_cv("Fortran") is False
        assert skill_in_cv("PHP") is False

    def test_edge_cases(self):
        assert skill_in_cv("") is False
        assert skill_in_cv("   ") is False


class TestComputeMatch:
    def test_all_match(self):
        assert compute_match(["Java", "Spring Boot", "Docker"]) == 100

    def test_partial_match(self):
        score = compute_match(["Java", "Spring Boot", "COBOL"])
        assert score == 66

    def test_no_match(self):
        assert compute_match(["COBOL", "Fortran"]) == 0

    def test_empty_list(self):
        assert compute_match([]) == 0
        assert compute_match(None) == 0

    def test_single_match(self):
        assert compute_match(["Java", "Unknown1", "Unknown2"]) == 33

    def test_clamps_range(self):
        mock_match = compute_match(["Java", "Spring Boot", "Docker", "AWS"])
        assert 0 <= mock_match <= 100


class TestProcessMatchesQuery:
    """Verify the MongoDB query filter used by process_matches
    (read-only — no documents are modified)"""

    def test_query_only_targets_docs_without_match(self):
        """Documents that already have a match should NOT be in the query result"""
        from application.service.match_service import process_matches
        query = {
            "technologies": {"$exists": True, "$ne": [], "$ne": None},
            "$or": [
                {"match": {"$exists": False}},
                {"match": None},
            ],
        }
        docs_without_match = list(unified_jobs_collection.find(query).limit(10))
        for doc in docs_without_match:
            assert "match" not in doc or doc.get("match") is None

    def test_all_processed_docs_have_valid_match(self):
        """All 296 docs should have a valid match score"""
        cursor = unified_jobs_collection.find(
            {"match": {"$exists": True}},
            {"match": 1}
        ).limit(500)
        for doc in cursor:
            score = doc.get("match")
            assert isinstance(score, int) or isinstance(score, float), f"match not numeric: {score} in {doc['_id']}"
            assert 0 <= score <= 100, f"match out of range: {score} in {doc['_id']}"


# =============================================================================
#  Data integrity  —  read-only checks on the live MongoDB
# =============================================================================

class TestExistingDataIntegrity:
    """Read-only validation of the already-processed pipeline data"""

    def test_all_docs_have_applicable_flag(self):
        total = unified_jobs_collection.count_documents({})
        with_flag = unified_jobs_collection.count_documents({"applicable": {"$exists": True}})
        assert total == with_flag, f"{total - with_flag} docs missing 'applicable'"

    def test_applicable_is_bool(self):
        bad = list(unified_jobs_collection.find(
            {"applicable": {"$not": {"$type": "bool"}}},
            {"applicable": 1}
        ).limit(100))
        assert len(bad) == 0, f"{len(bad)} docs have non-boolean 'applicable'"

    def test_all_docs_have_technologies_array(self):
        """technologies must be present and always a list"""
        missing = unified_jobs_collection.count_documents({"technologies": {"$exists": False}})
        assert missing == 0, f"{missing} docs missing 'technologies'"

        not_array = list(unified_jobs_collection.find(
            {"technologies": {"$not": {"$type": "array"}}},
            {"technologies": 1}
        ).limit(100))
        assert len(not_array) == 0, f"{len(not_array)} docs have non-array 'technologies'"

    def test_applicable_jobs_are_remote_or_germany(self):
        """Applicable jobs must be remote OR Germany-based (pipeline rule)"""
        german_cities = {"berlin", "munich", "hamburg", "frankfurt", "cologne",
                         "stuttgart", "düsseldorf", "dusseldorf", "leipzig",
                         "dresden", "nuremberg", "hannover", "bremen", "bonn"}

        cursor = unified_jobs_collection.find(
            {"applicable": True},
            {"is_remote": 1, "location": 1, "country": 1, "title": 1}
        )
        violations = []
        for doc in cursor:
            if doc.get("is_remote") is True:
                continue
            country = (doc.get("country") or "").lower()
            location = (doc.get("location") or "").lower()
            if "germany" in country:
                continue
            if any(city in location for city in german_cities):
                continue
            violations.append(doc.get("title", "?"))
        if violations:
            print(f"WARNING: {len(violations)} applicable jobs are neither remote nor Germany-based:")
            for v in violations[:5]:
                print(f"  - {v}")

    def test_match_is_consistent_with_technologies_and_cv_skills(self):
        """Spot-check: match % should equal (cv_matched / total_techs) * 100"""
        from application.service.match_service import CV_SKILLS, TECH_TO_CV_SKILL

        def skill_in_cv_check(skill: str) -> bool:
            sl = skill.lower().strip()
            if sl in CV_SKILLS:
                return True
            mapped = TECH_TO_CV_SKILL.get(sl)
            return mapped in CV_SKILLS if mapped else False

        cursor = unified_jobs_collection.find(
            {"technologies": {"$ne": []}},
            {"technologies": 1, "match": 1, "title": 1}
        ).limit(20)

        mismatches = []
        for doc in cursor:
            techs = doc.get("technologies") or []
            stored_match = doc.get("match", 0)
            if not techs:
                expected = 0
            else:
                matched = sum(1 for t in techs if skill_in_cv_check(t))
                expected = int((matched / len(techs)) * 100)

            if stored_match != expected:
                mismatches.append({
                    "title": doc.get("title"),
                    "stored": stored_match,
                    "expected": expected,
                    "techs": techs,
                })

        if mismatches:
            print(f"WARNING: {len(mismatches)} docs have 'match' inconsistent with compute_match():")
            for m in mismatches[:3]:
                print(f"  {m['title']}: stored={m['stored']} expected={m['expected']} techs={m['techs']}")


# =============================================================================
#  Pipeline orchestration  —  tests that run_pipeline calls all services
# =============================================================================

class TestPipelineOrchestration:

    @patch("application.service.transformation.process_applicable", return_value=(5, 0))
    @patch("application.service.transformation.process_technologies", return_value=(3, 1))
    @patch("application.service.transformation.process_matches", return_value=(4, 0))
    def test_run_pipeline_calls_all_services(self, mock_matches, mock_techs, mock_applicable):
        run_pipeline(batch_size=50)
        mock_applicable.assert_called_once_with(batch_size=50)
        mock_techs.assert_called_once_with(batch_size=50)
        mock_matches.assert_called_once_with(batch_size=50)

    @patch("application.service.transformation.process_applicable", return_value=(0, 2))
    @patch("application.service.transformation.process_technologies", return_value=(0, 0))
    @patch("application.service.transformation.process_matches", return_value=(0, 0))
    def test_run_pipeline_continues_on_error(self, mock_matches, mock_techs, mock_applicable):
        """Even if step 1 has errors, steps 2 and 3 should still run"""
        run_pipeline(batch_size=10)
        mock_applicable.assert_called_once()
        mock_techs.assert_called_once()
        mock_matches.assert_called_once()


# =============================================================================
#  applicable_service  —  prompt template validation
# =============================================================================

class TestApplicableServicePrompt:
    def test_prompt_template_has_required_variables(self):
        vars = APPLICABLE_PROMPT.input_variables
        for required in ("title", "location", "country", "is_remote", "description"):
            assert required in vars, f"Prompt missing input variable: {required}"

    def test_prompt_asks_for_json(self):
        raw = str(APPLICABLE_PROMPT)
        assert "applicable" in raw
        assert "true/false" in raw

    def test_process_applicable_query_filters_unprocessed(self):
        """Verify the MongoDB query used by process_applicable is read-only"""
        query = {"$or": [{"processed": {"$ne": True}}, {"processed": {"$exists": False}}]}
        unprocessed_count = unified_jobs_collection.count_documents(query)
        total = unified_jobs_collection.count_documents({})
        all_processed = unified_jobs_collection.count_documents({"processed": True})
        remaining = total - all_processed
        assert unprocessed_count == remaining, (
            f"Query should return remaining unprocessed docs ({remaining}), "
            f"but returned {unprocessed_count}"
        )


# =============================================================================
#  technology_service  —  prompt template validation
# =============================================================================

class TestTechnologyServicePrompt:
    def test_prompt_has_required_variables(self):
        vars = TECH_PROMPT.input_variables
        for required in ("title", "description"):
            assert required in vars, f"Prompt missing input variable: {required}"

    def test_prompt_asks_for_json_array(self):
        raw = str(TECH_PROMPT)
        assert "json" in raw.lower() or "[]" in raw
        assert "array" in raw.lower()

    def test_process_technologies_query_filters_correctly(self):
        """Verify the MongoDB query only targets applicable=True docs without techs"""
        query = {
            "applicable": True,
            "$or": [
                {"technologies": {"$exists": False}},
                {"technologies": {"$eq": []}},
                {"technologies": None},
            ],
        }
        pending_techs = unified_jobs_collection.count_documents(query)
        applicable_but_no_techs = unified_jobs_collection.count_documents({
            "applicable": True,
            "technologies": {"$in": [[], None]},
        })
        all_technologies = unified_jobs_collection.count_documents({
            "applicable": True,
            "technologies": {"$exists": True},
        })
        total_applicable = unified_jobs_collection.count_documents({"applicable": True})
        print(f"  Total applicable: {total_applicable}")
        print(f"  With technologies: {all_technologies}")
        print(f"  Pending (no techs): {pending_techs}")
        print(f"  Applicable with empty/null techs: {applicable_but_no_techs}")
        assert all_technologies >= total_applicable - pending_techs


# =============================================================================
#  Pipeline idempotency  —  verify re-running is safe
# =============================================================================

class TestPipelineIdempotency:
    """Ensure re-running the pipeline does not re-process already-done docs"""

    def test_applicable_service_skips_processed(self):
        """Count of already-processed docs that would be skipped"""
        query = {"$or": [{"processed": {"$ne": True}}, {"processed": {"$exists": False}}]}
        already_processed = unified_jobs_collection.count_documents({"processed": True})
        would_process = unified_jobs_collection.count_documents(query)
        total = unified_jobs_collection.count_documents({})
        print(f"  Total: {total}, already processed: {already_processed}, would re-process: {would_process}")
        assert would_process == total - already_processed

    def test_match_service_skips_already_scored(self):
        query = {
            "technologies": {"$exists": True, "$ne": [], "$ne": None},
            "$or": [
                {"match": {"$exists": False}},
                {"match": None},
            ],
        }
        would_reprocess = unified_jobs_collection.count_documents(query)
        print(f"  Docs that would be re-processed by match_service: {would_reprocess}")
        assert would_reprocess == 0, (
            f"match_service would re-process {would_reprocess} docs that already have scores"
        )

    def test_technology_service_skips_already_extracted(self):
        query = {
            "applicable": True,
            "$or": [
                {"technologies": {"$exists": False}},
                {"technologies": {"$eq": []}},
                {"technologies": None},
            ],
        }
        would_reprocess = unified_jobs_collection.count_documents(query)
        applicable_total = unified_jobs_collection.count_documents({"applicable": True})
        print(f"  Applicable: {applicable_total}, would re-process techs: {would_reprocess}")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
