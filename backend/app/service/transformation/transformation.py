"""
Transformation pipeline for unified_jobs collection.

Runs 3 steps sequentially:
  1. applicable_service  — determine if job is applicable for the candidate (LLM)
  2. technology_service   — extract technologies from applicable jobs (LLM)
  3. match_service        — calculate match score from technologies (deterministic)

Each step is idempotent: re-running skips already-processed documents.
"""

from app.service.transformation.applicable_service import process_applicable
from app.service.transformation.technology_service import process_technologies
from app.service.transformation.match_service import process_matches


def run_pipeline(batch_size: int = 50):
    print("=" * 50)
    print("Step 1/3: Applicable flag")
    print("=" * 50)
    a_ok, a_err = process_applicable(batch_size=batch_size)

    print()
    print("=" * 50)
    print("Step 2/3: Technology extraction")
    print("=" * 50)
    t_ok, t_err = process_technologies(batch_size=batch_size)

    print()
    print("=" * 50)
    print("Step 3/3: Match score")
    print("=" * 50)
    m_ok, m_err = process_matches(batch_size=batch_size)

    print()
    print("=" * 50)
    print("Pipeline complete")
    print(f"  Applicable:    {a_ok} ok, {a_err} errors")
    print(f"  Technologies:  {t_ok} ok, {t_err} errors")
    print(f"  Match:         {m_ok} ok, {m_err} errors")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()
